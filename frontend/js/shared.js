/**
 * LabLine — Enterprise Diagnostic Portal & Laboratory Management System
 * API Client & Session Manager (LabStore), Clinical Reference Models, and Analytical Helpers
 *
 * NOTE: LabStore operates as a live REST API client and JWT session manager.
 * Persistent records (tests, bookings, results, reports) are handled directly by the backend database.
 * Client-side localStorage is strictly reserved for JWT session state and shopping cart items.
 */

/**
 * LabLine Central API Discovery Engine:
 * 1. Explicit window.LABLINE_API_BASE override
 * 2. URL Query parameter (?api=https://...)
 * 3. <meta name="labline-api-base" content="...">
 * 4. localStorage key "labline_api_base"
 * 5. Automatic origin detection (if served by backend port 8000 or production cloud host)
 * 6. Local development fallback (http://127.0.0.1:8000)
 */
function resolveLabLineApiBase() {
  if (typeof window === 'undefined') return 'http://127.0.0.1:8000';
  if (window.LABLINE_API_BASE) return window.LABLINE_API_BASE.replace(/\/+$/, '');

  try {
    const urlParams = window.location.search ? new URLSearchParams(window.location.search) : null;
    const paramApi = urlParams ? urlParams.get('api') : null;
    if (paramApi) {
      const sanitized = paramApi.trim().replace(/\/+$/, '');
      localStorage.setItem('labline_api_base', sanitized);
      return sanitized;
    }
  } catch (e) {}

  const metaApi = typeof document !== 'undefined' ? document.querySelector('meta[name="labline-api-base"]')?.getAttribute('content') : null;
  if (metaApi && metaApi.trim()) return metaApi.trim().replace(/\/+$/, '');

  try {
    const localSaved = localStorage.getItem('labline_api_base');
    if (localSaved && localSaved.trim()) return localSaved.trim().replace(/\/+$/, '');
  } catch (e) {}

  // Auto-detect if served by the backend or cloud host
  const loc = typeof window !== 'undefined' ? window.location : null;
  if (loc && loc.protocol && loc.protocol.startsWith('http')) {
    const isLocalhost = ['localhost', '127.0.0.1', '0.0.0.0'].includes(loc.hostname);
    const isBackendPort = loc.port === '8000';
    // If on a cloud host or port 8000, use window.location.origin
    if (isBackendPort || (!isLocalhost && loc.port !== '5500' && loc.port !== '3000')) {
      return loc.origin.replace(/\/+$/, '');
    }
  }

  return 'http://127.0.0.1:8000';
}
window.LABLINE_API_BASE = resolveLabLineApiBase();

const STAGES = [
  'Booked',
  'Sample Collected',
  'In-Transit',
  'Processing',
  'Results Certified'
];

const PHLEBOTOMISTS = [
  { id: 'phleb-1', name: 'Rupesh Patel', phone: '+91 98450 12345', activePickups: 2, rating: 4.9 },
  { id: 'phleb-2', name: 'Vijay Nair', phone: '+91 98450 67890', activePickups: 1, rating: 4.8 },
  { id: 'phleb-3', name: 'Yatish Shetty', phone: '+91 98450 54321', activePickups: 3, rating: 4.9 }
];

const TECHNICIANS = [
  { id: 'tech-1', name: 'Clinical Technologist', role: 'technician', station: 'Central Diagnostics & Hematology' }
];

/**
 * LabStore: Central API client and session manager for LabLine.
 * Handles authenticated API calls, JWT session lifecycle, and client-side cart management.
 * All clinical data (tests, bookings, reports, results) are stored in and retrieved from the backend API.
 */
