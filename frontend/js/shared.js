/**
 * LabLine — Enterprise Diagnostic Portal & Laboratory Management System
 * Shared Clinical Data Models, LocalStorage Store, and Analytical Helpers
 */

const DEFAULT_TESTS = [
  {
    id: 'cbc',
    name: 'Complete Blood Count (CBC)',
    category: 'Hematology',
    price: 350,
    sampleType: 'EDTA Whole Blood (2ml)',
    tubeCapClass: 'tube-cap-edta',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Evaluates overall cellular health and screens for anemia, acute infections, immune disorders, and platelet abnormalities.',
    parameters: [
      { key: 'hb', label: 'Hemoglobin', unit: 'g/dL', min: 13.0, max: 17.0, defaultVal: 14.2 },
      { key: 'wbc', label: 'Total Leukocyte Count (WBC)', unit: '/µL', min: 4000, max: 11000, defaultVal: 7500 },
      { key: 'rbc', label: 'Total RBC Count', unit: 'million/µL', min: 4.5, max: 5.9, defaultVal: 5.1 },
      { key: 'plt', label: 'Platelet Count', unit: 'lakh/µL', min: 1.5, max: 4.5, defaultVal: 2.8 },
      { key: 'pcv', label: 'Packed Cell Volume (PCV)', unit: '%', min: 40, max: 50, defaultVal: 44.5 }
    ]
  },
  {
    id: 'lipid',
    name: 'Lipid Profile (Comprehensive)',
    category: 'Biochemistry',
    price: 650,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '6 Hours',
    fasting: true,
    fastingHours: 12,
    description: 'Measures circulating blood cholesterol fractions to quantify atherosclerotic risk and cardiovascular profile.',
    parameters: [
      { key: 'chol', label: 'Total Cholesterol', unit: 'mg/dL', min: 125, max: 200, defaultVal: 185 },
      { key: 'tg', label: 'Triglycerides', unit: 'mg/dL', min: 50, max: 150, defaultVal: 135 },
      { key: 'hdl', label: 'HDL (Good Cholesterol)', unit: 'mg/dL', min: 40, max: 60, defaultVal: 48 },
      { key: 'ldl', label: 'LDL (Bad Cholesterol)', unit: 'mg/dL', min: 60, max: 100, defaultVal: 92 },
      { key: 'vldl', label: 'VLDL Cholesterol', unit: 'mg/dL', min: 10, max: 30, defaultVal: 24 }
    ]
  },
  {
    id: 'thyroid',
    name: 'Thyroid Function Panel (TFT)',
    category: 'Endocrinology',
    price: 550,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '6 Hours',
    fasting: false,
    description: 'Measures Ultrasensitive TSH, Total T3, and Total T4 to assess thyroid gland metabolic homeostasis.',
    parameters: [
      { key: 'tsh', label: 'TSH (Ultrasensitive)', unit: 'µIU/mL', min: 0.35, max: 4.94, defaultVal: 2.45 },
      { key: 't3', label: 'Total Triiodothyronine (T3)', unit: 'ng/dL', min: 80, max: 200, defaultVal: 130 },
      { key: 't4', label: 'Total Thyroxine (T4)', unit: 'µg/dL', min: 5.1, max: 14.1, defaultVal: 8.8 }
    ]
  },
  {
    id: 'hba1c',
    name: 'HbA1c & Estimated Glucose',
    category: 'Diabetes Care',
    price: 450,
    sampleType: 'EDTA Whole Blood (2ml)',
    tubeCapClass: 'tube-cap-edta',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Gold-standard glycated biomarker providing an accurate 90-day glycemic control profile.',
    parameters: [
      { key: 'hba1c_pct', label: 'HbA1c (Glycated Hemoglobin)', unit: '%', min: 4.0, max: 5.6, defaultVal: 5.4 },
      { key: 'eag', label: 'Estimated Avg Glucose (eAG)', unit: 'mg/dL', min: 70, max: 115, defaultVal: 108 }
    ]
  },
  {
    id: 'lft',
    name: 'Liver Function Panel (LFT)',
    category: 'Biochemistry',
    price: 750,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '8 Hours',
    fasting: true,
    fastingHours: 8,
    description: 'Evaluates hepatic enzyme kinetics, biliary excretion, and liver protein synthesis.',
    parameters: [
      { key: 'sgot', label: 'SGOT / AST (Transaminase)', unit: 'U/L', min: 5, max: 40, defaultVal: 26 },
      { key: 'sgpt', label: 'SGPT / ALT (Transaminase)', unit: 'U/L', min: 7, max: 56, defaultVal: 32 },
      { key: 'bili_tot', label: 'Total Bilirubin', unit: 'mg/dL', min: 0.2, max: 1.2, defaultVal: 0.8 },
      { key: 'alp', label: 'Alkaline Phosphatase (ALP)', unit: 'U/L', min: 44, max: 147, defaultVal: 95 },
      { key: 'protein', label: 'Total Serum Protein', unit: 'g/dL', min: 6.4, max: 8.3, defaultVal: 7.2 }
    ]
  },
  {
    id: 'kft',
    name: 'Kidney Function Profile (KFT)',
    category: 'Biochemistry',
    price: 600,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '6 Hours',
    fasting: false,
    description: 'Evaluates glomerular filtration integrity, serum creatinine clearance, and nitrogenous urea excretion.',
    parameters: [
      { key: 'creat', label: 'Serum Creatinine', unit: 'mg/dL', min: 0.6, max: 1.2, defaultVal: 0.9 },
      { key: 'bun', label: 'Blood Urea Nitrogen (BUN)', unit: 'mg/dL', min: 7, max: 20, defaultVal: 14 },
      { key: 'uric', label: 'Serum Uric Acid', unit: 'mg/dL', min: 3.5, max: 7.2, defaultVal: 5.2 }
    ]
  },
  {
    id: 'vitd_b12',
    name: 'Vitamin D & B12 Vitality Duo',
    category: 'Wellness',
    price: 1100,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '12 Hours',
    fasting: false,
    description: 'Assesses bone mineralization density, neurological integrity, and cellular metabolic vitality.',
    parameters: [
      { key: 'vit_d', label: 'Vitamin D (25-OH Hydroxy)', unit: 'ng/mL', min: 30, max: 100, defaultVal: 34 },
      { key: 'vit_b12', label: 'Vitamin B12 (Cyanocobalamin)', unit: 'pg/mL', min: 211, max: 911, defaultVal: 480 }
    ]
  }
];

