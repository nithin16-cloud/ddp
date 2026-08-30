/**
 * LabLine — Diagnostic Portal & Lab Management System
 * Shared Data Models, LocalStorage Engine, and Clinical Calculation Helpers
 */

const DEFAULT_TESTS = [
  {
    id: 'cbc',
    name: 'Complete Blood Count (CBC)',
    category: 'Hematology',
    price: 350,
    sampleType: 'EDTA Whole Blood (2ml)',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Evaluates overall health and screens for anemia, infections, leukemia, and platelet disorders.',
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
    name: 'Lipid Profile (Complete)',
    category: 'Biochemistry',
    price: 650,
    sampleType: 'Serum (Gold Top Tube)',
    turnaround: '6 Hours',
    fasting: true,
    fastingHours: 12,
    description: 'Measures circulating blood lipids to determine cardiovascular risk and atherosclerosis profile.',
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
    name: 'Thyroid Function Test (TFT)',
    category: 'Endocrinology',
    price: 550,
    sampleType: 'Serum (Gold Top Tube)',
    turnaround: '6 Hours',
    fasting: false,
    description: 'Measures TSH, Total T3, and Total T4 to assess thyroid gland metabolic function.',
    parameters: [
      { key: 'tsh', label: 'TSH (Thyroid Stimulating Hormone)', unit: 'µIU/mL', min: 0.35, max: 4.94, defaultVal: 2.45 },
      { key: 't3', label: 'Total Triiodothyronine (T3)', unit: 'ng/dL', min: 80, max: 200, defaultVal: 130 },
      { key: 't4', label: 'Total Thyroxine (T4)', unit: 'µg/dL', min: 5.1, max: 14.1, defaultVal: 8.8 }
    ]
  },
  {
    id: 'hba1c',
    name: 'HbA1c (Glycated Hemoglobin)',
    category: 'Diabetes Care',
    price: 450,
    sampleType: 'EDTA Whole Blood (2ml)',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Gold-standard biomarker reflecting average glycemic control over the past 90 days.',
    parameters: [
      { key: 'hba1c_pct', label: 'HbA1c', unit: '%', min: 4.0, max: 5.6, defaultVal: 5.4 },
      { key: 'eag', label: 'Estimated Average Glucose', unit: 'mg/dL', min: 70, max: 115, defaultVal: 108 }
    ]
  },
  {
    id: 'lft',
    name: 'Liver Function Test (LFT)',
    category: 'Biochemistry',
    price: 750,
    sampleType: 'Serum (Gold Top Tube)',
    turnaround: '8 Hours',
    fasting: true,
    fastingHours: 8,
    description: 'Evaluates hepatic enzyme activity, protein synthesis, and bilirubin clearance.',
    parameters: [
      { key: 'sgot', label: 'SGOT / AST', unit: 'U/L', min: 5, max: 40, defaultVal: 26 },
      { key: 'sgpt', label: 'SGPT / ALT', unit: 'U/L', min: 7, max: 56, defaultVal: 32 },
      { key: 'bili_tot', label: 'Bilirubin Total', unit: 'mg/dL', min: 0.2, max: 1.2, defaultVal: 0.8 },
      { key: 'alp', label: 'Alkaline Phosphatase (ALP)', unit: 'U/L', min: 44, max: 147, defaultVal: 95 },
      { key: 'protein', label: 'Total Protein', unit: 'g/dL', min: 6.4, max: 8.3, defaultVal: 7.2 }
    ]
  },
  {
    id: 'kft',
    name: 'Renal / Kidney Function Test (KFT)',
    category: 'Biochemistry',
    price: 600,
    sampleType: 'Serum (Gold Top Tube)',
    turnaround: '6 Hours',
    fasting: false,
    description: 'Evaluates glomerular filtration, serum creatinine, urea, and electrolyte balance.',
    parameters: [
      { key: 'creat', label: 'Serum Creatinine', unit: 'mg/dL', min: 0.6, max: 1.2, defaultVal: 0.9 },
      { key: 'bun', label: 'Blood Urea Nitrogen (BUN)', unit: 'mg/dL', min: 7, max: 20, defaultVal: 14 },
      { key: 'uric', label: 'Uric Acid', unit: 'mg/dL', min: 3.5, max: 7.2, defaultVal: 5.2 }
    ]
  },
  {
    id: 'vitd_b12',
    name: 'Vitamin D & B12 Vitality Duo',
    category: 'Wellness',
    price: 1100,
    sampleType: 'Serum (Gold Top Tube)',
    turnaround: '12 Hours',
    fasting: false,
    description: 'Screens for bone mineralization, metabolic fatigue, and peripheral nervous system health.',
    parameters: [
      { key: 'vit_d', label: 'Vitamin D (25-OH)', unit: 'ng/mL', min: 30, max: 100, defaultVal: 34 },
      { key: 'vit_b12', label: 'Vitamin B12', unit: 'pg/mL', min: 211, max: 911, defaultVal: 480 }
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
  { id: 'phleb-1', name: 'Kiran Kumar', phone: '+91 98450 12345', activePickups: 2 },
  { id: 'phleb-2', name: 'Priya Sharma', phone: '+91 98450 67890', activePickups: 1 },
  { id: 'phleb-3', name: 'Arun Varma', phone: '+91 98450 54321', activePickups: 3 }
];

const TECHNICIANS = [
  { id: 'tech-1', name: 'Dr. Arvind Rao (Lab Director)', role: 'technician' },
  { id: 'tech-2', name: 'Rohan Deshmukh (Lab Technologist)', role: 'technician' }
];

const DEFAULT_ORDERS = [
  {
    id: 'LL-2026-8941',
    patientName: 'Nithin T',
    patientAge: 21,
    patientGender: 'Male',
    patientPhone: '+91 98765 43210',
    patientEmail: 'nithin@labline.com',
    testIds: ['cbc', 'lipid'],
    testNames: ['Complete Blood Count (CBC)', 'Lipid Profile (Complete)'],
    type: 'Home Pickup',
    address: '#142, 4th Cross, Malleshwaram, Bangalore - 560003',
    date: '2026-08-30',
    timeSlot: '07:30 AM - 08:30 AM',
    totalAmount: 1000,
    paymentStatus: 'Paid',
    paymentMethod: 'UPI / Razorpay',
    transactionId: 'pay_NITHIN2026_8941',
    status: 'Processing',
    currentStage: 'Processing',
    phlebotomist: 'Kiran Kumar',
    technician: 'Rohan Deshmukh',
    urgency: 'Routine',
    sampleTubeBarcode: 'BC89410982',
    timestamps: {
      booked: '2026-08-30 08:15 AM',
      collected: '2026-08-30 09:30 AM',
      inTransit: '2026-08-30 10:15 AM',
      processing: '2026-08-30 11:00 AM',
      completed: null
    },
    results: {
      hb: 14.2,
      wbc: 7600,
      rbc: 5.1,
      plt: 2.8,
      pcv: 44.2,
      chol: 218, // Slightly elevated to display out-of-range flag & diet advice
      tg: 165,
      hdl: 46,
      ldl: 112,
      vldl: 26
    },
    dietAdvice: [
      {
        category: 'Foods to Increase',
        items: ['Soluble fiber sources: oats, barley, chia seeds, and fresh apples', 'Healthy unsaturated fats: almonds, walnuts, and cold-pressed olive oil', 'Antioxidant-rich leafy greens and steamed vegetables']
      },
      {
        category: 'Foods to Moderate / Avoid',
        items: ['Deep-fried foods, commercially baked snacks, and trans-fats', 'High-sugar carbonated beverages and refined carbohydrate products']
      },
      {
        category: 'Lifestyle Recommendation',
        items: ['30 minutes of brisk walking or moderate aerobic exercise 5 days/week', 'Maintain adequate hydration (2.5 - 3.0 Liters daily)']
      }
    ]
  },
  {
    id: 'LL-2026-8942',
    patientName: 'Ananya Rao',
    patientAge: 28,
    patientGender: 'Female',
    patientPhone: '+91 98441 22334',
    patientEmail: 'ananya@example.com',
    testIds: ['thyroid', 'vitd_b12'],
    testNames: ['Thyroid Function Test (TFT)', 'Vitamin D & B12 Vitality Duo'],
    type: 'Home Pickup',
    address: '#78, Indiranagar 100ft Road, Bangalore - 560038',
    date: '2026-08-30',
    timeSlot: '08:30 AM - 09:30 AM',
    totalAmount: 1650,
    paymentStatus: 'Paid',
    paymentMethod: 'Credit Card',
    transactionId: 'pay_ANANYA2026_8942',
    status: 'Sample Collected',
    currentStage: 'Sample Collected',
    phlebotomist: 'Priya Sharma',
    technician: 'Dr. Arvind Rao',
    urgency: 'Routine',
    sampleTubeBarcode: 'BC89429184',
    timestamps: {
      booked: '2026-08-30 08:45 AM',
      collected: '2026-08-30 10:30 AM',
      inTransit: null,
      processing: null,
      completed: null
    },
    results: {}
  },
  {
    id: 'LL-2026-8940',
    patientName: 'Rahul Verma',
    patientAge: 45,
    patientGender: 'Male',
    patientPhone: '+91 97412 88990',
    patientEmail: 'rahul.verma@example.com',
    testIds: ['hba1c', 'kft'],
    testNames: ['HbA1c (Glycated Hemoglobin)', 'Renal / Kidney Function Test (KFT)'],
    type: 'Lab Visit',
    address: 'LabLine Central Laboratory, Bangalore',
    date: '2026-08-30',
    timeSlot: '09:00 AM - 10:00 AM',
    totalAmount: 1050,
    paymentStatus: 'Paid',
    paymentMethod: 'UPI',
    transactionId: 'pay_RAHUL2026_8940',
    status: 'Report Generated',
    currentStage: 'Report Generated',
    phlebotomist: 'Central Lab Station #2',
    technician: 'Rohan Deshmukh',
    urgency: 'STAT',
    sampleTubeBarcode: 'BC89401726',
    timestamps: {
      booked: '2026-08-30 07:00 AM',
      collected: '2026-08-30 07:45 AM',
      inTransit: '2026-08-30 08:00 AM',
      processing: '2026-08-30 08:30 AM',
      completed: '2026-08-30 09:45 AM'
    },
    results: {
      hba1c_pct: 6.2,
      eag: 131,
      creat: 1.0,
      bun: 16,
      uric: 5.8
    },
    dietAdvice: [
      {
        category: 'Foods to Increase',
        items: ['Low glycemic whole grains (Quinoa, steel-cut oats, millets)', 'Bitter gourd, fenugreek seeds, and high-fiber raw vegetable salads']
      },
      {
        category: 'Foods to Moderate',
        items: ['Table sugar, sweets, packaged juices, and refined flour']
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
        name: 'Nithin T',
        email: 'nithin@labline.com',
        role: 'patient',
        token: 'mock_jwt_token_nithin_2026'
      };
    }
    return JSON.parse(data);
  },

  setCurrentUser(user) {
    localStorage.setItem('labline_user', JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem('labline_user');
    window.location.href = window.location.pathname.includes('/patient/') || 
                           window.location.pathname.includes('/admin/') || 
                           window.location.pathname.includes('/technician/') 
                           ? '../index.html' 
                           : 'index.html';
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
    ? `<svg class="w-4 h-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>`
    : type === 'error'
    ? `<svg class="w-4 h-4 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`
    : `<svg class="w-4 h-4 text-teal-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`;

  toast.innerHTML = `
    ${iconSvg}
    <div class="flex-1 text-xs font-medium leading-snug">${message}</div>
    <button onclick="this.parentElement.remove()" class="text-slate-400 hover:text-white shrink-0">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.2s ease';
    setTimeout(() => toast.remove(), 220);
  }, 3500);
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
    pct = 22 + ((val - minVal) / rangeSpan) * 56;
    pct = Math.max(5, Math.min(95, pct));
  }

  if (val > maxVal * 1.35) {
    return { status: 'CRITICAL_HIGH', label: 'Critical High', cssClass: 'badge-critical', markerPct: pct };
  } else if (val > maxVal) {
    return { status: 'HIGH', label: 'High', cssClass: 'badge-high', markerPct: pct };
  } else if (val < minVal) {
    return { status: 'LOW', label: 'Low', cssClass: 'badge-low', markerPct: pct };
  } else {
    return { status: 'NORMAL', label: 'Normal', cssClass: 'badge-normal', markerPct: pct };
  }
}

function generateDietAdviceForResults(results, testList) {
  const suggestions = [];

  if (results.chol > 200 || results.tg > 150) {
    suggestions.push({
      category: 'Cardiovascular & Lipid Balance',
      items: [
        'Incorporate soluble fiber: oats, chia seeds, lentils, and apples.',
        'Replace saturated fats (butter, palm oil) with polyunsaturated fats (walnuts, almonds, olive oil).',
        'Limit trans-fats, processed bakery items, and deep-fried snacks.'
      ]
    });
  }

  if ((results.hba1c_pct && results.hba1c_pct > 5.7) || (results.eag && results.eag > 115)) {
    suggestions.push({
      category: 'Glycemic Regulation',
      items: [
        'Choose low glycemic-index complex carbohydrates (millets, quinoa, steel-cut oats).',
        'Avoid sugar-sweetened beverages, commercial sodas, and refined flour.',
        'Walk 15 minutes post-meals to support insulin sensitivity.'
      ]
    });
  }

  if (results.hb && results.hb < 13.0) {
    suggestions.push({
      category: 'Hemoglobin & Iron Support',
      items: [
        'Include iron-rich foods: spinach, beetroots, pomegranates, and dates.',
        'Pair iron sources with Vitamin C (lemon, amla, oranges) to optimize bio-availability.'
      ]
    });
  }

  if (suggestions.length === 0) {
    suggestions.push({
      category: 'Nutritional Maintenance',
      items: [
        'Maintain balanced plate: 50% fresh vegetables, 25% lean protein, 25% whole grains.',
        'Drink 2.5 - 3.0 liters of clean water daily for metabolic hydration.',
        'Continue regular 30-minute moderate physical exercise.'
      ]
    });
  }

  return suggestions;
}

window.LabStore = LabStore;
window.showToast = showToast;
window.evaluateParameter = evaluateParameter;
window.generateDietAdviceForResults = generateDietAdviceForResults;
window.STAGES = STAGES;
window.PHLEBOTOMISTS = PHLEBOTOMISTS;
window.TECHNICIANS = TECHNICIANS;