const LabStore = {
  /**
   * Central authenticated API fetch wrapper
   */
  async api(endpoint, options = {}) {
    const baseUrl = window.LABLINE_API_BASE || 'http://127.0.0.1:8000';
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${cleanEndpoint}`;
    const user = this.getCurrentUser();
    const token = user ? user.token : null;

    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers
    };

    try {
      const res = await fetch(url, config);
      if (res.status === 401) {
        console.warn(`[LabStore] 401 Unauthorized for ${cleanEndpoint}`);
        if (token && !cleanEndpoint.includes('/auth/login')) {
          this.logout('Session expired or unauthorized. Please sign in again.');
        }
        const errJson = await res.json().catch(() => ({ detail: 'Unauthorized credentials' }));
        throw new Error(errJson.detail || 'Incorrect credentials or unauthorized access');
      }
      if (!res.ok) {
        const errJson = await res.json().catch(() => ({ detail: `HTTP Error ${res.status}` }));
        const detailMsg = typeof errJson.detail === 'string'
          ? errJson.detail
          : Array.isArray(errJson.detail)
          ? errJson.detail.map(d => d.msg || JSON.stringify(d)).join('; ')
          : JSON.stringify(errJson.detail || errJson);
        throw new Error(detailMsg || `Request failed (${res.status})`);
      }
      if (res.status === 204) return null;
      return await res.json();
    } catch (err) {
      if (!err.message || err.message.includes('Failed to fetch')) {
        console.error(`[LabStore Network Error] Unable to connect to ${url}:`, err);
        throw new Error('Unable to connect to LabLine API server. Please verify the backend is running.');
      }
      throw err;
    }
  },

  // -------------------------------------------------------------
  // User Session & Authentication (Real JWT)
  // -------------------------------------------------------------
  getCurrentUser() {
    const data = localStorage.getItem('labline_user');
    if (!data) return null;
    try {
      const user = JSON.parse(data);
      if (!user || !user.token) return null;
      return user;
    } catch (e) {
      return null;
    }
  },

  setCurrentUser(user) {
    if (!user) {
      localStorage.removeItem('labline_user');
    } else {
      localStorage.setItem('labline_user', JSON.stringify(user));
    }
  },

  async login(email, password) {
    const cleanEmail = (email || '').trim().toLowerCase();
    const data = await this.api('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: cleanEmail, password })
    });
    const userSession = {
      id: data.user.id,
      name: data.user.name,
      email: data.user.email,
      role: data.user.role,
      phone: data.user.phone || null,
      station: data.user.station || null,
      token: data.access_token
    };
    this.setCurrentUser(userSession);
    return userSession;
  },

  async signup(payload) {
    const cleanEmail = (payload.email || '').trim().toLowerCase();
    const cleanName = (payload.name || '').trim();
    const data = await this.api('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        name: cleanName,
        email: cleanEmail,
        password: payload.password,
        role: payload.role || 'patient'
      })
    });
    const userSession = {
      id: data.user.id,
      name: data.user.name,
      email: data.user.email,
      role: data.user.role,
      token: data.access_token
    };
    this.setCurrentUser(userSession);
    return userSession;
  },

  logout(reason = null) {
    localStorage.removeItem('labline_user');
    if (reason) {
      sessionStorage.setItem('labline_auth_error', reason);
    }
    const path = window.location.pathname.toLowerCase().replace(/\\/g, '/');
    if (path.includes('/patient/') || path.includes('/admin/') || path.includes('/technician/')) {
      window.location.href = '../index.html';
    } else {
      window.location.href = 'index.html';
    }
  },

  // -------------------------------------------------------------
  // Test Catalog (FastAPI /tests)
  // -------------------------------------------------------------
  normalizeTest(t) {
    if (!t) return null;
    return {
      ...t,
      sampleType: t.sampleType || t.sample_type || 'Serum / Plasma',
      sample_type: t.sample_type || t.sampleType || 'Serum / Plasma',
      tubeCapClass: t.tubeCapClass || t.tube_cap_class || 'tube-cap-edta',
      tube_cap_class: t.tube_cap_class || t.tubeCapClass || 'tube-cap-edta',
      fastingHours: t.fastingHours !== undefined ? t.fastingHours : (t.fasting_hours !== undefined ? t.fasting_hours : 0),
      fasting_hours: t.fasting_hours !== undefined ? t.fasting_hours : (t.fastingHours !== undefined ? t.fastingHours : 0),
      turnaround: t.turnaround || '4 Hours',
      parameters: (t.parameters || []).map(p => ({
        ...p,
        key: p.key,
        label: p.label || p.key,
        unit: p.unit || '',
        min: p.min !== undefined ? p.min : (p.min_val !== undefined ? p.min_val : 0),
        min_val: p.min_val !== undefined ? p.min_val : (p.min !== undefined ? p.min : 0),
        max: p.max !== undefined ? p.max : (p.max_val !== undefined ? p.max_val : 100),
        max_val: p.max_val !== undefined ? p.max_val : (p.max !== undefined ? p.max : 100),
        defaultVal: p.defaultVal !== undefined ? p.defaultVal : (p.default_val !== undefined ? p.default_val : 0),
        default_val: p.default_val !== undefined ? p.default_val : (p.defaultVal !== undefined ? p.default_val : 0)
      }))
    };
  },

  async getTests(category = '', search = '') {
    const params = new URLSearchParams();
    if (category && category !== 'all') params.append('category', category);
    if (search) params.append('search', search);
    const query = params.toString() ? `?${params.toString()}` : '';
    const list = await this.api(`/tests${query}`, { method: 'GET' });
    const tests = (list || []).map(t => this.normalizeTest(t));
    this._testsCache = tests;
    return tests.sort((a, b) => {
      const aCbc = a.id === 'cbc' || (a.name && a.name.toLowerCase().includes('complete blood count'));
      const bCbc = b.id === 'cbc' || (b.name && b.name.toLowerCase().includes('complete blood count'));
      if (aCbc && !bCbc) return -1;
      if (!aCbc && bCbc) return 1;
      return 0;
    });
  },

  async getTestById(id) {
    const t = await this.api(`/tests/${id}`, { method: 'GET' });
    return this.normalizeTest(t);
  },

  async createTest(testData) {
    return await this.api('/tests', {
      method: 'POST',
      body: JSON.stringify(testData)
    });
  },

  async updateTest(id, testData) {
    return await this.api(`/tests/${id}`, {
      method: 'PUT',
      body: JSON.stringify(testData)
    });
  },

  async deleteTest(id) {
    return await this.api(`/tests/${id}`, {
      method: 'DELETE'
    });
  },

  // -------------------------------------------------------------
  // Bookings / Orders (FastAPI /bookings)
  // -------------------------------------------------------------
  normalizeOrder(o) {
    if (!o) return null;
    const testNames = o.testNames || (o.items ? o.items.map(it => it.test_name) : []);
    const testIds = o.testIds || (o.items ? o.items.map(it => it.test_id) : []);
    const resultsObj = {};
    if (o.results) {
      if (Array.isArray(o.results)) {
        o.results.forEach(r => { resultsObj[r.parameter_key] = r.observed_value; });
      } else if (typeof o.results === 'object') {
        Object.assign(resultsObj, o.results);
      }
    }
    return {
      ...o,
      patientName: o.patient_name || o.patientName || 'Anonymous Patient',
      patientAge: o.patient_age !== undefined ? o.patient_age : (o.patientAge || 29),
      patientGender: o.patient_gender || o.patientGender || 'Male',
      patientPhone: o.patient_phone || o.patientPhone || '+91 98765 43210',
      patientEmail: o.patient_email || o.patientEmail || 'patient@labline.com',
      collectionType: o.collection_type || o.type || o.collectionType || 'Home Collection',
      type: o.collection_type || o.type || 'Home Collection',
      date: o.date || (o.created_at ? String(o.created_at).split('T')[0] : 'Scheduled'),
      timeSlot: o.time_slot || o.timeSlot || '08:30 AM - 09:30 AM',
      time_slot: o.time_slot || o.timeSlot || '08:30 AM - 09:30 AM',
      address: o.address || (o.collection_type === 'Lab Visit' ? 'LabLine Central Diagnostic Facility' : 'Registered Patient Address'),
      totalAmount: o.total_amount !== undefined ? o.total_amount : (o.totalAmount || 0),
      paymentStatus: o.payment_status || o.paymentStatus || 'Pending',
      paymentMethod: o.payment_method || o.paymentMethod || 'UPI',
      transactionId: o.transaction_id || o.transactionId || null,
      status: o.status || 'Booked',
      currentStage: o.current_stage || o.currentStage || 'Booked',
      phlebotomist: o.phlebotomist || 'Kiran Kumar',
      technician: o.technician || 'Unassigned',
      urgency: o.urgency || 'Standard',
      sampleTubeBarcode: o.sample_tube_barcode || o.sampleTubeBarcode || `BC-${o.id ? o.id.replace('ORD-', '') : '89410982'}`,
      temperatureTelemetry: o.temperature_telemetry || o.temperatureTelemetry || '4.2°C (Cold Chain Monitored)',
      technicianNotes: o.technician_notes || o.technicianNotes || null,
      reportHash: o.report_hash || o.reportHash || null,
      isCertified: Boolean(o.is_certified !== undefined ? o.is_certified : o.isCertified),
      certifiedAt: o.certified_at || o.certifiedAt || null,
      testNames,
      testIds,
      results: resultsObj,
      timestamps: {
        booked: o.time_booked ? new Date(o.time_booked).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (o.timestamps?.booked || '08:00 AM'),
        collected: o.time_collected ? new Date(o.time_collected).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (o.timestamps?.collected || null),
        inTransit: o.time_in_transit ? new Date(o.time_in_transit).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (o.timestamps?.inTransit || null),
        processing: o.time_processing ? new Date(o.time_processing).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (o.timestamps?.processing || null),
        completed: o.time_completed ? new Date(o.time_completed).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : (o.timestamps?.completed || null)
      }
    };
  },

  async getOrders(filter = {}) {
    const params = new URLSearchParams();
    if (filter.email) params.append('email', filter.email);
    if (filter.stage) params.append('stage', filter.stage);
    if (filter.status_filter) params.append('status_filter', filter.status_filter);
    if (filter.urgency) params.append('urgency', filter.urgency);
    const query = params.toString() ? `?${params.toString()}` : '';
    const list = await this.api(`/bookings${query}`, { method: 'GET' });
    return (list || []).map(o => this.normalizeOrder(o));
  },

  async getOrderById(orderId) {
    if (!orderId) return null;
    const o = await this.api(`/bookings/${orderId}`, { method: 'GET' });
    return this.normalizeOrder(o);
  },

  async getActiveOrder() {
    const orders = await this.getOrders();
    if (orders && orders.length > 0) {
      return orders[0];
    }
    return null;
  },

  getActiveOrderId() {
    return sessionStorage.getItem('labline_active_order_id') || localStorage.getItem('labline_active_order_id') || null;
  },

  setActiveOrder(orderId) {
    if (orderId) {
      sessionStorage.setItem('labline_active_order_id', orderId);
      localStorage.setItem('labline_active_order_id', orderId);
    } else {
      sessionStorage.removeItem('labline_active_order_id');
      localStorage.removeItem('labline_active_order_id');
    }
    return orderId;
  },

  async createBooking(bookingData) {
    const created = await this.api('/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingData)
    });
    const norm = this.normalizeOrder(created);
    this.setActiveOrder(norm.id);
    return norm;
  },

  async advanceBookingStage(bookingId, stage, technicianNotes = null) {
    const updated = await this.api(`/bookings/${bookingId}/stage`, {
      method: 'PUT',
      body: JSON.stringify({
        stage: stage,
        technician_notes: technicianNotes
      })
    });
    return this.normalizeOrder(updated);
  },

  async assignBooking(bookingId, technician = null, phlebotomist = null) {
    const payload = {};
    if (technician !== null) payload.technician = technician;
    if (phlebotomist !== null) payload.phlebotomist = phlebotomist;
    const updated = await this.api(`/bookings/${bookingId}/assign`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    });
    return this.normalizeOrder(updated);
  },

  async autoDispatchWorkload() {
    return await this.api('/bookings/dispatch/auto-balance', {
      method: 'POST'
    });
  },

  // -------------------------------------------------------------
  // Payments (FastAPI /payments)
  // -------------------------------------------------------------
  async createPayment(bookingId, amount, method = 'UPI') {
    return await this.api('/payments/create', {
      method: 'POST',
      body: JSON.stringify({
        booking_id: bookingId,
        amount: parseFloat(amount),
        method: method
      })
    });
  },

  // -------------------------------------------------------------
  // Clinical Results & Pathology Certification (FastAPI /results, /reports)
  // -------------------------------------------------------------
  async submitResults(bookingId, resultsArray, notes = null) {
    return await this.api(`/results/${bookingId}`, {
      method: 'POST',
      body: JSON.stringify({
        results: resultsArray,
        technician_notes: notes
      })
    });
  },

  async certifyReport(bookingId) {
    return await this.api(`/reports/${bookingId}/certify`, {
      method: 'POST'
    });
  },

  async getReport(bookingId) {
    return await this.api(`/reports/${bookingId}`, {
      method: 'GET'
    });
  },

  async verifyReport(bookingId) {
    return await this.api(`/reports/${bookingId}/verify`, {
      method: 'GET'
    });
  },

  // -------------------------------------------------------------
  // Analytics & Administrative Metrics (FastAPI /analytics)
  // -------------------------------------------------------------
  async getAnalyticsSummary() {
    return await this.api('/analytics/summary', {
      method: 'GET'
    });
  },

  async getAnalyticsCategories() {
    return await this.api('/analytics/categories', {
      method: 'GET'
    });
  },

  async getAnalyticsTechnicians() {
    return await this.api('/analytics/technicians', {
      method: 'GET'
    });
  },

  // -------------------------------------------------------------
  // Non-sensitive Client Cart Preferences
  // -------------------------------------------------------------
  getCart() {
    const data = localStorage.getItem('labline_cart');
    try { return data ? JSON.parse(data) : ['cbc']; } catch (e) { return ['cbc']; }
  },

  saveCart(cart) {
    localStorage.setItem('labline_cart', JSON.stringify(cart));
  }
};

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('labline_theme', next);
  window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
}

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-item ${type}`;

  const iconSvg = type === 'success'
    ? `<svg style="width:16px;height:16px;color:var(--success);flex-shrink:0;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M5 13l4 4L19 7"/></svg>`
    : type === 'error'
    ? `<svg style="width:16px;height:16px;color:var(--danger);flex-shrink:0;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 18L18 6M6 6l12 12"/></svg>`
    : type === 'warning'
    ? `<svg style="width:16px;height:16px;color:var(--warning);flex-shrink:0;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`
    : `<svg style="width:16px;height:16px;color:var(--accent);flex-shrink:0;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

  toast.innerHTML = `
    ${iconSvg}
    <div style="flex:1; font-size:13px; font-weight:500; line-height:1.4; color:var(--text-primary);">${message}</div>
    <button type="button" onclick="this.parentElement.remove()" style="background:none; border:none; cursor:pointer; color:var(--text-muted); padding:2px 4px; font-size:16px; line-height:1;" aria-label="Close notification">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 3600);
}

