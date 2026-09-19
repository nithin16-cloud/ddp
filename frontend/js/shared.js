/**
 * LabLine — Enterprise Diagnostic Portal & Laboratory Management System
 * Shared Clinical Data Models, LocalStorage Store, and Analytical Helpers
 */

/**
 * Central API base URL — change this ONE value when deploying to production.
 * Local dev:   http://127.0.0.1:8000
 * Production:  https://api.yourdomain.com  (or wherever uvicorn is hosted)
 *
 * To override without editing this file, set:
 *   <script>window.LABLINE_API_BASE = 'https://api.yourdomain.com';</script>
 *   before loading shared.js in your HTML.
 */
window.LABLINE_API_BASE = window.LABLINE_API_BASE || 'http://127.0.0.1:8000';

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
  },
  {
    id: 'fbs_ppbs',
    name: 'Blood Glucose Duo (Fasting & PPBS)',
    category: 'Diabetes Care',
    price: 250,
    sampleType: 'Fluoride Plasma (Grey Top Vacutainer)',
    tubeCapClass: 'tube-cap-fluoride',
    turnaround: '2 Hours',
    fasting: true,
    fastingHours: 10,
    description: 'Gold standard dual evaluation of basal fasting blood sugar and post-prandial glycemic excursions for diabetes mellitus diagnosis.',
    parameters: [
      { key: 'fbs', label: 'Fasting Blood Glucose (FBS)', unit: 'mg/dL', min: 70.0, max: 99.0, defaultVal: 88.0 },
      { key: 'ppbs', label: 'Post-Prandial Glucose (PPBS)', unit: 'mg/dL', min: 70.0, max: 140.0, defaultVal: 118.0 }
    ]
  },
  {
    id: 'crp',
    name: 'C-Reactive Protein (Quantitative & hs-CRP)',
    category: 'Immunology',
    price: 480,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '4 Hours',
    fasting: false,
    description: 'High-sensitivity acute-phase reactant quantifying systemic inflammation, bacterial infection severity, and atherothrombotic risk.',
    parameters: [
      { key: 'crp_val', label: 'C-Reactive Protein (Quantitative)', unit: 'mg/L', min: 0.0, max: 5.0, defaultVal: 1.4 },
      { key: 'hs_crp', label: 'High Sensitivity hs-CRP (Cardiac)', unit: 'mg/L', min: 0.0, max: 1.0, defaultVal: 0.6 }
    ]
  },
  {
    id: 'urine_re',
    name: 'Urine Routine & Microscopic Examination (CUE)',
    category: 'Clinical Pathology',
    price: 220,
    sampleType: 'Midstream Clean Catch Urine (15ml)',
    tubeCapClass: 'tube-cap-urine',
    turnaround: '2 Hours',
    fasting: false,
    description: 'Comprehensive physical, chemical, and microscopic examination for urinary tract infections (UTI), proteinuria, microhematuria, and renal casts.',
    parameters: [
      { key: 'urine_ph', label: 'Urine pH Reaction', unit: 'pH', min: 4.8, max: 7.5, defaultVal: 6.2 },
      { key: 'urine_sp_gr', label: 'Specific Gravity', unit: 'ratio', min: 1.005, max: 1.030, defaultVal: 1.018 },
      { key: 'urine_pus', label: 'Pus Cells (Leukocytes)', unit: '/HPF', min: 0.0, max: 5.0, defaultVal: 1.0 },
      { key: 'urine_rbc', label: 'Red Blood Cells (RBC)', unit: '/HPF', min: 0.0, max: 2.0, defaultVal: 0.0 },
      { key: 'urine_alb', label: 'Protein / Albumin (Qualitative)', unit: 'mg/dL', min: 0.0, max: 15.0, defaultVal: 0.0 }
    ]
  },
  {
    id: 'electrolytes',
    name: 'Serum Electrolytes Panel (Na / K / Cl / HCO3)',
    category: 'Biochemistry',
    price: 520,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '3 Hours',
    fasting: false,
    description: 'Measures vital extracellular and intracellular ions to evaluate cellular dehydration, renal tubular acidosis, hypertension, and arrhythmia.',
    parameters: [
      { key: 'na', label: 'Serum Sodium (Na+)', unit: 'mEq/L', min: 136.0, max: 145.0, defaultVal: 140.0 },
      { key: 'k', label: 'Serum Potassium (K+)', unit: 'mEq/L', min: 3.5, max: 5.1, defaultVal: 4.2 },
      { key: 'cl', label: 'Serum Chloride (Cl-)', unit: 'mEq/L', min: 96.0, max: 106.0, defaultVal: 101.0 },
      { key: 'hco3', label: 'Serum Bicarbonate (HCO3-)', unit: 'mEq/L', min: 22.0, max: 29.0, defaultVal: 24.5 }
    ]
  },
  {
    id: 'esr',
    name: 'Erythrocyte Sedimentation Rate (ESR - Westergren)',
    category: 'Hematology',
    price: 180,
    sampleType: 'Sodium Citrate Whole Blood (1.6ml)',
    tubeCapClass: 'tube-cap-citrate',
    turnaround: '2 Hours',
    fasting: false,
    description: 'Gold-standard Westergren automated kinetic measurement of red cell sedimentation indicating occult inflammation, infection, or connective tissue disease.',
    parameters: [
      { key: 'esr_val', label: 'ESR (1st Hour - Westergren)', unit: 'mm/hr', min: 0.0, max: 20.0, defaultVal: 9.0 }
    ]
  },
  {
    id: 'iron_profile',
    name: 'Iron Deficiency & Ferritin Profile',
    category: 'Hematology',
    price: 850,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '6 Hours',
    fasting: true,
    fastingHours: 10,
    description: 'Comprehensive investigation of iron metabolism, measuring serum ferritin storage pools, circulating iron, and transferrin saturation to evaluate microcytic anemia.',
    parameters: [
      { key: 'ferritin', label: 'Serum Ferritin', unit: 'ng/mL', min: 20.0, max: 250.0, defaultVal: 95.0 },
      { key: 'iron', label: 'Total Serum Iron', unit: 'µg/dL', min: 60.0, max: 170.0, defaultVal: 105.0 },
      { key: 'tibc', label: 'Total Iron Binding Capacity (TIBC)', unit: 'µg/dL', min: 250.0, max: 425.0, defaultVal: 310.0 },
      { key: 'transferrin_sat', label: 'Transferrin Saturation Index', unit: '%', min: 20.0, max: 50.0, defaultVal: 32.0 }
    ]
  },
  {
    id: 'dengue',
    name: 'Dengue Duo Serology (NS1 Antigen & IgM/IgG)',
    category: 'Infectious Disease',
    price: 750,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '3 Hours',
    fasting: false,
    description: 'Rapid immuno-assay detecting early Dengue virus NS1 antigen (Day 1-5 pyrexia) alongside differential IgM and IgG antibodies for acute or secondary infection.',
    parameters: [
      { key: 'dengue_ns1', label: 'Dengue NS1 Antigen (Early)', unit: 'Index', min: 0.0, max: 0.9, defaultVal: 0.2 },
      { key: 'dengue_igm', label: 'Dengue IgM Antibodies (Acute)', unit: 'Index', min: 0.0, max: 0.9, defaultVal: 0.3 },
      { key: 'dengue_igg', label: 'Dengue IgG Antibodies (Past/Secondary)', unit: 'Index', min: 0.0, max: 0.9, defaultVal: 0.2 }
    ]
  },
  {
    id: 'typhoid',
    name: 'Typhoid Fever Serology (Widal & Typhidot)',
    category: 'Infectious Disease',
    price: 420,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Evaluates agglutinating antibodies against Salmonella enterica serovars Typhi and Paratyphi for enteric fever diagnosis in prolonged fever.',
    parameters: [
      { key: 'typhi_o', label: "S. Typhi 'O' Antigen Titer", unit: 'Titer', min: 0.0, max: 80.0, defaultVal: 40.0 },
      { key: 'typhi_h', label: "S. Typhi 'H' Antigen Titer", unit: 'Titer', min: 0.0, max: 80.0, defaultVal: 40.0 }
    ]
  },
  {
    id: 'troponin',
    name: 'Cardiac Troponin-I (High Sensitivity hs-cTnI)',
    category: 'Cardiology',
    price: 1200,
    sampleType: 'EDTA Whole Blood (2ml)',
    tubeCapClass: 'tube-cap-edta',
    turnaround: '1 Hour (STAT)',
    fasting: false,
    description: 'Definitive emergency biomarker of myocardial injury and myocardial necrosis in acute coronary syndrome (ACS), unstable angina, and acute chest pain.',
    parameters: [
      { key: 'troponin_i', label: 'High Sensitivity Troponin-I', unit: 'ng/L', min: 0.0, max: 15.6, defaultVal: 3.8 }
    ]
  },
  {
    id: 'coagulation',
    name: 'Coagulation Profile (PT / INR & APTT)',
    category: 'Hematology',
    price: 580,
    sampleType: 'Sodium Citrate (Light Blue Top 2.7ml)',
    tubeCapClass: 'tube-cap-citrate',
    turnaround: '3 Hours',
    fasting: false,
    description: 'Essential screen of extrinsic and intrinsic coagulation pathways, prothrombin time, international normalized ratio, and anticoagulant therapy monitoring.',
    parameters: [
      { key: 'pt', label: 'Prothrombin Time (PT)', unit: 'Seconds', min: 11.0, max: 14.5, defaultVal: 12.2 },
      { key: 'inr', label: 'International Normalized Ratio (INR)', unit: 'ratio', min: 0.85, max: 1.15, defaultVal: 1.02 },
      { key: 'aptt', label: 'Activated Partial Thromboplastin Time (APTT)', unit: 'Seconds', min: 26.0, max: 38.0, defaultVal: 30.5 }
    ]
  },
  {
    id: 'calcium_phosphorus',
    name: 'Calcium & Phosphorus Bone Mineral Panel',
    category: 'Biochemistry',
    price: 450,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Evaluates mineral homeostasis, ionized calcium fractions, neuromuscular tetany, bone resorption, and parathyroid endocrine function.',
    parameters: [
      { key: 'calcium', label: 'Total Serum Calcium', unit: 'mg/dL', min: 8.6, max: 10.2, defaultVal: 9.4 },
      { key: 'ionized_ca', label: 'Ionized Free Calcium', unit: 'mmol/L', min: 1.12, max: 1.32, defaultVal: 1.21 },
      { key: 'phosphorus', label: 'Serum Inorganic Phosphorus', unit: 'mg/dL', min: 2.5, max: 4.5, defaultVal: 3.6 }
    ]
  },
  {
    id: 'pancreatic',
    name: 'Pancreatic Enzymes (Amylase & Lipase)',
    category: 'Biochemistry',
    price: 780,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Highly specific enzymatic duo for rapid clinical diagnosis of acute pancreatitis, pancreatic pseudocysts, and acute epigastric distress.',
    parameters: [
      { key: 'amylase', label: 'Serum Amylase', unit: 'U/L', min: 28.0, max: 100.0, defaultVal: 62.0 },
      { key: 'lipase', label: 'Serum Lipase (Pancreatic Specific)', unit: 'U/L', min: 13.0, max: 60.0, defaultVal: 31.0 }
    ]
  },
  {
    id: 'urine_microalbumin',
    name: 'Urine Microalbumin & Creatinine Ratio (ACR)',
    category: 'Renal & Urology',
    price: 620,
    sampleType: 'Early Morning Spot Urine',
    tubeCapClass: 'tube-cap-urine',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Early screening biomarker for diabetic nephropathy and microvascular renal endothelial injury prior to overt macroalbuminuria.',
    parameters: [
      { key: 'microalbumin', label: 'Spot Urine Microalbumin', unit: 'mg/L', min: 0.0, max: 20.0, defaultVal: 8.5 },
      { key: 'urine_creat', label: 'Urine Creatinine', unit: 'mg/dL', min: 20.0, max: 275.0, defaultVal: 110.0 },
      { key: 'acr_ratio', label: 'Albumin-to-Creatinine Ratio (ACR)', unit: 'mg/g', min: 0.0, max: 30.0, defaultVal: 12.0 }
    ]
  },
  {
    id: 'psa',
    name: 'Prostate Specific Antigen (Total PSA)',
    category: 'Oncology & Urology',
    price: 750,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '6 Hours',
    fasting: false,
    description: 'Immunoassay assessing prostatic kallikrein-3 glycoprotein for male screening, benign prostatic hyperplasia (BPH), and prostate adenocarcinoma.',
    parameters: [
      { key: 'psa_total', label: 'Total Serum PSA', unit: 'ng/mL', min: 0.0, max: 4.0, defaultVal: 1.45 }
    ]
  },
  {
    id: 'rheumatoid',
    name: 'Rheumatoid Arthritis Panel (RF & Anti-CCP)',
    category: 'Immunology',
    price: 1150,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '8 Hours',
    fasting: false,
    description: 'High-specificity autoimmune antibody screening combining quantitative Rheumatoid Factor with Anti-Cyclic Citrullinated Peptide to confirm early erosive RA.',
    parameters: [
      { key: 'rf_val', label: 'Rheumatoid Factor (RF Quantitative)', unit: 'IU/mL', min: 0.0, max: 14.0, defaultVal: 7.2 },
      { key: 'anti_ccp', label: 'Anti-CCP (Cyclic Citrullinated Peptide)', unit: 'U/mL', min: 0.0, max: 17.0, defaultVal: 5.1 }
    ]
  },
  {
    id: 'uric_acid',
    name: 'Serum Uric Acid (Gout & Hyperuricemia Panel)',
    category: 'Biochemistry',
    price: 260,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '2 Hours',
    fasting: false,
    description: 'Measures end-product purine catabolism to diagnose acute gouty monoarthritis, tophi formation, and uric acid renal lithiasis.',
    parameters: [
      { key: 'uric_val', label: 'Serum Uric Acid', unit: 'mg/dL', min: 3.5, max: 7.2, defaultVal: 4.8 }
    ]
  },
  {
    id: 'viral_screen',
    name: 'Viral Screening Tri-Panel (HIV, HBsAg, HCV)',
    category: 'Infectious Disease',
    price: 950,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '6 Hours',
    fasting: false,
    description: 'High-affinity 4th-generation ELISA screening for Human Immunodeficiency Virus, Hepatitis B surface antigen, and Hepatitis C antibody for pre-op clearance.',
    parameters: [
      { key: 'hiv', label: 'HIV 1 & 2 Antigen-Antibody Duo', unit: 'Index', min: 0.0, max: 0.9, defaultVal: 0.12 },
      { key: 'hbsag', label: 'Hepatitis B Surface Antigen (HBsAg)', unit: 'Index', min: 0.0, max: 0.9, defaultVal: 0.15 },
      { key: 'hcv', label: 'Hepatitis C Antibody (Anti-HCV)', unit: 'Index', min: 0.0, max: 0.9, defaultVal: 0.14 }
    ]
  },
  {
    id: 'cardiac_risk',
    name: 'Advanced Cardiac Biomarkers (Homocysteine & Apo-B)',
    category: 'Cardiology',
    price: 1450,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '8 Hours',
    fasting: true,
    fastingHours: 12,
    description: 'Comprehensive secondary cardiovascular risk panel assessing serum homocysteine, atherogenic Apolipoprotein B particles, and Lipoprotein(a).',
    parameters: [
      { key: 'homocysteine', label: 'Serum Total Homocysteine', unit: 'µmol/L', min: 5.0, max: 15.0, defaultVal: 9.8 },
      { key: 'apob', label: 'Apolipoprotein B (Apo-B)', unit: 'mg/dL', min: 55.0, max: 125.0, defaultVal: 82.0 },
      { key: 'lp_a', label: 'Lipoprotein (a) [Lp(a)]', unit: 'nmol/L', min: 0.0, max: 75.0, defaultVal: 28.0 }
    ]
  },
  {
    id: 'allergy_ige',
    name: 'Total Serum IgE (Allergy & Atopy Screen)',
    category: 'Immunology',
    price: 650,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '4 Hours',
    fasting: false,
    description: 'Assesses total circulating immunoglobulin E reaginic antibodies for diagnosis and therapeutic monitoring of atopic asthma, allergic rhinitis, and urticaria.',
    parameters: [
      { key: 'ige_total', label: 'Total Serum IgE', unit: 'IU/mL', min: 0.0, max: 100.0, defaultVal: 42.0 }
    ]
  },
  {
    id: 'beta_hcg',
    name: 'Total Beta-hCG (Quantitative Pregnancy Marker)',
    category: 'Endocrinology',
    price: 490,
    sampleType: 'Serum (Gold Top SST)',
    tubeCapClass: 'tube-cap-serum',
    turnaround: '2 Hours',
    fasting: false,
    description: 'Chemiluminescent quantitative assessment of beta-subunit Human Chorionic Gonadotropin for early pregnancy confirmation, viability, and gestational dating.',
    parameters: [
      { key: 'hcg_val', label: 'Total Beta-hCG (Serum)', unit: 'mIU/mL', min: 0.0, max: 5.0, defaultVal: 1.1 }
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
    try {
      const stored = JSON.parse(data);
      if (Array.isArray(stored) && stored.length < DEFAULT_TESTS.length) {
        const storedIds = new Set(stored.map(t => t.id));
        const missing = DEFAULT_TESTS.filter(t => !storedIds.has(t.id));
        const merged = [...stored, ...missing];
        localStorage.setItem('labline_tests', JSON.stringify(merged));
        return merged;
      }
      return stored;
    } catch (e) {
      localStorage.setItem('labline_tests', JSON.stringify(DEFAULT_TESTS));
      return DEFAULT_TESTS;
    }
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
    // Bug 16 fix: return null instead of orders[0] when order is not found
    // to prevent silently displaying wrong patient data
    return orders.find(o => o.id === orderId) || null;
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
    : type === 'warning'
    // Bug 20/21 fix: add proper amber warning icon for 'warning' type
    ? `<svg class="w-4 h-4 text-amber-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.2" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`
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
  // Bug 15 fix: canonical format must match Python backend generate_report_hash().
  // Python format: "key:value.2f:flag" — the status_flag MUST be included.
  // Previously JS only included "key:value" which caused permanent hash mismatch.
  const resultsObj = simulatedResults || order.results || {};
  const tests = LabStore.getTests();
  const testMap = new Map(tests.map(t => [t.id, t]));

  // Build parameter key → {min, max} for status flag computation
  const paramRefMap = {};
  tests.forEach(test => {
    (test.parameters || []).forEach(p => {
      paramRefMap[p.key] = { min: p.min, max: p.max };
    });
  });

  const sortedKeys = Object.keys(resultsObj).sort();
  const canonicalResults = sortedKeys.map(k => {
    const val = parseFloat(resultsObj[k] || 0);
    const ref = paramRefMap[k];
    let flag = 'Normal';
    if (ref) {
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

  // Bug 18 fix: Count actual existing active assignments per technician
  // before the dispatch loop (matches backend dispatcher logic).
  const loads = {};
  activeTechs.forEach(t => loads[t] = 0);
  orders.forEach(o => {
    if (o.currentStage === 'Report Generated') return;
    activeTechs.forEach(t => {
      if ((o.technician || '').includes(t.split(' ')[0])) {
        loads[t]++;
      }
    });
  });

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

function parsePrescriptionTextClient(rawText) {
  rawText = (rawText || '').trim();
  if (!rawText) return null;

  const allTests = LabStore.getTests();
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
  const testMap = new Map(testsList.map(t => [t.id, t]));
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
window.levenshteinSimilarityClient = levenshteinSimilarityClient;
window.parsePrescriptionTextClient = parsePrescriptionTextClient;
window.getCompanionRecommendationsClient = getCompanionRecommendationsClient;
window.STAGES = STAGES;
window.PHLEBOTOMISTS = PHLEBOTOMISTS;
window.TECHNICIANS = TECHNICIANS;



