"""
LabLine Initial Database Seeding Service
Ensures catalog tests, parameters, phlebotomists, and single administrator exist,
while guaranteeing all legacy demo accounts and credentials are fully eradicated.
"""
import os
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
from auth import hash_password, verify_password
from config import settings
from utils.logger import logger

def seed_initial_data():
    """Ensure essential tests, schema columns, phlebotomists, and default accounts exist in the database."""
    with engine.connect() as conn:
        try:
            if engine.dialect.name == "mysql":
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
            logger.debug(f"Schema migration check: {ex}")

    db: Session = SessionLocal()
    try:
        # ── TASK 1: Purge obsolete demo accounts and credentials ───────────────────
        old_demo_emails = ["admin@labline.com", "yashasrao@gmail.com", "nithinshetty1166@gmail.com"]
        for old_email in old_demo_emails:
            old_u = db.query(models.User).filter(models.User.email == old_email).first()
            if old_u:
                db.delete(old_u)
        
        # Purge legacy demo names
        demo_names = ["Nitish Kumar", "Varshith Gowda", "Aryan Sharma"]
        for d_name in demo_names:
            legacy_users = db.query(models.User).filter(models.User.name.like(f"%{d_name}%")).all()
            for lu in legacy_users:
                if lu.email not in (settings.ADMIN_EMAIL, settings.TECH_EMAIL):
                    db.delete(lu)
        db.commit()

        # ── TASK 2: Ensure EXACTLY TWO system staff accounts (Admin & Technician) ────
        admin_email = settings.ADMIN_EMAIL
        admin_pass = settings.ADMIN_PASSWORD
        tech_email = settings.TECH_EMAIL
        tech_pass = settings.TECH_PASSWORD

        # 1. Administrator Account
        admin_user = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin_user:
            admin_user = models.User(
                name="System Administrator",
                email=admin_email,
                hashed_password=hash_password(admin_pass),
                role=models.UserRole.admin,
                phone="+91 98450 11223",
                station="Central Diagnostic Laboratory"
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Provisioned administrator account for {admin_email}.")
        else:
            admin_user.role = models.UserRole.admin
            admin_user.name = "System Administrator"
            if not verify_password(admin_pass, admin_user.hashed_password):
                admin_user.hashed_password = hash_password(admin_pass)
            db.commit()

        # 2. Technician Account
        tech_user = db.query(models.User).filter(models.User.email == tech_email).first()
        if not tech_user:
            tech_user = models.User(
                name="Lead Technologist (Yashas)",
                email=tech_email,
                hashed_password=hash_password(tech_pass),
                role=models.UserRole.technician,
                phone="+91 98450 44556",
                station="Station 1 - Central Diagnostics & Hematology"
            )
            db.add(tech_user)
            db.commit()
            logger.info(f"Provisioned technician account for {tech_email}.")
        else:
            tech_user.role = models.UserRole.technician
            tech_user.name = "Lead Technologist (Yashas)"
            if not verify_password(tech_pass, tech_user.hashed_password):
                tech_user.hashed_password = hash_password(tech_pass)
            db.commit()

        # Ensure single admin: delete any other administrator accounts
        other_admins = db.query(models.User).filter(
            models.User.role == models.UserRole.admin,
            models.User.email != admin_email
        ).all()
        for oa in other_admins:
            db.delete(oa)

        # Ensure single technician: delete any other technician accounts
        other_techs = db.query(models.User).filter(
            models.User.role == models.UserRole.technician,
            models.User.email != tech_email
        ).all()
        for ot in other_techs:
            db.delete(ot)

        db.commit()

        # Check phlebotomists
        if db.query(models.Phlebotomist).count() == 0:
            sample_phlebs = [
                models.Phlebotomist(id="PHL-01", name="Rupesh Patel", phone="+91 98451 22341", active_pickups=2, rating=4.9),
                models.Phlebotomist(id="PHL-02", name="Vijay Nair", phone="+91 98451 33452", active_pickups=1, rating=4.8),
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
                "name": "Liver Function Test (LFT)",
                "category": "Biochemistry",
                "price": 500.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Screens for hepatic inflammation, biliary obstruction, and protein synthesis integrity.",
                "params": [
                    ("bili_tot", "Bilirubin (Total)", "mg/dL", 0.2, 1.2, 0.8),
                    ("bili_dir", "Bilirubin (Direct)", "mg/dL", 0.0, 0.3, 0.15),
                    ("sgot", "SGOT / AST", "U/L", 10.0, 40.0, 26.0),
                    ("sgpt", "SGPT / ALT", "U/L", 7.0, 56.0, 31.0),
                    ("alp", "Alkaline Phosphatase (ALP)", "U/L", 44.0, 147.0, 85.0),
                    ("prot_tot", "Total Protein", "g/dL", 6.0, 8.3, 7.2),
                    ("alb", "Albumin", "g/dL", 3.5, 5.2, 4.3),
                ]
            },
            {
                "id": "kft",
                "name": "Kidney Function Test (KFT)",
                "category": "Biochemistry",
                "price": 500.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Assesses glomerular filtration, nitrogen retention, and electrolyte balance.",
                "params": [
                    ("urea", "Blood Urea", "mg/dL", 15.0, 45.0, 28.0),
                    ("creat", "Serum Creatinine", "mg/dL", 0.7, 1.3, 0.95),
                    ("uric", "Uric Acid", "mg/dL", 3.5, 7.2, 5.2),
                    ("na", "Serum Sodium (Na+)", "mEq/L", 136.0, 145.0, 140.0),
                    ("k", "Serum Potassium (K+)", "mEq/L", 3.5, 5.1, 4.2),
                ]
            },
            {
                "id": "vit_d",
                "name": "Vitamin D 25-Hydroxy (Total)",
                "category": "Immunology",
                "price": 850.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "8 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Quantifies 25-hydroxycalciferol stores for bone health, immune regulation, and fatigue.",
                "params": [
                    ("vit_d_val", "25-OH Vitamin D", "ng/mL", 30.0, 100.0, 42.5),
                ]
            },
            {
                "id": "vit_b12",
                "name": "Vitamin B12 (Cyanocobalamin)",
                "category": "Immunology",
                "price": 750.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": True,
                "fasting_hours": 10,
                "description": "Assesses neurotropic cobalamin levels for megaloblastic anemia and peripheral neuropathy.",
                "params": [
                    ("vit_b12_val", "Vitamin B12", "pg/mL", 211.0, 911.0, 480.0),
                ]
            },
            {
                "id": "electrolytes",
                "name": "Serum Electrolytes Panel",
                "category": "Biochemistry",
                "price": 400.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "3 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "High-precision ion-selective electrode panel for fluid homeostasis and cardiac stability.",
                "params": [
                    ("na", "Sodium (Na+)", "mmol/L", 136.0, 146.0, 141.0),
                    ("k", "Potassium (K+)", "mmol/L", 3.5, 5.0, 4.1),
                    ("cl", "Chloride (Cl-)", "mmol/L", 98.0, 106.0, 102.0),
                    ("bicarb", "Bicarbonate (HCO3-)", "mmol/L", 22.0, 29.0, 25.5),
                ]
            },
            {
                "id": "crp_quant",
                "name": "C-Reactive Protein (hs-CRP Quantitative)",
                "category": "Immunology",
                "price": 420.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "4 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "High-sensitivity acute-phase inflammatory protein evaluating tissue inflammation and vascular risk.",
                "params": [
                    ("crp", "hs-CRP", "mg/L", 0.0, 3.0, 1.2),
                ]
            },
            {
                "id": "iron_profile",
                "name": "Iron Studies & Ferritin Panel",
                "category": "Hematology",
                "price": 800.0,
                "sample_type": "Serum (Gold Top SST)",
                "tube_cap_class": "tube-cap-serum",
                "turnaround": "6 Hours",
                "fasting": True,
                "fasting_hours": 12,
                "description": "Comprehensive iron homeostasis panel evaluating storage ferritin, total binding capacity, and saturation.",
                "params": [
                    ("serum_iron", "Serum Iron", "µg/dL", 65.0, 175.0, 110.0),
                    ("tibc", "Total Iron Binding Capacity (TIBC)", "µg/dL", 250.0, 450.0, 340.0),
                    ("transferrin_sat", "Transferrin Saturation", "%", 20.0, 50.0, 32.5),
                    ("ferritin", "Serum Ferritin", "ng/mL", 20.0, 250.0, 95.0),
                ]
            },
            {
                "id": "urine_routine",
                "name": "Urine Routine & Microscopic Examination",
                "category": "Clinical Pathology",
                "price": 200.0,
                "sample_type": "Clean Catch Midstream Urine (30ml)",
                "tube_cap_class": "tube-cap-urine",
                "turnaround": "2 Hours",
                "fasting": False,
                "fasting_hours": 0,
                "description": "Physical, chemical strip, and sediment microscopy screening for renal disease and urinary tract infections.",
                "params": [
                    ("ph_urine", "pH (Urine)", "pH units", 4.8, 7.5, 6.2),
                    ("sg_urine", "Specific Gravity", "ratio", 1.005, 1.030, 1.018),
                    ("protein_urine", "Urine Protein", "mg/dL", 0.0, 14.0, 5.0),
                    ("glucose_urine", "Urine Glucose", "mg/dL", 0.0, 15.0, 4.0),
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