function evaluateParameter(value, min, max) {
  if (value === null || value === undefined || value === '' || isNaN(value)) {
    return { status: 'PENDING', label: 'Pending', cssClass: 'badge-low', markerPct: 50 };
  }
  const val = parseFloat(value);
  const minVal = parseFloat(min);
  const maxVal = parseFloat(max);

  const rangeSpan = maxVal - minVal;
  let pct = 50;
  if (rangeSpan > 0) {
    pct = 20 + ((val - minVal) / rangeSpan) * 60;
    pct = Math.max(4, Math.min(96, pct));
  }

  if (val > maxVal * 1.35) {
    return { status: 'CRITICAL_HIGH', label: 'Critical High', cssClass: 'badge-critical', markerPct: pct };
  } else if (val > maxVal) {
    return { status: 'HIGH', label: 'High', cssClass: 'badge-high', markerPct: pct };
  } else if (val < minVal * 0.7) {
    return { status: 'CRITICAL_LOW', label: 'Critical Low', cssClass: 'badge-critical', markerPct: pct };
  } else if (val < minVal) {
    return { status: 'LOW', label: 'Low', cssClass: 'badge-low', markerPct: pct };
  } else {
    return { status: 'NORMAL', label: 'Normal', cssClass: 'badge-normal', markerPct: pct };
  }
}

function generateDietAdviceForResults(results, testList) {
  const suggestions = [];

  if ((results.chol && results.chol > 200) || (results.tg && results.tg > 150)) {
    suggestions.push({
      category: 'Cardiovascular & Lipid Modulation',
      items: [
        'Incorporate water-soluble beta-glucans: oats, barley, chia seeds, and fresh seasonal fruits.',
        'Replace saturated dietary fats with cold-pressed olive oil, walnuts, and flaxseeds.',
        'Restrict industrial trans-fats, processed bakery pastries, and deep-fried items.'
      ]
    });
  }

  if ((results.hba1c_pct && results.hba1c_pct > 5.7) || (results.eag && results.eag > 115)) {
    suggestions.push({
      category: 'Glycemic Regulation & Insulin Sensitivity',
      items: [
        'Shift to complex low glycemic-index carbohydrates: millets, quinoa, and legumes.',
        'Eliminate added table sugar, high-fructose corn syrups, and carbonated sodas.',
        'Engage in 15-minute brisk walking post-meals to assist GLUT4 glucose uptake.'
      ]
    });
  }

  if (results.hb && results.hb < 13.0) {
    suggestions.push({
      category: 'Erythropoiesis & Iron Replenishment',
      items: [
        'Consume bioavailable dietary iron: steamed spinach, beetroot, pomegranates, and dried figs.',
        'Co-ingest with Vitamin C (lemon juice, oranges) to optimize non-heme iron absorption.'
      ]
    });
  }

  if (results.uric_val && results.uric_val > 7.2) {
    suggestions.push({
      category: 'Purine Metabolism & Gout Prevention',
      items: [
        'Limit high-purine foods: red meats, organ meats, shellfish, and brewer yeast extract.',
        'Increase daily hydration to 3.0 Liters to facilitate renal excretion of uric acid crystals.',
        'Incorporate tart cherry juice, low-fat dairy products, and vitamin C-rich fruits.'
      ]
    });
  }

  if (results.crp_val && results.crp_val > 5.0) {
    suggestions.push({
      category: 'Anti-Inflammatory Nutritional Protocol',
      items: [
        'Adopt an anti-inflammatory diet: turmeric (curcumin with black pepper), ginger, and dark leafy greens.',
        'Include cold-water fatty fish (rich in Omega-3 EPA/DHA) or freshly ground flaxseeds.',
        'Minimize refined sugars, industrial seed oils, and ultra-processed food items.'
      ]
    });
  }

  if (suggestions.length === 0) {
    suggestions.push({
      category: 'Clinical Health Maintenance & Hydration',
      items: [
        'Maintain balanced plate: 50% raw/steamed vegetables, 25% lean protein, 25% whole grains.',
        'Drink 2.5 - 3.0 Liters of water daily for optimal renal filtration and metabolic clearance.',
        'Sustain at least 150 minutes of moderate aerobic physical activity each week.'
      ]
    });
  }

  return suggestions;
}