const STAGES = [
  'Booked',
  'Sample Collected',
  'In-Transit',
  'Processing',
  'Report Generated'
];

const PHLEBOTOMISTS = [
  { id: 'phleb-1', name: 'Rupesh Patel', phone: '+91 98450 12345', activePickups: 2, rating: 4.9 },
  { id: 'phleb-2', name: 'Varshith Gowda', phone: '+91 98450 67890', activePickups: 1, rating: 4.8 },
  { id: 'phleb-3', name: 'Yatish Shetty', phone: '+91 98450 54321', activePickups: 3, rating: 4.9 }
];

const TECHNICIANS = [
  { id: 'tech-1', name: 'Dr. Yatish Rao (Lead Pathologist)', role: 'technician', station: 'Central Diagnostics' },
  { id: 'tech-2', name: 'Varshith Gowda (Senior Technologist)', role: 'technician', station: 'Automated Analyzer Station 4' },
  { id: 'tech-3', name: 'Rupesh Patel (Clinical Biochemist)', role: 'technician', station: 'Biochemistry Station 2' }
];

const DEFAULT_ORDERS = [
  {
    id: 'LL-2026-8941',
    patientName: 'Aryan Sharma',
    patientAge: 29,
    patientGender: 'Male',
    patientPhone: '+91 98765 43210',
    patientEmail: 'aryan@labline.com',
    testIds: ['cbc', 'lipid'],
    testNames: ['Complete Blood Count (CBC)', 'Lipid Profile (Comprehensive)'],
    type: 'Home Pickup',
    address: '42 Crescent Avenue, Bangalore - 560001',
    date: '2026-08-30',
    timeSlot: '07:30 AM - 08:30 AM',
    totalAmount: 1000,
    paymentStatus: 'Paid',
    paymentMethod: 'UPI / Razorpay',
    transactionId: 'pay_RAZORPAY_8941',
    status: 'Processing',
    currentStage: 'Processing',
    phlebotomist: 'Rupesh Patel',
    technician: 'Varshith Gowda',
    urgency: 'Routine',
    sampleTubeBarcode: 'BC89410982',
    temperatureTelemetry: '3.8°C (Cold-Chain Verified)',
    timestamps: {
      booked: '08:15 AM',
      collected: '09:30 AM',
      inTransit: '10:15 AM',
      processing: '11:00 AM',
      completed: null
    },
    results: {
      hb: 14.2,
      wbc: 7600,
      rbc: 5.1,
      plt: 2.8,
      pcv: 44.2,
      chol: 218, // Elevated to trigger clinical dietary engine
      tg: 165,
      hdl: 46,
      ldl: 112,
      vldl: 26
    },
    dietAdvice: [
      {
        category: 'Cardiovascular & Lipid Balance',
        items: [
          'Incorporate soluble viscous fiber: steel-cut oats, chia seeds, and fresh seasonal fruits.',
          'Substitute dietary saturated fats with monounsaturated fats: cold-pressed olive oil & walnuts.',
          'Eliminate hydrogenated trans-fats and commercially fried products.'
        ]
      },
      {
        category: 'Lifestyle Recommendation',
        items: [
          '30 minutes of moderate aerobic cardiovascular exercise 5 days per week.',
          'Maintain metabolic cellular hydration (2.5 - 3.0 Liters daily).'
        ]
      }
    ]
  },
  {
    id: 'LL-2026-8942',
    patientName: 'Rupesh Patel',
    patientAge: 32,
    patientGender: 'Female',
    patientPhone: '+91 98441 22334',
    patientEmail: 'rupesh.patel@example.com',
    testIds: ['thyroid', 'vitd_b12'],
    testNames: ['Thyroid Function Panel (TFT)', 'Vitamin D & B12 Vitality Duo'],
    type: 'Home Pickup',
    address: '88 Skyline Boulevard, Bangalore - 560038',
    date: '2026-08-30',
    timeSlot: '08:30 AM - 09:30 AM',
    totalAmount: 1650,
    paymentStatus: 'Paid',
    paymentMethod: 'Credit Card',
    transactionId: 'pay_CARD_8942',
    status: 'Sample Collected',
    currentStage: 'Sample Collected',
    phlebotomist: 'Varshith Gowda',
    technician: 'Dr. Yatish Rao',
    urgency: 'Routine',
    sampleTubeBarcode: 'BC89429184',
    temperatureTelemetry: '4.1°C (Monitored)',
    timestamps: {
      booked: '08:45 AM',
      collected: '10:30 AM',
      inTransit: null,
      processing: null,
      completed: null
    },
    results: {}
  },
  {
    id: 'LL-2026-8940',
    patientName: 'Nitish Kumar',
    patientAge: 48,
    patientGender: 'Male',
    patientPhone: '+91 97412 88990',
    patientEmail: 'nitish.kumar@example.com',
    testIds: ['hba1c', 'kft'],
    testNames: ['HbA1c & Estimated Glucose', 'Kidney Function Profile (KFT)'],
    type: 'Lab Visit',
    address: 'LabLine Central Clinical Laboratory',
    date: '2026-08-30',
    timeSlot: '09:00 AM - 10:00 AM',
    totalAmount: 1050,
    paymentStatus: 'Paid',
    paymentMethod: 'UPI',
    transactionId: 'pay_UPI_8940',
    status: 'Report Generated',
    currentStage: 'Report Generated',
    phlebotomist: 'Central Lab Station #2',
    technician: 'Varshith Gowda',
    urgency: 'STAT',
    sampleTubeBarcode: 'BC89401726',
    temperatureTelemetry: '3.6°C (Verified)',
    timestamps: {
      booked: '07:00 AM',
      collected: '07:45 AM',
      inTransit: '08:00 AM',
      processing: '08:30 AM',
      completed: '09:45 AM'
    },
    results: {
      hba1c_pct: 6.2,
      eag: 131,
      creat: 1.0,
      bun: 16,
      uric: 5.8
    },
    reportHash: 'e7a9b401f83c42e989417d91e6b8c4d284a1e938f219cb84e72081d5b3a9e4f1',
    isCertified: true,
    certifiedAt: '2026-08-30 09:45 AM',
    dietAdvice: [
      {
        category: 'Glycemic Regulation & Metabolic Care',
        items: [
          'Prioritize low glycemic-index complex whole grains: quinoa, barley, and steel-cut oats.',
          'Include high-fiber cruciferous vegetables, bitter gourd, and fenugreek seeds.',
          'Eliminate refined sugars, carbonated syrups, and processed carbohydrates.'
        ]
      }
    ]
  }
];

