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

# Automatically create all tables in MySQL if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LabLine Healthcare Diagnostic API",
    description="Backend REST API for LabLine Specimen & Diagnostic Management Platform",
    version="1.0.0"
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.on_event("startup")
def seed_initial_data():
    """Ensure essential tests and clinical phlebotomists exist in the database."""
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

        # Check tests
        if db.query(models.Test).count() == 0:
            default_tests = [
                models.Test(
                    id="cbc",
                    name="Complete Blood Count (CBC)",
                    category="Hematology",
                    price=350.0,
                    sample_type="EDTA Whole Blood (2ml)",
                    tube_cap_class="tube-cap-edta",
                    turnaround="4 Hours",
                    fasting=False,
                    description="Evaluates cellular health and screens for anemia, infections, and platelet disorders."
                ),
                models.Test(
                    id="lipid",
                    name="Lipid Profile (Comprehensive)",
                    category="Biochemistry",
                    price=650.0,
                    sample_type="Serum (Gold Top SST)",
                    tube_cap_class="tube-cap-serum",
                    turnaround="6 Hours",
                    fasting=True,
                    fasting_hours=12,
                    description="Measures cholesterol fractions to quantify cardiovascular risk."
                ),
                models.Test(
                    id="thyroid",
                    name="Thyroid Function Panel (TFT)",
                    category="Endocrinology",
                    price=550.0,
                    sample_type="Serum (Gold Top SST)",
                    tube_cap_class="tube-cap-serum",
                    turnaround="6 Hours",
                    fasting=False,
                    description="Measures TSH, T3, and T4 to assess thyroid function."
                ),
                models.Test(
                    id="hba1c",
                    name="HbA1c & Estimated Glucose",
                    category="Diabetes Care",
                    price=450.0,
                    sample_type="EDTA Whole Blood (2ml)",
                    tube_cap_class="tube-cap-edta",
                    turnaround="4 Hours",
                    fasting=False,
                    description="Gold-standard glycated biomarker for 90-day glycemic control."
                )
            ]
            db.add_all(default_tests)
            db.commit()

            # Parameters for CBC
            cbc_params = [
                models.TestParameter(test_id="cbc", key="hb", label="Hemoglobin", unit="g/dL", min_val=13.0, max_val=17.0, default_val=14.2),
                models.TestParameter(test_id="cbc", key="wbc", label="Total Leukocyte Count (WBC)", unit="/µL", min_val=4000.0, max_val=11000.0, default_val=7500.0),
                models.TestParameter(test_id="cbc", key="rbc", label="Total RBC Count", unit="million/µL", min_val=4.5, max_val=5.9, default_val=5.1),
                models.TestParameter(test_id="cbc", key="plt", label="Platelet Count", unit="lakh/µL", min_val=1.5, max_val=4.5, default_val=2.8),
                models.TestParameter(test_id="cbc", key="pcv", label="Packed Cell Volume (PCV)", unit="%", min_val=40.0, max_val=50.0, default_val=44.5),
            ]
            db.add_all(cbc_params)

            # Parameters for Lipid
            lipid_params = [
                models.TestParameter(test_id="lipid", key="chol", label="Total Cholesterol", unit="mg/dL", min_val=125.0, max_val=200.0, default_val=185.0),
                models.TestParameter(test_id="lipid", key="tg", label="Triglycerides", unit="mg/dL", min_val=50.0, max_val=150.0, default_val=135.0),
                models.TestParameter(test_id="lipid", key="hdl", label="HDL (Good Cholesterol)", unit="mg/dL", min_val=40.0, max_val=60.0, default_val=48.0),
                models.TestParameter(test_id="lipid", key="ldl", label="LDL (Bad Cholesterol)", unit="mg/dL", min_val=60.0, max_val=100.0, default_val=92.0),
            ]
            db.add_all(lipid_params)

            # Parameters for Thyroid
            tft_params = [
                models.TestParameter(test_id="thyroid", key="tsh", label="TSH (Ultrasensitive)", unit="µIU/mL", min_val=0.35, max_val=4.94, default_val=2.45),
                models.TestParameter(test_id="thyroid", key="t3", label="Total Triiodothyronine (T3)", unit="ng/dL", min_val=80.0, max_val=200.0, default_val=130.0),
                models.TestParameter(test_id="thyroid", key="t4", label="Total Thyroxine (T4)", unit="µg/dL", min_val=5.1, max_val=14.1, default_val=8.8),
            ]
            db.add_all(tft_params)

            # Parameters for HbA1c
            hba1c_params = [
                models.TestParameter(test_id="hba1c", key="hba1c_pct", label="HbA1c (Glycated Hemoglobin)", unit="%", min_val=4.0, max_val=5.6, default_val=5.4),
                models.TestParameter(test_id="hba1c", key="eag", label="Estimated Avg Glucose (eAG)", unit="mg/dL", min_val=70.0, max_val=115.0, default_val=108.0),
            ]
            db.add_all(hba1c_params)
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