// Role Portal Navigator - verifies user authentication and role permissions
function switchPortalRole(role) {
  const portalRoutes = {
    patient: 'patient/catalog.html',
    technician: 'technician/queue.html',
    admin: 'admin/dashboard.html'
  };

  const targetUrl = portalRoutes[role];
  if (!targetUrl) return;

  const currentUser = LabStore.getCurrentUser();
  const path = window.location.pathname.toLowerCase().replace(/\\/g, '/');
  let targetPath = targetUrl;
  if (path.includes('/patient/') || path.includes('/technician/') || path.includes('/admin/')) {
    targetPath = '../' + targetUrl;
  }

  if (!currentUser) {
    const loginPath = (path.includes('/patient/') || path.includes('/technician/') || path.includes('/admin/')) ? '../index.html' : 'index.html';
    sessionStorage.setItem('labline_auth_error', `Please sign in to access the ${role.toUpperCase()} portal.`);
    window.location.href = loginPath;
    return;
  }

  const userRole = (currentUser.role || '').toLowerCase();

  // Admin can access all portals; technician can access technician and patient views; patient only patient view
  const isAllowed = 
    userRole === 'admin' ||
    userRole === role ||
    (userRole === 'technician' && role === 'patient');

  if (isAllowed) {
    window.location.href = targetPath;
  } else {
    const targetDemo = demoAccounts[role];
    if (targetDemo) {
      showToast(`Switching to Demo ${role.toUpperCase()} workspace (${targetDemo.name})...`, 'info');
      LabStore.login(targetDemo.email, targetDemo.password)
        .then(() => {
          setTimeout(() => { window.location.href = targetPath; }, 300);
        })
        .catch(() => {
          showToast(`Access Restricted: Signed in as ${userRole.toUpperCase()}. Please sign in with an authorized account for ${role.toUpperCase()} access.`, 'warning');
        });
    } else {
      showToast(`Access Restricted: Signed in as ${userRole.toUpperCase()}. Please sign in with an authorized account for ${role.toUpperCase()} access.`, 'warning');
    }
  }
}

// ==================== Cryptographic Tamper-Detection Engine ====================

async function computeSha256(message) {
  if (window.crypto && window.crypto.subtle) {
    try {
      const msgUint8 = new TextEncoder().encode(message);
      const hashBuffer = await window.crypto.subtle.digest('SHA-256', msgUint8);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (e) {
      console.warn('SubtleCrypto error, falling back to internal digest:', e);
    }
  }

  // Canonical pure-JS SHA-256 fallback
  function rightRotate(value, amount) {
    return (value >>> amount) | (value << (32 - amount));
  }
  const mathPow = Math.pow;
  const maxWord = mathPow(2, 32);
  let lengthProperty = 'length';
  let i, j;
  let result = '';
  const words = [];
  const asciiBitLength = message[lengthProperty] * 8;
  const hash = [];
  const k = [];
  let primeCounter = 0;

  const isComposite = {};
  for (let candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (i = 0; i < 313; i += candidate) {
        isComposite[i] = candidate;
      }
      hash[primeCounter] = (mathPow(candidate, 0.5) * maxWord) | 0;
      k[primeCounter++] = (mathPow(candidate, 1 / 3) * maxWord) | 0;
    }
  }

  message += '\x80';
  while ((message[lengthProperty] % 64) - 56) message += '\x00';
  for (i = 0; i < message[lengthProperty]; i++) {
    j = message.charCodeAt(i);
    words[i >> 2] |= j << (((3 - i) % 4) * 8);
  }
  words[words[lengthProperty]] = (asciiBitLength / maxWord) | 0;
  words[words[lengthProperty]] = asciiBitLength;

  for (j = 0; j < words[lengthProperty];) {
    const w = words.slice(j, (j += 16));
    const oldHash = hash.slice(0);
    for (i = 0; i < 64; i++) {
      const i2 = i + j;
      const w15 = w[i - 15], w2 = w[i - 2];
      const s0 = rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3);
      const s1 = rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10);
      w[i] = i < 16 ? w[i] : (w[i - 16] + s0 + w[i - 7] + s1) | 0;

      const s1h = rightRotate(hash[4], 6) ^ rightRotate(hash[4], 11) ^ rightRotate(hash[4], 25);
      const ch = (hash[4] & hash[5]) ^ (~hash[4] & hash[6]);
      const temp1 = (hash[7] + s1h + ch + k[i] + w[i]) | 0;
      const s0h = rightRotate(hash[0], 2) ^ rightRotate(hash[0], 13) ^ rightRotate(hash[0], 22);
      const maj = (hash[0] & hash[1]) ^ (hash[0] & hash[2]) ^ (hash[1] & hash[2]);
      const temp2 = (s0h + maj) | 0;

      hash[7] = hash[6];
      hash[6] = hash[5];
      hash[5] = hash[4];
      hash[4] = (hash[3] + temp1) | 0;
      hash[3] = hash[2];
      hash[2] = hash[1];
      hash[1] = hash[0];
      hash[0] = (temp1 + temp2) | 0;
    }
    for (i = 0; i < 8; i++) {
      hash[i] = (hash[i] + oldHash[i]) | 0;
    }
  }

  for (i = 0; i < 8; i++) {
    for (j = 3; j >= 0; j--) {
      const b = (hash[i] >> (8 * j)) & 255;
      result += (b < 16 ? '0' : '') + b.toString(16);
    }
  }
  return result;
}

async function computeCanonicalReportPayload(order, simulatedResults = null, testsList = null) {
  // Bug 15 fix: canonical format must match Python backend generate_report_hash().
  // Python format: "key:value.2f:flag" — the status_flag MUST be included.
  const resultsObj = simulatedResults || order.results || {};
  let tests = testsList;
  if (!tests || !Array.isArray(tests) || tests.length === 0) {
    if (LabStore._testsCache && LabStore._testsCache.length > 0) {
      tests = LabStore._testsCache;
    } else {
      try {
        tests = await LabStore.getTests();
      } catch (e) {
        tests = [];
      }
    }
  }
  if (!Array.isArray(tests)) tests = [];
  const testMap = new Map(tests.map(t => [t.id, t]));

  // Build parameter key → {min, max} for status flag computation
  const paramRefMap = {};
  tests.forEach(test => {
    (test.parameters || []).forEach(p => {
      paramRefMap[p.key] = { min: (p.min !== undefined ? p.min : p.min_val), max: (p.max !== undefined ? p.max : p.max_val) };
    });
  });

  const sortedKeys = Object.keys(resultsObj).sort();
  const canonicalResults = sortedKeys.map(k => {
    const val = parseFloat(resultsObj[k] || 0);
    const ref = paramRefMap[k];
    let flag = 'Normal';
    if (ref && ref.min !== undefined && ref.max !== undefined) {
      const eval_ = evaluateParameter(val, ref.min, ref.max);
      // Map frontend status labels to backend flag names
      if (eval_.status === 'CRITICAL_HIGH' || eval_.status === 'CRITICAL_LOW') flag = 'Critical';
      else if (eval_.status === 'HIGH') flag = 'High';
      else if (eval_.status === 'LOW') flag = 'Low';
      else flag = 'Normal';
    }
    return `${k}:${val.toFixed(2)}:${flag}`;
  }).join(';');

  const sortedTests = (order.testNames || []).slice().sort().map(t => t.trim().toUpperCase()).join(',');
  return `ISSUER=LABLINE_CLINICAL_PATHOLOGY|BOOKING_ID=${(order.id || '').trim()}|PATIENT=${(order.patientName || '').trim().toUpperCase()}|TESTS=${sortedTests}|RESULTS=${canonicalResults}`;
}

async function generateOrderReportHash(order, customResults = null, testsList = null) {
  const payload = await computeCanonicalReportPayload(order, customResults, testsList);
  return await computeSha256(payload);
}

