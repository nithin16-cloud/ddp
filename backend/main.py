import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
import models  # ensures models are registered before create_all
from routers import (
    auth_router,
    tests_router,
    bookings_router,
    payments_router,
    results_router,
    reports_router,
    analytics_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan handler — replaces deprecated @app.on_event."""
    # Automatically create all tables in MySQL if they do not exist
    Base.metadata.create_all(bind=engine)
    _seed_initial_data()
    yield


app = FastAPI(
    title="LabLine Healthcare Diagnostic API",
    description="Backend REST API for LabLine Specimen & Diagnostic Management Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — development fallback origins (always allowed in any environment)
_DEV_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Production origins come from env vars — no code change needed on deployment.
# Set FRONTEND_BASE_URL=https://yourdomain.com
# Or ALLOWED_ORIGINS=https://app.yourdomain.com,https://www.yourdomain.com (CSV)
# WARNING: never set allow_origins=["*"] when allow_credentials=True — browsers block it.
_extra_origins: list[str] = []

_frontend_base = os.getenv("FRONTEND_BASE_URL", "").strip()
if _frontend_base:
    _extra_origins.append(_frontend_base)

_allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "").strip()
if _allowed_origins_env:
    for _o in _allowed_origins_env.split(","):
        _o = _o.strip()
        if _o and _o not in _extra_origins:
            _extra_origins.append(_o)

allowed_origins = list(dict.fromkeys(_DEV_ORIGINS + _extra_origins))  # deduplicated, insertion-ordered

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all 7 core modules
app.include_router(auth_router.router)
app.include_router(tests_router.router)
app.include_router(bookings_router.router)
app.include_router(payments_router.router)
app.include_router(results_router.router)
app.include_router(reports_router.router)
app.include_router(analytics_router.router)


def _seed_initial_data():
    """Ensure essential tests, schema columns, and phlebotomists exist in the database."""
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            res = conn.execute(text("DESCRIBE bookings"))
            cols = [r[0] for r in res.fetchall()]
            if "report_hash" not in cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN report_hash VARCHAR(64) NULL AFTER technician_notes"))
            if "is_certified" not in cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN is_certified BOOLEAN DEFAULT 0 AFTER report_hash"))
            if "certified_at" not in cols:
                conn.execute(text("ALTER TABLE bookings ADD COLUMN certified_at VARCHAR(40) NULL AFTER is_certified"))
            conn.commit()
        except Exception as ex:
            print("Schema migration notice:", ex)

    db: Session = SessionLocal()
    try:
        # Check phlebotomists
        if db.query(models.Phlebotomist).count() == 0:
            sample_phlebs = [
                models.Phlebotomist(id="PHL-01", name="Rupesh Patel", phone="+91 98451 22341", active_pickups=2, rating=4.9),
                models.Phlebotomist(id="PHL-02", name="Varshith Gowda", phone="+91 98451 33452", active_pickups=1, rating=4.8),
                models.Phlebotomist(id="PHL-03", name="Yatish Shetty", phone="+91 98451 44563", active_pickups=0, rating=4.9),
            ]
            db.add_all(sample_phlebs)
            db.commit()

        # Check and seed all diagnostic catalog tests and parameters
        existing_test_ids = {t.id for t in db.query(models.Test.id).all()}

        catalog_data = [
            {
                "id": "cbc",
                "name": "Complete Blood Count (CBC)",
                "category": "Hematology",
                "price": 350.0,
                "sample_type": "EDTA Whole Blood (2ml)",
                "tube_cap_class": "tube-cap-edta",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Evaluates cellular health and screens for anemia, infections, and platelet disorders.",
                "params": [
                    ("hb", "Hemoglobin", "g/dL", 13.0, 17.0, 14.2),
                    ("wbc", "Total Leukocyte Count (WBC)", "/µL", 4000.0, 11000.0, 7500.0),
                    ("rbc", "Total RBC Count", "million/µL", 4.5, 5.9, 5.1),
                    ("plt", "Platelet Count", "lakh/µL", 1.5, 4.5, 2.8),
                    ("pcv", "Packed Cell Volume (PCV)", "%", 40.0, 50.0, 44.5),
                ]
            },
            {
                "id": "lipid",
                "name": "Lipid Profile (Comprehensive)",
                "category": "Biochemistry",
                "price": 650.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": True,
                "fasting_hours": 12,
                "description": "Measures cholesterol fractions to quantify cardiovascular risk.",
                "params": [
                    ("chol", "Total Cholesterol", "mg/dL", 125.0, 200.0, 185.0),
                    ("tg", "Triglycerides", "mg/dL", 50.0, 150.0, 135.0),
                    ("hdl", "HDL (Good Cholesterol)", "mg/dL", 40.0, 60.0, 48.0),
                    ("ldl", "LDL (Bad Cholesterol)", "mg/dL", 60.0, 100.0, 92.0),
                    ("vldl", "VLDL Cholesterol", "mg/dL", 10.0, 30.0, 24.0),
                ]
            },
            {
                "id": "thyroid",
                "name": "Thyroid Function Panel (TFT)",
                "category": "Endocrinology",
                "price": 550.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Measures TSH, T3, and T4 to assess thyroid function.",
                "params": [
                    ("tsh", "TSH (Ultrasensitive)", "µIU/mL", 0.35, 4.94, 2.45),
                    ("t3", "Total Triiodothyronine (T3)", "ng/dL", 80.0, 200.0, 130.0),
                    ("t4", "Total Thyroxine (T4)", "µg/dL", 5.1, 14.1, 8.8),
                ]
            },
            {
                "id": "hba1c",
                "name": "HbA1c & Estimated Glucose",
                "category": "Diabetes Care",
                "price": 450.0,
                "sample_type": "EDTA Whole Blood (2ml)",
                "tube_cap_class": "tube-cap-edta",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Gold-standard glycated biomarker for 90-day glycemic control.",
                "params": [
                    ("hba1c_pct", "HbA1c (Glycated Hemoglobin)", "%", 4.0, 5.6, 5.4),
                    ("eag", "Estimated Avg Glucose (eAG)", "mg/dL", 70.0, 115.0, 108.0),
                ]
            },
            {
                "id": "lft",
                "name": "Liver Function Panel (LFT)",
                "category": "Biochemistry",
                "price": 750.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "8 Hours",
                "fasting": True,
                "fasting_hours": 8,
                "description": "Evaluates hepatic enzyme kinetics, biliary excretion, and liver protein synthesis.",
                "params": [
                    ("sgot", "SGOT / AST (Transaminase)", "U/L", 5.0, 40.0, 26.0),
                    ("sgpt", "SGPT / ALT (Transaminase)", "U/L", 7.0, 56.0, 32.0),
                    ("bili_tot", "Total Bilirubin", "mg/dL", 0.2, 1.2, 0.8),
                    ("alp", "Alkaline Phosphatase (ALP)", "U/L", 44.0, 147.0, 95.0),
                    ("protein", "Total Serum Protein", "g/dL", 6.4, 8.3, 7.2),
                ]
            },
            {
                "id": "kft",
                "name": "Kidney Function Profile (KFT)",
                "category": "Biochemistry",
                "price": 600.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Evaluates glomerular filtration integrity, serum creatinine clearance, and nitrogenous urea excretion.",
                "params": [
                    ("creat", "Serum Creatinine", "mg/dL", 0.6, 1.2, 0.9),
                    ("bun", "Blood Urea Nitrogen (BUN)", "mg/dL", 7.0, 20.0, 14.0),
                    ("uric", "Serum Uric Acid", "mg/dL", 3.5, 7.2, 5.2),
                ]
            },
            {
                "id": "vitd_b12",
                "name": "Vitamin D & B12 Vitality Duo",
                "category": "Wellness",
                "price": 1100.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "12 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Assesses bone mineralization density, neurological integrity, and cellular metabolic vitality.",
                "params": [
                    ("vit_d", "Vitamin D (25-OH Hydroxy)", "ng/mL", 30.0, 100.0, 34.0),
                    ("vit_b12", "Vitamin B12 (Cyanocobalamin)", "pg/mL", 211.0, 911.0, 480.0),
                ]
            },
            {
                "id": "fbs_ppbs",
                "name": "Blood Glucose Duo (Fasting & PPBS)",
                "category": "Diabetes Care",
                "price": 250.0,
                "sample_type": "Fluoride Plasma (Grey Top Vacutainer)",
                "tube_cap_class": "tube-cap-fluoride",
                "turnaround": "2 Hours",
                "fasting": True,
                "fasting_hours": 10,
                "description": "Gold standard dual evaluation of basal fasting blood sugar and post-prandial glycemic excursions.",
                "params": [
                    ("fbs", "Fasting Blood Glucose (FBS)", "mg/dL", 70.0, 99.0, 88.0),
                    ("ppbs", "Post-Prandial Glucose (PPBS)", "mg/dL", 70.0, 140.0, 118.0),
                ]
            },
            {
                "id": "crp",
                "name": "C-Reactive Protein (Quantitative & hs-CRP)",
                "category": "Immunology",
                "price": 480.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "High-sensitivity acute-phase reactant quantifying systemic inflammation, bacterial infection, and atherothrombotic risk.",
                "params": [
                    ("crp_val", "C-Reactive Protein (Quantitative)", "mg/L", 0.0, 5.0, 1.4),
                    ("hs_crp", "High Sensitivity hs-CRP (Cardiac)", "mg/L", 0.0, 1.0, 0.6),
                ]
            },
            {
                "id": "urine_re",
                "name": "Urine Routine & Microscopic Examination (CUE)",
                "category": "Clinical Pathology",
                "price": 220.0,
                "sample_type": "Midstream Clean Catch Urine (15ml)",
                "tube_cap_class": "tube-cap-urine",
                "turnaround": "2 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Comprehensive physical, chemical, and microscopic examination for UTI, proteinuria, and microhematuria.",
                "params": [
                    ("urine_ph", "Urine pH Reaction", "pH", 4.8, 7.5, 6.2),
                    ("urine_sp_gr", "Specific Gravity", "ratio", 1.005, 1.030, 1.018),
                    ("urine_pus", "Pus Cells (Leukocytes)", "/HPF", 0.0, 5.0, 1.0),
                    ("urine_rbc", "Red Blood Cells (RBC)", "/HPF", 0.0, 2.0, 0.0),
                    ("urine_alb", "Protein / Albumin (Qualitative)", "mg/dL", 0.0, 15.0, 0.0),
                ]
            },
            {
                "id": "electrolytes",
                "name": "Serum Electrolytes Panel (Na / K / Cl / HCO3)",
                "category": "Biochemistry",
                "price": 520.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "3 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Measures vital ions to evaluate dehydration, renal tubular acidosis, hypertension, and arrhythmia.",
                "params": [
                    ("na", "Serum Sodium (Na+)", "mEq/L", 136.0, 145.0, 140.0),
                    ("k", "Serum Potassium (K+)", "mEq/L", 3.5, 5.1, 4.2),
                    ("cl", "Serum Chloride (Cl-)", "mEq/L", 96.0, 106.0, 101.0),
                    ("hco3", "Serum Bicarbonate (HCO3-)", "mEq/L", 22.0, 29.0, 24.5),
                ]
            },
            {
                "id": "esr",
                "name": "Erythrocyte Sedimentation Rate (ESR - Westergren)",
                "category": "Hematology",
                "price": 180.0,
                "sample_type": "Sodium Citrate Whole Blood (1.6ml)",
                "tube_cap_class": "tube-cap-citrate",
                "turnaround": "2 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Automated kinetic measurement of red cell sedimentation indicating occult inflammation or infection.",
                "params": [
                    ("esr_val", "ESR (1st Hour - Westergren)", "mm/hr", 0.0, 20.0, 9.0),
                ]
            },
            {
                "id": "iron_profile",
                "name": "Iron Deficiency & Ferritin Profile",
                "category": "Hematology",
                "price": 850.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": True,
                "fasting_hours": 10,
                "description": "Comprehensive investigation of iron metabolism, serum ferritin storage pools, and transferrin saturation.",
                "params": [
                    ("ferritin", "Serum Ferritin", "ng/mL", 20.0, 250.0, 95.0),
                    ("iron", "Total Serum Iron", "µg/dL", 60.0, 170.0, 105.0),
                    ("tibc", "Total Iron Binding Capacity (TIBC)", "µg/dL", 250.0, 425.0, 310.0),
                    ("transferrin_sat", "Transferrin Saturation Index", "%", 20.0, 50.0, 32.0),
                ]
            },
            {
                "id": "dengue",
                "name": "Dengue Duo Serology (NS1 Antigen & IgM/IgG)",
                "category": "Infectious Disease",
                "price": 750.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "3 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Rapid immuno-assay detecting early Dengue virus NS1 antigen alongside differential IgM and IgG antibodies.",
                "params": [
                    ("dengue_ns1", "Dengue NS1 Antigen (Early)", "Index", 0.0, 0.9, 0.2),
                    ("dengue_igm", "Dengue IgM Antibodies (Acute)", "Index", 0.0, 0.9, 0.3),
                    ("dengue_igg", "Dengue IgG Antibodies (Past/Secondary)", "Index", 0.0, 0.9, 0.2),
                ]
            },
            {
                "id": "typhoid",
                "name": "Typhoid Fever Serology (Widal & Typhidot)",
                "category": "Infectious Disease",
                "price": 420.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Evaluates agglutinating antibodies against Salmonella enterica serovars Typhi and Paratyphi for enteric fever.",
                "params": [
                    ("typhi_o", "S. Typhi 'O' Antigen Titer", "Titer", 0.0, 80.0, 40.0),
                    ("typhi_h", "S. Typhi 'H' Antigen Titer", "Titer", 0.0, 80.0, 40.0),
                ]
            },
            {
                "id": "troponin",
                "name": "Cardiac Troponin-I (High Sensitivity hs-cTnI)",
                "category": "Cardiology",
                "price": 1200.0,
                "sample_type": "EDTA Whole Blood (2ml)",
                "tube_cap_class": "tube-cap-edta",
                "turnaround": "1 Hour (STAT)",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Definitive emergency biomarker of myocardial injury in acute coronary syndrome (ACS) and chest pain.",
                "params": [
                    ("troponin_i", "High Sensitivity Troponin-I", "ng/L", 0.0, 15.6, 3.8),
                ]
            },
            {
                "id": "coagulation",
                "name": "Coagulation Profile (PT / INR & APTT)",
                "category": "Hematology",
                "price": 580.0,
                "sample_type": "Sodium Citrate (Light Blue Top 2.7ml)",
                "tube_cap_class": "tube-cap-citrate",
                "turnaround": "3 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Essential screen of extrinsic and intrinsic coagulation pathways, PT/INR, and anticoagulant therapy monitoring.",
                "params": [
                    ("pt", "Prothrombin Time (PT)", "Seconds", 11.0, 14.5, 12.2),
                    ("inr", "International Normalized Ratio (INR)", "ratio", 0.85, 1.15, 1.02),
                    ("aptt", "Activated Partial Thromboplastin Time (APTT)", "Seconds", 26.0, 38.0, 30.5),
                ]
            },
            {
                "id": "calcium_phosphorus",
                "name": "Calcium & Phosphorus Bone Mineral Panel",
                "category": "Biochemistry",
                "price": 450.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Evaluates mineral homeostasis, ionized calcium fractions, neuromuscular tetany, and parathyroid function.",
                "params": [
                    ("calcium", "Total Serum Calcium", "mg/dL", 8.6, 10.2, 9.4),
                    ("ionized_ca", "Ionized Free Calcium", "mmol/L", 1.12, 1.32, 1.21),
                    ("phosphorus", "Serum Inorganic Phosphorus", "mg/dL", 2.5, 4.5, 3.6),
                ]
            },
            {
                "id": "pancreatic",
                "name": "Pancreatic Enzymes (Amylase & Lipase)",
                "category": "Biochemistry",
                "price": 780.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Specific enzymatic duo for clinical diagnosis of acute pancreatitis and epigastric distress.",
                "params": [
                    ("amylase", "Serum Amylase", "U/L", 28.0, 100.0, 62.0),
                    ("lipase", "Serum Lipase (Pancreatic Specific)", "U/L", 13.0, 60.0, 31.0),
                ]
            },
            {
                "id": "urine_microalbumin",
                "name": "Urine Microalbumin & Creatinine Ratio (ACR)",
                "category": "Renal & Urology",
                "price": 620.0,
                "sample_type": "Early Morning Spot Urine",
                "tube_cap_class": "tube-cap-urine",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Early screening biomarker for diabetic nephropathy and microvascular renal injury.",
                "params": [
                    ("microalbumin", "Spot Urine Microalbumin", "mg/L", 0.0, 20.0, 8.5),
                    ("urine_creat", "Urine Creatinine", "mg/dL", 20.0, 275.0, 110.0),
                    ("acr_ratio", "Albumin-to-Creatinine Ratio (ACR)", "mg/g", 0.0, 30.0, 12.0),
                ]
            },
            {
                "id": "psa",
                "name": "Prostate Specific Antigen (Total PSA)",
                "category": "Oncology & Urology",
                "price": 750.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Immunoassay assessing prostatic PSA for male screening, BPH, and prostate adenocarcinoma.",
                "params": [
                    ("psa_total", "Total Serum PSA", "ng/mL", 0.0, 4.0, 1.45),
                ]
            },
            {
                "id": "rheumatoid",
                "name": "Rheumatoid Arthritis Panel (RF & Anti-CCP)",
                "category": "Immunology",
                "price": 1150.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "8 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "High-specificity autoimmune antibody screening combining RF with Anti-Cyclic Citrullinated Peptide.",
                "params": [
                    ("rf_val", "Rheumatoid Factor (RF Quantitative)", "IU/mL", 0.0, 14.0, 7.2),
                    ("anti_ccp", "Anti-CCP (Cyclic Citrullinated Peptide)", "U/mL", 0.0, 17.0, 5.1),
                ]
            },
            {
                "id": "uric_acid",
                "name": "Serum Uric Acid (Gout & Hyperuricemia Panel)",
                "category": "Biochemistry",
                "price": 260.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "2 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Measures end-product purine catabolism to diagnose acute gouty monoarthritis and hyperuricemia.",
                "params": [
                    ("uric_val", "Serum Uric Acid", "mg/dL", 3.5, 7.2, 4.8),
                ]
            },
            {
                "id": "viral_screen",
                "name": "Viral Screening Tri-Panel (HIV, HBsAg, HCV)",
                "category": "Infectious Disease",
                "price": 950.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "High-affinity ELISA screening for HIV 1/2, Hepatitis B surface antigen, and Hepatitis C antibody.",
                "params": [
                    ("hiv", "HIV 1 & 2 Antigen-Antibody Duo", "Index", 0.0, 0.9, 0.12),
                    ("hbsag", "Hepatitis B Surface Antigen (HBsAg)", "Index", 0.0, 0.9, 0.15),
                    ("hcv", "Hepatitis C Antibody (Anti-HCV)", "Index", 0.0, 0.9, 0.14),
                ]
            },
            {
                "id": "cardiac_risk",
                "name": "Advanced Cardiac Biomarkers (Homocysteine & Apo-B)",
                "category": "Cardiology",
                "price": 1450.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "8 Hours",
                "fasting": True,
                "fasting_hours": 12,
                "description": "Secondary cardiovascular risk panel assessing homocysteine, atherogenic Apo-B, and Lipoprotein(a).",
                "params": [
                    ("homocysteine", "Serum Total Homocysteine", "µmol/L", 5.0, 15.0, 9.8),
                    ("apob", "Apolipoprotein B (Apo-B)", "mg/dL", 55.0, 125.0, 82.0),
                    ("lp_a", "Lipoprotein (a) [Lp(a)]", "nmol/L", 0.0, 75.0, 28.0),
                ]
            },
            {
                "id": "allergy_ige",
                "name": "Total Serum IgE (Allergy & Atopy Screen)",
                "category": "Immunology",
                "price": 650.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Assesses total circulating IgE reaginic antibodies for atopic asthma, allergic rhinitis, and urticaria.",
                "params": [
                    ("ige_total", "Total Serum IgE", "IU/mL", 0.0, 100.0, 42.0),
                ]
            },
            {
                "id": "beta_hcg",
                "name": "Total Beta-hCG (Quantitative Pregnancy Marker)",
                "category": "Endocrinology",
                "price": 490.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "2 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Chemiluminescent quantitative assessment of beta-subunit Human Chorionic Gonadotropin.",
                "params": [
                    ("hcg_val", "Total Beta-hCG (Serum)", "mIU/mL", 0.0, 5.0, 1.1),
                ]
            }
        ]

        for item in catalog_data:
            if item["id"] not in existing_test_ids:
                t = models.Test(
                    id=item["id"],
                    name=item["name"],
                    category=item["category"],
                    price=item["price"],
                    sample_type=item["sample_type"],
                    tube_cap_class=item["tube_cap_class"],
                    turnaround=item["turnaround"],
                    fasting=item["fasting"],
                    fasting_hours=item["fasting_hours"],
                    description=item["description"],
                    is_active=True
                )
                db.add(t)
                db.commit()

                # Add parameters
                for p_key, p_lbl, p_unit, p_min, p_max, p_def in item["params"]:
                    param_obj = models.TestParameter(
                        test_id=item["id"],
                        key=p_key,
                        label=p_lbl,
                        unit=p_unit,
                        min_val=p_min,
                        max_val=p_max,
                        default_val=p_def
                    )
                    db.add(param_obj)
                db.commit()

    finally:
        db.close()


@app.get("/")
def root():
    return {
        "service": "LabLine Diagnostic API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }
