import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User, UserRole, UserActivity
from services.seed_service import seed_initial_data

client = TestClient(app)


def test_public_signup_flow():
    seed_initial_data()
    db = SessionLocal()

    # 1. Administrator signup is strictly rejected (403 Forbidden)
    admin_signup = client.post("/auth/signup", json={
        "name": "Malicious Admin",
        "email": "hacker_admin@example.com",
        "password": "Password123!",
        "role": "admin"
    })
    assert admin_signup.status_code == 403
    assert "Administrator accounts cannot be registered" in admin_signup.json()["detail"]

    # 2. Patient signup succeeds (201 Created)
    patient_email = "new_registered_patient@example.com"
    existing_p = db.query(User).filter(User.email == patient_email).first()
    if existing_p:
        db.delete(existing_p)
        db.commit()

    patient_signup = client.post("/auth/signup", json={
        "name": "Sarah Connor",
        "email": patient_email,
        "password": "ClinicalPass123!",
        "role": "patient"
    })
    assert patient_signup.status_code == 201, patient_signup.text
    pat_data = patient_signup.json()
    assert "access_token" in pat_data
    assert pat_data["user"]["role"] == "patient"
    assert pat_data["user"]["name"] == "Sarah Connor"

    # 3. Technician signup succeeds (201 Created)
    tech_email = "new_registered_tech@example.com"
    existing_t = db.query(User).filter(User.email == tech_email).first()
    if existing_t:
        db.delete(existing_t)
        db.commit()

    tech_signup = client.post("/auth/signup", json={
        "name": "Dr. Alex Murphy",
        "email": tech_email,
        "password": "ClinicalPass123!",
        "role": "technician"
    })
    assert tech_signup.status_code == 201, tech_signup.text
    tech_data = tech_signup.json()
    assert "access_token" in tech_data
    assert tech_data["user"]["role"] == "technician"

    # 4. Duplicate email signup fails (400 Bad Request)
    dup_res = client.post("/auth/signup", json={
        "name": "Duplicate Sarah",
        "email": patient_email,
        "password": "AnotherPassword!",
        "role": "patient"
    })
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"]

    # Cleanup created users
    p_to_del = db.query(User).filter(User.email == patient_email).first()
    if p_to_del:
        db.delete(p_to_del)
    t_to_del = db.query(User).filter(User.email == tech_email).first()
    if t_to_del:
        db.delete(t_to_del)
    db.commit()
    db.close()