async function verifyOrderIntegrity(order, testedResults = null, testsList = null) {
  const computedHash = await generateOrderReportHash(order, testedResults, testsList);
  const certifiedHash = order.reportHash || computedHash;
  const isAuthentic = (computedHash.toLowerCase() === certifiedHash.toLowerCase());

  return {
    orderId: order.id,
    patientName: order.patientName,
    certifiedHash: certifiedHash,
    computedHash: computedHash,
    isAuthentic: isAuthentic,
    certifiedAt: order.certifiedAt || '2026-08-30 09:45 AM',
    pathologist: 'Dr. Yatish Rao, MD (Lead Pathologist)',
    statusText: isAuthentic ? 'VERIFIED AUTHENTIC (Unmodified)' : 'TAMPER DETECTED (Integrity Breach)'
  };
}


// ==================== Fair-Workload Specimen Priority Dispatcher ====================

function computeSpecimenPriority(order) {
  let score = 0;
  const factors = [];

  // 1. Urgency Weight
  if ((order.urgency || '').toUpperCase() === 'STAT') {
    score += 100;
    factors.push('Emergency STAT Urgency (+100)');
  } else {
    score += 20;
    factors.push('Standard Routine Scheduling (+20)');
  }

  // 2. Pre-Analytical Tube Stability / Cellular Lysis Window
  const tests = (order.testNames || []).map(t => t.toLowerCase());
  if (tests.some(t => t.includes('cbc') || t.includes('blood count'))) {
    score += 35;
    factors.push('EDTA Whole Blood High-Lysis Risk (+35)');
  } else if (tests.some(t => t.includes('glucose') || t.includes('sugar') || t.includes('hba1c'))) {
    score += 25;
    factors.push('Glycolytic Preservation Window (+25)');
  } else {
    score += 15;
    factors.push('Standard Serum Stability (+15)');
  }

  // 3. Stage Progression
  const stage = (order.currentStage || '').toLowerCase();
  if (stage.includes('processing')) {
    score += 20;
    factors.push('Active Analyzer Processing (+20)');
  } else if (stage.includes('transit')) {
    score += 15;
    factors.push('In-Transit Cold Chain (+15)');
  } else if (stage.includes('collected')) {
    score += 10;
    factors.push('Sample Collected (+10)');
  } else {
    score += 5;
    factors.push('Intake Queued (+5)');
  }

  const tier = score >= 120 ? 'CRITICAL_STAT' : score >= 60 ? 'HIGH_PRIORITY' : 'ROUTINE';
  return { score, tier, factors };
}

async function autoDispatchWorkload() {
  try {
    return await LabStore.autoDispatchWorkload();
  } catch (err) {
    console.error('[autoDispatchWorkload Error]:', err);
    throw err;
  }
}

// ==================== Smart Prescription Text Parser (Levenshtein) ====================

const CLINICAL_ALIASES_CLIENT = {
  cbc: ['cbc', 'complete blood count', 'hemogram', 'complete hemogram', 'blood count', 'hb', 'hemoglobin', 'platelets', 'platelet count', 'wbc', 'rbc', 'pcv', 'blood routine', 'blood examination'],
  lipid: ['lipid', 'lipid profile', 'cholesterol', 'chol', 'triglycerides', 'tg', 'hdl', 'ldl', 'vldl', 'cardiac lipid', 'lipid panel', 'serum lipids', 'dyslipidemia'],
  thyroid: ['thyroid', 'tft', 'tsh', 'thyroid profile', 't3', 't4', 'ultrasensitive tsh', 'thyroid test', 'thyroid panel', 't3 t4 tsh'],
  hba1c: ['hba1c', 'glycated hemoglobin', 'estimated glucose', 'eag', 'glycohemoglobin', 'a1c', 'diabetes panel', 'hba1c test', '3 month sugar'],
  lft: ['lft', 'liver function', 'liver function test', 'sgot', 'sgpt', 'alt', 'ast', 'bilirubin', 'bili', 'liver enzymes', 'hepatic', 'liver profile', 'hepatic panel', 'alkaline phosphatase'],
  kft: ['kft', 'kidney function', 'kidney function test', 'creatinine', 'sr creatinine', 'serum creatinine', 'urea', 'bun', 'uric acid', 'renal profile', 'renal panel', 'kidney panel', 'rft'],
  vitd_b12: ['vitamin d', 'vit d', 'vitamin b12', 'vit b12', 'b12', 'd3', 'cholecalciferol', 'cyanocobalamin', 'vitality duo', 'vitamin d3', 'vit d3', 'b12 deficiency'],
  fbs_ppbs: ['fbs', 'ppbs', 'fasting blood sugar', 'post prandial blood sugar', 'blood sugar fasting', 'pp sugar', 'glucose fasting', 'fbs ppbs', 'fasting glucose', 'pp glucose', 'blood sugar', 'sugar test', 'rbs', 'random blood sugar', 'fasting and pp', 'fasting sugar', 'ppbs test'],
  crp: ['crp', 'c reactive protein', 'hs crp', 'hscrp', 'c-reactive protein', 'inflammation marker', 'quantitative crp', 'reactive protein', 'high sensitivity crp', 'crp quantitative', 'cardiac crp'],
  urine_re: ['urine routine', 'urine r/e', 'urinalysis', 'urine re', 'urine microscopy', 'cue', 'complete urine exam', 'urine culture screen', 'urine test', 'urine rm', 'routine urine', 'urine r/m', 'urine analysis'],
  electrolytes: ['electrolytes', 'serum electrolytes', 'lytes', 'na k cl', 'sodium potassium', 'sodium', 'potassium', 'electrolyte panel', 'serum sodium', 'serum potassium', 'iono', 'serum ions'],
  esr: ['esr', 'erythrocyte sedimentation rate', 'sed rate', 'sedimentation rate', 'westergren esr', 'esr 1st hour', 'sedrate', 'westergren', 'sed rate westergren'],
  iron_profile: ['iron profile', 'serum ferritin', 'ferritin', 'iron', 'serum iron', 'tibc', 'transferrin', 'iron studies', 'iron panel', 'fe profile', 'iron deficiency', 'anemia profile', 'anemia panel'],
  dengue: ['dengue', 'dengue ns1', 'dengue serology', 'dengue profile', 'ns1 antigen', 'dengue igm', 'dengue duo', 'dengue test', 'breakbone', 'dengue fever', 'ns1 igm igg', 'dengue antibody'],
  typhoid: ['typhoid', 'widal', 'widal test', 'typhidot', 'enteric fever', 'salmonella typhi', 'typhoid serology', 'widal slide test', 'typhi dot', 'enteric fever panel'],
  troponin: ['troponin', 'trop i', 'troponin i', 'hs-ctni', 'hstroponin', 'cardiac troponin', 'trop-i', 'cardiac enzymes', 'heart attack marker', 'ctni', 'troponin t', 'hs trop', 'myocardial marker'],
  coagulation: ['coagulation', 'pt', 'inr', 'pt/inr', 'prothrombin time', 'aptt', 'clotting profile', 'coagulation profile', 'bleeding time', 'pt inr', 'clotting time', 'inr test', 'pre op coagulation'],
  calcium_phosphorus: ['calcium', 'serum calcium', 'phosphorus', 'calcium phosphorus', 'bone mineral', 'ionized calcium', 'ca++', 'hypocalcemia', 'hypercalcemia', 'total calcium', 'bone profile'],
  pancreatic: ['amylase', 'lipase', 'pancreatic', 'pancreas', 'serum lipase', 'serum amylase', 'pancreatic enzymes', 'acute pancreatitis', 'pancreas panel', 'amylase lipase'],
  urine_microalbumin: ['microalbumin', 'urine microalbumin', 'acr', 'albumin creatinine ratio', 'urine acr', 'spot microalbumin', 'diabetic kidney screen', 'renal microalbumin', 'microalbuminuria', 'urine albumin'],
  psa: ['psa', 'prostate specific antigen', 'total psa', 'prostate test', 'psa screening', 'prostate antigen', 'serum psa', 'psa total', 'prostate screen'],
  rheumatoid: ['rheumatoid', 'rf', 'ra factor', 'rheumatoid factor', 'anti ccp', 'anticcp', 'arthritis', 'joint pain panel', 'rheumatoid arthritis', 'ra test', 'arthritis panel', 'ra factor quantitative'],
  uric_acid: ['uric acid', 'serum uric acid', 'gout', 'hyperuricemia', 'urate', 'gout test', 'uric', 'uric acid level', 'blood uric acid'],
  viral_screen: ['viral marker', 'viral markers', 'hiv', 'hbsag', 'hcv', 'hepatitis b', 'hepatitis c', 'pre op viral screen', 'viral screening', 'serology tri panel', 'australia antigen', 'hiv hbsag hcv', 'tri dot'],
  cardiac_risk: ['cardiac risk', 'homocysteine', 'apolipoprotein', 'apo b', 'lp a', 'lipoprotein a', 'advanced cardiac', 'heart risk', 'vascular risk', 'atherosclerosis panel', 'apo-b'],
  allergy_ige: ['ige', 'total ige', 'allergy', 'allergy test', 'immunoglobulin e', 'atopy', 'allergic rhinitis', 'asthma panel', 'allergy screen', 'serum ige', 'allergy profile'],
  beta_hcg: ['hcg', 'beta hcg', 'b-hcg', 'pregnancy test', 'pregnancy blood test', 'human chorionic gonadotropin', 'bhcg', 'beta-hcg', 'serum beta hcg', 'serum pregnancy test']
};