const LabStore = {
  getTests() {
    const data = localStorage.getItem('labline_tests');
    if (!data) {
      localStorage.setItem('labline_tests', JSON.stringify(DEFAULT_TESTS));
      return DEFAULT_TESTS;
    }
    return JSON.parse(data);
  },

  saveTests(tests) {
    localStorage.setItem('labline_tests', JSON.stringify(tests));
  },

  getOrders() {
    const data = localStorage.getItem('labline_orders');
    if (!data) {
      localStorage.setItem('labline_orders', JSON.stringify(DEFAULT_ORDERS));
      return DEFAULT_ORDERS;
    }
    return JSON.parse(data);
  },

  saveOrders(orders) {
    localStorage.setItem('labline_orders', JSON.stringify(orders));
  },

  getOrderById(orderId) {
    const orders = this.getOrders();
    return orders.find(o => o.id === orderId) || orders[0];
  },

  updateOrder(updatedOrder) {
    const orders = this.getOrders();
    const idx = orders.findIndex(o => o.id === updatedOrder.id);
    if (idx !== -1) {
      orders[idx] = updatedOrder;
    } else {
      orders.unshift(updatedOrder);
    }
    this.saveOrders(orders);
    return updatedOrder;
  },

  getActiveOrder() {
    const activeId = localStorage.getItem('labline_active_order_id');
    const orders = this.getOrders();
    if (activeId) {
      const found = orders.find(o => o.id === activeId);
      if (found) return found;
    }
    return orders[0];
  },

  setActiveOrder(orderId) {
    localStorage.setItem('labline_active_order_id', orderId);
  },

  getCart() {
    const data = localStorage.getItem('labline_cart');
    return data ? JSON.parse(data) : ['cbc'];
  },

  saveCart(cart) {
    localStorage.setItem('labline_cart', JSON.stringify(cart));
  },

  getCurrentUser() {
    const data = localStorage.getItem('labline_user');
    if (!data) {
      return {
        name: 'Aryan Sharma',
        email: 'aryan@labline.com',
        role: 'patient',
        token: 'jwt_mock_token_clinical_2026'
      };
    }
    return JSON.parse(data);
  },

  setCurrentUser(user) {
    localStorage.setItem('labline_user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('labline_user');
    const path = window.location.pathname;
    if (path.includes('/patient/') || path.includes('/admin/') || path.includes('/technician/')) {
      window.location.href = '../index.html';
    } else {
      window.location.href = 'index.html';
    }
  }
};

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
    ? `<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M5 13l4 4L19 7"/></svg>`
    : type === 'error'
    ? `<svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M6 18L18 6M6 6l12 12"/></svg>`
    : `<svg class="w-4 h-4 text-teal-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

  toast.innerHTML = `
    ${iconSvg}
    <div class="flex-1 text-xs font-medium leading-snug">${message}</div>
    <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white shrink-0 p-1 text-sm font-bold">&times;</button>
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

// Universal Role Switcher for instant testing
function switchPortalRole(role) {
  const roleMap = {
    patient: {
      name: 'Aryan Sharma',
      email: 'aryan@labline.com',
      url: 'patient/catalog.html'
    },
    technician: {
      name: 'Varshith Gowda (Technologist)',
      email: 'technician@labline.com',
      url: 'technician/queue.html'
    },
    admin: {
      name: 'Nitish Kumar (Administrator)',
      email: 'admin@labline.com',
      url: 'admin/dashboard.html'
    }
  };

  const target = roleMap[role];
  if (!target) return;

  LabStore.setCurrentUser({
    name: target.name,
    email: target.email,
    role: role,
    token: `jwt_${role}_${Date.now()}`
  });

  const path = window.location.pathname;
  let targetPath = target.url;
  if (path.includes('/patient/') || path.includes('/technician/') || path.includes('/admin/')) {
    targetPath = '../' + target.url;
  }

  showToast(`Switched to ${role.toUpperCase()} mode.`, 'success');
  setTimeout(() => {
    window.location.href = targetPath;
  }, 300);
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

function computeCanonicalReportPayload(order, simulatedResults = null) {
  const results = simulatedResults || order.results || {};
  const sortedKeys = Object.keys(results).sort();
  const canonicalResults = sortedKeys.map(k => `${k}:${parseFloat(results[k] || 0).toFixed(2)}`).join(';');
  const sortedTests = (order.testNames || []).slice().sort().map(t => t.trim().toUpperCase()).join(',');
  return `ISSUER=LABLINE_CLINICAL_PATHOLOGY|BOOKING_ID=${(order.id || '').trim()}|PATIENT=${(order.patientName || '').trim().toUpperCase()}|TESTS=${sortedTests}|RESULTS=${canonicalResults}`;
}

async function generateOrderReportHash(order, customResults = null) {
  const payload = computeCanonicalReportPayload(order, customResults);
  return await computeSha256(payload);
}

async function verifyOrderIntegrity(order, testedResults = null) {
  const computedHash = await generateOrderReportHash(order, testedResults);
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

function autoDispatchWorkload() {
  const orders = LabStore.getOrders();
  const activeTechs = [
    'Varshith Gowda (Senior Technologist)',
    'Rupesh Patel (Clinical Biochemist)',
    'Dr. Yatish Rao (Lead Pathologist)'
  ];

  // Baseline load map
  const loads = {};
  activeTechs.forEach(t => loads[t] = 0);

  // Identify active (uncompleted) orders
  const activeOrders = orders.filter(o => o.currentStage !== 'Report Generated');

  // Score each active order
  const scored = activeOrders.map(o => {
    const p = computeSpecimenPriority(o);
    return { order: o, score: p.score, info: p };
  });

  // Sort descending by priority score (Greedy max-priority first)
  scored.sort((a, b) => b.score - a.score);

  const allocations = [];
  scored.forEach(item => {
    // Greedy Choice: find technician with lowest load
    let minTech = activeTechs[0];
    let minVal = loads[minTech];
    activeTechs.forEach(t => {
      if (loads[t] < minVal) {
        minVal = loads[t];
        minTech = t;
      }
    });

    item.order.technician = minTech;
    loads[minTech]++;

    allocations.push({
      orderId: item.order.id,
      patientName: item.order.patientName,
      urgency: item.order.urgency,
      score: item.score,
      tier: item.info.tier,
      assignedTech: minTech,
      reason: `Priority Score ${item.score} routed to ${minTech.split(' ')[0]} (Station load: ${loads[minTech]})`
    });
  });

  LabStore.saveOrders(orders);

  return {
    success: true,
    dispatchedCount: allocations.length,
    balancedLoads: loads,
    allocations: allocations
  };
}

// Attach utilities to window
window.LabStore = LabStore;
window.showToast = showToast;
window.evaluateParameter = evaluateParameter;
window.generateDietAdviceForResults = generateDietAdviceForResults;
window.switchPortalRole = switchPortalRole;
window.computeSha256 = computeSha256;
window.generateOrderReportHash = generateOrderReportHash;
window.verifyOrderIntegrity = verifyOrderIntegrity;
window.computeSpecimenPriority = computeSpecimenPriority;
window.autoDispatchWorkload = autoDispatchWorkload;
window.STAGES = STAGES;
window.PHLEBOTOMISTS = PHLEBOTOMISTS;
window.TECHNICIANS = TECHNICIANS;