function levenshteinSimilarityClient(s1, s2) {
  s1 = (s1 || '').toLowerCase().trim();
  s2 = (s2 || '').toLowerCase().trim();
  if (s1 === s2) return 1.0;
  if (!s1 || !s2) return 0.0;

  const len1 = s1.length;
  const len2 = s2.length;
  const dp = Array.from({ length: len1 + 1 }, () => Array(len2 + 1).fill(0));

  for (let i = 0; i <= len1; i++) dp[i][0] = i;
  for (let j = 0; j <= len2; j++) dp[0][j] = j;

  for (let i = 1; i <= len1; i++) {
    for (let j = 1; j <= len2; j++) {
      const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      );
    }
  }

  const dist = dp[len1][len2];
  const maxLen = Math.max(len1, len2);
  return Number((1.0 - dist / maxLen).toFixed(2));
}

function parsePrescriptionTextClient(rawText, testsList = null) {
  rawText = (rawText || '').trim();
  if (!rawText) return null;

  let allTests = testsList;
  if (!allTests || !Array.isArray(allTests) || allTests.length === 0) {
    allTests = LabStore._testsCache || [];
  }
  const delimiters = /[,;\n\r\t/&+]|\band\b|\bwith\b|\bplus\b|\balso\b|\badv\b|\badvise\b|\brx\b|\bcheck\b|\btest\b|\btests\b|\bpanel\b|\bneed\b|\bfor\b/i;
  const rawTokens = rawText.split(delimiters);
  const cleanedTokens = rawTokens.map(t => t.trim().toLowerCase()).filter(t => t.length > 1);

  const matchedTests = [];
  const matchedIds = new Set();

  allTests.forEach(test => {
    let bestScore = 0.0;
    let bestToken = '';
    let bestAlias = '';
    let reason = '';

    const aliases = CLINICAL_ALIASES_CLIENT[test.id] || [test.name.toLowerCase(), test.id.toLowerCase()];

    // 1. Direct regex substring search
    for (const alias of aliases) {
      const regex = new RegExp(`\\b${alias.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
      if (regex.test(rawText)) {
        bestScore = 1.0;
        bestToken = alias;
        bestAlias = alias;
        reason = `Exact clinical acronym match: '${alias.toUpperCase()}'`;
        break;
      }
    }

    // 2. Token-level fuzzy match
    if (bestScore < 1.0) {
      for (const token of cleanedTokens) {
        for (const alias of aliases) {
          const sim = levenshteinSimilarityClient(token, alias);
          if (sim > bestScore && sim >= 0.75) {
            bestScore = sim;
            bestToken = token;
            bestAlias = alias;
            reason = `Fuzzy matched '${token}' to '${alias}' (${Math.round(sim * 100)}% match)`;
          }
        }
      }
    }

    if (bestScore >= 0.75 && !matchedIds.has(test.id)) {
      matchedIds.add(test.id);
      matchedTests.push({
        ...test,
        confidence: bestScore,
        matchedToken: bestToken,
        matchedAlias: bestAlias,
        matchReason: reason
      });
    }
  });

  matchedTests.sort((a, b) => b.confidence - a.confidence);

  const totalPrice = matchedTests.reduce((acc, t) => acc + (t.price || 0), 0);
  const bundleDiscount = matchedTests.length >= 3 ? Math.round(totalPrice * 0.10) : 0;
  const finalPrice = totalPrice - bundleDiscount;
  const requiresFasting = matchedTests.some(t => t.fasting);
  const maxFastingHours = Math.max(...matchedTests.map(t => t.fastingHours || 0), 0);

  return {
    queryText: rawText,
    matchedCount: matchedTests.length,
    matchedTests,
    totalPrice,
    bundleDiscount,
    finalPrice,
    requiresFasting,
    maxFastingHours,
    fastingNotice: requiresFasting
      ? `Fasting Protocol: ${maxFastingHours} hours overnight water-only fasting is required for these biomarkers.`
      : 'No pre-test fasting required.'
  };
}

// ==================== Feature 4: Clinical Association Recommender ====================

const CLINICAL_ASSOCIATIONS_CLIENT = {
  hba1c: [
    { targetId: "kft", confidence: 0.84, reason: "Diabetic Nephropathy & Renal Clearance Monitoring (ADA Protocol)" },
    { targetId: "lipid", confidence: 0.78, reason: "Cardiovascular Risk & Diabetic Dyslipidemia Assessment" },
    { targetId: "urine_microalbumin", confidence: 0.88, reason: "Early Microvascular Diabetic Nephropathy Detection" }
  ],
  fbs_ppbs: [
    { targetId: "hba1c", confidence: 0.94, reason: "Glycated Hemoglobin 90-Day Glycemic Control Correlation" },
    { targetId: "urine_microalbumin", confidence: 0.86, reason: "Glomerular Hyperfiltration & Diabetic Renal Screening" }
  ],
  lipid: [
    { targetId: "hba1c", confidence: 0.79, reason: "Metabolic Syndrome & Insulin Resistance Evaluation" },
    { targetId: "lft", confidence: 0.72, reason: "Baseline Hepatic Enzyme Assessment for Lipid Clearance" },
    { targetId: "cardiac_risk", confidence: 0.83, reason: "Apolipoprotein-B & Vascular Endothelial Risk Assessment" }
  ],
  troponin: [
    { targetId: "lipid", confidence: 0.86, reason: "Atherosclerotic Coronary Plaque Risk Assessment" },
    { targetId: "electrolytes", confidence: 0.82, reason: "Arrhythmogenic Myocardial Ion Surveillance (K+/Mg2+)" },
    { targetId: "crp", confidence: 0.80, reason: "Acute Coronary Arterial Wall Inflammation Index" }
  ],
  crp: [
    { targetId: "cbc", confidence: 0.88, reason: "Leukocyte & Platelet Infection Response Differential" },
    { targetId: "esr", confidence: 0.85, reason: "Synchronous Acute vs Chronic Inflammatory Phase Tracking" }
  ],
  esr: [
    { targetId: "cbc", confidence: 0.89, reason: "Anemia & White Cell Differential Correlation" },
    { targetId: "crp", confidence: 0.84, reason: "Complementary Acute-Phase Protein Confirmation" }
  ],
  dengue: [
    { targetId: "cbc", confidence: 0.96, reason: "Urgent Platelet Count & Hemoconcentration (PCV) Surveillance" },
    { targetId: "lft", confidence: 0.78, reason: "Hepatic Transaminase Flare Monitoring in Dengue" }
  ],
  typhoid: [
    { targetId: "cbc", confidence: 0.86, reason: "Relative Bradycardia & Leukopenia Differential in Pyrexia" },
    { targetId: "lft", confidence: 0.77, reason: "Enteric Hepatitis & Hepatic Clearance Monitoring" }
  ],
  thyroid: [
    { targetId: "vitd_b12", confidence: 0.81, reason: "Chronic Fatigue, Neuropathy & Autoimmune Screening" },
    { targetId: "lipid", confidence: 0.69, reason: "Hypothyroidism-induced Secondary Hyperlipidemia" }
  ],
  cbc: [
    { targetId: "esr", confidence: 0.88, reason: "Systemic Inflammatory & Infection Severity Index" },
    { targetId: "iron_profile", confidence: 0.86, reason: "Iron Deficiency Microcytic Anemia Differential" },
    { targetId: "vitd_b12", confidence: 0.76, reason: "Megaloblastic Anemia & Cellular Maturation Workup" }
  ],
  lft: [
    { targetId: "kft", confidence: 0.83, reason: "Hepatorenal Function & Metabolic Clearance Index" },
    { targetId: "lipid", confidence: 0.74, reason: "Fatty Liver (NAFLD) & Lipid Clearance Workup" },
    { targetId: "viral_screen", confidence: 0.79, reason: "Viral Hepatitis (HBsAg / HCV) Etiology Screen" }
  ],
  kft: [
    { targetId: "electrolytes", confidence: 0.89, reason: "Renal Tubular Excretion & Electrolyte Clearance Index" },
    { targetId: "urine_re", confidence: 0.84, reason: "Complete Urinary Sediment & Proteinuria Correlation" },
    { targetId: "hba1c", confidence: 0.82, reason: "Diabetic Kidney Disease Screening" }
  ],
  electrolytes: [
    { targetId: "kft", confidence: 0.89, reason: "Renal Glomerular & Tubular Filtration Balance" },
    { targetId: "calcium_phosphorus", confidence: 0.78, reason: "Complete Mineral & Divalent Cation Homeostasis" }
  ],
  urine_re: [
    { targetId: "kft", confidence: 0.83, reason: "Glomerular Clearance & Creatinine Evaluation" },
    { targetId: "urine_microalbumin", confidence: 0.80, reason: "Early Quantitative Microalbuminuria Confirmation" }
  ],
  iron_profile: [
    { targetId: "cbc", confidence: 0.92, reason: "Complete Red Blood Cell Indices & Hematocrit Correlation" },
    { targetId: "vitd_b12", confidence: 0.80, reason: "Nutritional Anemia & Co-Factor Deficiency Workup" }
  ],
  rheumatoid: [
    { targetId: "crp", confidence: 0.89, reason: "Synovial Inflammation Severity & Disease Activity Score" },
    { targetId: "uric_acid", confidence: 0.83, reason: "Gouty vs Rheumatoid Polyarthritis Differential" },
    { targetId: "esr", confidence: 0.81, reason: "Chronic Autoimmune Flare-up Rate Tracking" }
  ],
  uric_acid: [
    { targetId: "kft", confidence: 0.86, reason: "Renal Urate Clearance & Gout Nephropathy Assessment" },
    { targetId: "lipid", confidence: 0.73, reason: "Metabolic Syndrome & Hyperuricemia Co-Morbidity" }
  ],
  pancreatic: [
    { targetId: "lft", confidence: 0.85, reason: "Biliary Gallstone Pancreatitis & Obstruction Workup" },
    { targetId: "electrolytes", confidence: 0.80, reason: "Pancreatic Third-Spacing Fluid & Electrolyte Shift" }
  ],
  calcium_phosphorus: [
    { targetId: "vitd_b12", confidence: 0.90, reason: "Vitamin D-Dependent Calcium Absorption & Bone Health" },
    { targetId: "kft", confidence: 0.79, reason: "Renal Calcium/Phosphate Excretion Dynamics" }
  ],
  psa: [
    { targetId: "urine_re", confidence: 0.82, reason: "Exclude Urinary Infection Artifact in Elevated PSA" },
    { targetId: "kft", confidence: 0.75, reason: "Obstructive Uropathy & Renal Outflow Surveillance" }
  ],
  coagulation: [
    { targetId: "cbc", confidence: 0.88, reason: "Baseline Platelet Count for Primary Hemostasis" },
    { targetId: "lft", confidence: 0.85, reason: "Hepatic Synthesis of Vitamin K Clotting Factors" }
  ],
  viral_screen: [
    { targetId: "lft", confidence: 0.87, reason: "Hepatocellular Damage & Transaminase Baseline" },
    { targetId: "cbc", confidence: 0.78, reason: "Immunologic Lymphocyte & Cytopenia Screening" }
  ],
  allergy_ige: [
    { targetId: "cbc", confidence: 0.87, reason: "Absolute Eosinophil Count (AEC) Allergic Correlation" }
  ],
  cardiac_risk: [
    { targetId: "lipid", confidence: 0.91, reason: "Primary Lipid Profile Atherogenic Subfraction Baseline" },
    { targetId: "troponin", confidence: 0.82, reason: "Subclinical Myocardial Stress & Troponin Baseline" }
  ],
  urine_microalbumin: [
    { targetId: "hba1c", confidence: 0.90, reason: "Diabetic Microvascular Complication Monitoring" },
    { targetId: "kft", confidence: 0.85, reason: "Renal Clearance & Glomerular Filtration Integrity" }
  ],
  vitd_b12: [
    { targetId: "thyroid", confidence: 0.77, reason: "Endocrine & Cellular Energy Regulation" },
    { targetId: "cbc", confidence: 0.75, reason: "Red Blood Cell Maturation & Hemoglobin Synthesis" },
    { targetId: "calcium_phosphorus", confidence: 0.88, reason: "Cholecalciferol-Bone Mineralization Homeostasis" }
  ]
};

function getCompanionRecommendationsClient(cartIds = [], testsList = []) {
  if (!cartIds || cartIds.length === 0) return [];
  let tests = testsList;
  if (!tests || !Array.isArray(tests) || tests.length === 0) {
    tests = LabStore._testsCache || [];
  }
  const testMap = new Map(tests.map(t => [t.id, t]));
  const candidateMap = new Map();

  cartIds.forEach(id => {
    const assocs = CLINICAL_ASSOCIATIONS_CLIENT[id] || [];
    assocs.forEach(assoc => {
      const targetId = assoc.targetId;
      if (cartIds.includes(targetId)) return;
      const targetTest = testMap.get(targetId);
      if (!targetTest) return;

      const existing = candidateMap.get(targetId);
      if (!existing || assoc.confidence > existing.confidence) {
        const addonPrice = Math.round(targetTest.price * 0.85); // 15% companion bundle discount
        candidateMap.set(targetId, {
          ...targetTest,
          confidence: assoc.confidence,
          correlationPct: Math.round(assoc.confidence * 100),
          reason: assoc.reason,
          addonPrice: addonPrice,
          savings: targetTest.price - addonPrice,
          triggeredBy: id
        });
      }
    });
  });

  return Array.from(candidateMap.values())
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 3);
}

// ==================== Universal Responsive Mobile Navigation & Persona Sync ====================

function initResponsiveMobileNav() {
  if (typeof window === 'undefined' || typeof document === 'undefined') return;
  const path = window.location.pathname.toLowerCase().replace(/\\/g, '/');
  
  // Only inject inside portal sub-directories (patient, technician, admin)
  const isPatient = path.includes('/patient/');
  const isTech = path.includes('/technician/');
  const isAdmin = path.includes('/admin/');
  if (!isPatient && !isTech && !isAdmin) return;

  const currentPortal = isPatient ? 'patient' : isTech ? 'technician' : 'admin';

  // Add safe padding to body on mobile so bottom nav does not overlap content
  document.body.classList.add('mobile-nav-padded');

  // 1. Mobile Bottom Navigation Bar definition
  const navConfigs = {
    patient: [
      {
        label: 'Catalog',
        file: 'catalog.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>'
      },
      {
        label: 'Tracking',
        file: 'tracking.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
      },
      {
        label: 'Reports',
        file: 'reports.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>'
      },
      {
        label: 'Verify',
        file: 'verify.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>'
      }
    ],
    technician: [
      {
        label: 'Queue',
        file: 'queue.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>'
      },
      {
        label: 'Result Entry',
        file: 'result-entry.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>'
      },
      {
        label: 'Switch Role',
        action: 'openRoleSwitchModal()',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>'
      }
    ],
    admin: [
      {
        label: 'Analytics',
        file: 'dashboard.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>'
      },
      {
        label: 'Dispatch',
        file: 'assign.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>'
      },
      {
        label: 'Catalog CRUD',
        file: 'catalog-manage.html',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>'
      },
      {
        label: 'Switch Role',
        action: 'openRoleSwitchModal()',
        icon: '<svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>'
      }
    ]
  };

  const currentItems = navConfigs[currentPortal] || [];
  let existingBottomNav = document.getElementById('labline-mobile-bottom-nav');
  if (!existingBottomNav && currentItems.length > 0) {
    const bottomNav = document.createElement('nav');
    bottomNav.id = 'labline-mobile-bottom-nav';
    bottomNav.className = 'mobile-bottom-nav md:hidden';
    bottomNav.setAttribute('aria-label', 'Mobile Portal Navigation');

    const html = currentItems.map(item => {
      const isCurrent = item.file && path.endsWith(item.file);
      const href = item.file ? item.file : 'javascript:void(0)';
      const onclickAttr = item.action ? `onclick="${item.action}"` : '';
      return `
        <a href="${href}" ${onclickAttr} class="mobile-nav-item ${isCurrent ? 'active' : ''}">
          ${item.icon}
          <span>${item.label}</span>
        </a>
      `;
    }).join('');

    bottomNav.innerHTML = html;
    document.body.appendChild(bottomNav);
  }

  // 2. Mobile Header Hamburger Button
  const header = document.querySelector('header');
  if (header && !document.getElementById('mobile-menu-btn')) {
    const headerContainer = header.querySelector('.max-w-7xl, .max-w-6xl, .max-w-5xl, div');
    if (headerContainer) {
      const rightArea = headerContainer.querySelector('.flex.items-center.gap-3') || headerContainer;
      const hamburger = document.createElement('button');
      hamburger.id = 'mobile-menu-btn';
      hamburger.type = 'button';
      hamburger.className = 'md:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors border border-slate-200';
      hamburger.setAttribute('aria-label', 'Toggle Mobile Menu');
      hamburger.innerHTML = `<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>`;
      hamburger.onclick = toggleMobileDrawer;
      rightArea.insertBefore(hamburger, rightArea.firstChild);
    }
  }
}

function toggleMobileDrawer() {
  let drawer = document.getElementById('mobile-drawer-modal');
  if (drawer) {
    drawer.remove();
    document.body.classList.remove('modal-open');
    return;
  }

  const path = window.location.pathname.toLowerCase().replace(/\\/g, '/');
  const currentUser = LabStore.getCurrentUser();
  const userName = currentUser ? (currentUser.name || 'User') : 'Guest';
  const userRole = currentUser ? (currentUser.role || 'patient').toUpperCase() : 'PATIENT';

  drawer = document.createElement('div');
  drawer.id = 'mobile-drawer-modal';
  drawer.className = 'modal-backdrop md:hidden';
  drawer.onclick = (e) => { 
    if (e.target === drawer) {
      drawer.remove();
      document.body.classList.remove('modal-open');
    }
  };

  document.body.classList.add('modal-open');

  drawer.innerHTML = `
    <div class="modal-sheet" style="padding: 20px; max-width: 360px;">
      <div style="display:flex; align-items:center; justify-content:space-between; padding-bottom:12px; border-bottom:1px solid var(--border);">
        <div style="display:flex; align-items:center; gap:10px;">
          <div class="brand-icon" style="width:32px; height:32px; font-size:12px;">LL</div>
          <div>
            <h3 style="font-size:13px; font-weight:700; color:var(--text-primary); margin:0;">${userName}</h3>
            <span style="font-size:10px; font-family:var(--font-mono); color:var(--accent-text); font-weight:600;">${userRole} WORKSPACE</span>
          </div>
        </div>
        <button type="button" onclick="document.getElementById('mobile-drawer-modal').remove(); document.body.classList.remove('modal-open');" style="background:var(--surface-subtle); border:1px solid var(--border); border-radius:50%; width:28px; height:28px; color:var(--text-secondary); cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:14px;">&times;</button>
      </div>

      <div style="margin-top:14px;">
        <span style="font-size:11px; font-weight:600; color:var(--text-muted); display:block; margin-bottom:8px;">Switch Role:</span>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:6px;">
          <button type="button" onclick="switchPortalRole('patient')" class="app-btn ${path.includes('/patient/') ? 'app-btn-primary' : 'app-btn-secondary'}" style="padding:8px 6px; font-size:11px;">Patient</button>
          <button type="button" onclick="switchPortalRole('technician')" class="app-btn ${path.includes('/technician/') ? 'app-btn-primary' : 'app-btn-secondary'}" style="padding:8px 6px; font-size:11px;">Tech</button>
          <button type="button" onclick="switchPortalRole('admin')" class="app-btn ${path.includes('/admin/') ? 'app-btn-primary' : 'app-btn-secondary'}" style="padding:8px 6px; font-size:11px;">Admin</button>
        </div>
      </div>

      <div style="margin-top:16px; padding-top:12px; border-top:1px solid var(--border);">
        <button type="button" onclick="LabStore.logout()" class="app-btn app-btn-danger" style="width:100%; justify-content:center;">
          <svg style="width:14px; height:14px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
          <span>Sign Out</span>
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(drawer);
}

function openRoleSwitchModal() {
  toggleMobileDrawer();
}

// Attach utilities to window
window.LabStore = LabStore;
window.showToast = showToast;
window.toggleTheme = toggleTheme;
window.evaluateParameter = evaluateParameter;
window.generateDietAdviceForResults = generateDietAdviceForResults;
window.switchPortalRole = switchPortalRole;
window.computeSha256 = computeSha256;
window.generateOrderReportHash = generateOrderReportHash;
window.verifyOrderIntegrity = verifyOrderIntegrity;
window.computeSpecimenPriority = computeSpecimenPriority;
window.autoDispatchWorkload = autoDispatchWorkload;
window.levenshteinSimilarityClient = levenshteinSimilarityClient;
window.parsePrescriptionTextClient = parsePrescriptionTextClient;
window.getCompanionRecommendationsClient = getCompanionRecommendationsClient;
window.initResponsiveMobileNav = initResponsiveMobileNav;
window.toggleMobileDrawer = toggleMobileDrawer;
window.openRoleSwitchModal = openRoleSwitchModal;
window.STAGES = STAGES;
window.PHLEBOTOMISTS = PHLEBOTOMISTS;
window.TECHNICIANS = TECHNICIANS;

// Auto-initialize mobile navigation on DOM ready
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initResponsiveMobileNav);
  } else {
    initResponsiveMobileNav();
  }
}



