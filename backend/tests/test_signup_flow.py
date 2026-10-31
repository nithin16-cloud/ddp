import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User, UserRole, UserActivity
from services.seed_service import seed_initial_data

client = TestClient(app)


def test_public_signup_flow():
    seed_initial_data()
    patient_email = "new_registered_patient@example.com"
    tech_email = "new_registered_tech@example.com"

    db = SessionLocal()
    existing_p = db.query(User).filter(User.email == patient_email).first()
    if existing_p:
        db.delete(existing_p)
    existing_t = db.query(User).filter(User.email == tech_email).first()
    if existing_t:
        db.delete(existing_t)
    db.commit()
    db.close()

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
    db = SessionLocal()
    p_to_del = db.query(User).filter(User.email == patient_email).first()
    if p_to_del:
        db.delete(p_to_del)
    t_to_del = db.query(User).filter(User.email == tech_email).first()
    if t_to_del:
        db.delete(t_to_del)
    db.commit()
    db.close()


def test_multi_tap_and_deduplication():
    seed_initial_data()
    test_email = "multitap_patient@example.com"

    db = SessionLocal()
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
    db.query(UserActivity).filter(UserActivity.user_email == test_email).delete()
    db.commit()
    db.close()

    # 1. First tap: Sign up succeeds
    res1 = client.post("/auth/signup", json={
        "name": "Multi Tap User",
        "email": "  MultiTap_Patient@example.com  ",
        "password": "Password123!",
        "role": "patient"
    })
    assert res1.status_code == 201, res1.text
    assert res1.json()["user"]["email"] == test_email

    # 2. Second tap (multi-tap / duplicate): Rejected cleanly without creating redundant row
    res2 = client.post("/auth/signup", json={
        "name": "Multi Tap User",
        "email": test_email,
        "password": "Password123!",
        "role": "patient"
    })
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]

    # Verify database has strictly 1 user row
    db = SessionLocal()
    user_count = db.query(User).filter(User.email == test_email).count()
    assert user_count == 1, f"Expected 1 user, found {user_count}"

    # Verify UserActivity has strictly 1 "Signed up" event
    signup_acts = db.query(UserActivity).filter(
        UserActivity.user_email == test_email,
        UserActivity.event_type == "Signed up"
    ).count()
    assert signup_acts == 1, f"Expected 1 signup activity, found {signup_acts}"
    db.close()

    # 3. Multi-tap logins: 3 consecutive login requests within milliseconds
    log1 = client.post("/auth/login", json={"email": test_email, "password": "Password123!"})
    log2 = client.post("/auth/login", json={"email": "MULTITAP_PATIENT@EXAMPLE.COM", "password": "Password123!"})
    log3 = client.post("/auth/login", json={"email": test_email, "password": "Password123!"})
    assert log1.status_code == 200
    assert log2.status_code == 200
    assert log3.status_code == 200

    # Verify UserActivity records each login event
    db = SessionLocal()
    login_acts = db.query(UserActivity).filter(
        UserActivity.user_email == test_email,
        UserActivity.event_type == "Logged in"
    ).count()
    assert login_acts == 3, f"Expected 3 login activities, found {login_acts}"
    db.close()

    # 4. In Admin portal: Verify that /admin/user-data/users shows strictly 1 particular user row
    admin_res = client.post("/auth/login", json={"email": "nithin@gmail.com", "password": "12345678"})
    assert admin_res.status_code == 200
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    users_res = client.get(f"/admin/user-data/users?q={test_email}", headers=admin_headers)
    assert users_res.status_code == 200
    users_data = users_res.json()
    assert len(users_data["users"]) == 1, f"Expected 1 user row in admin portal, found {len(users_data['users'])}"
    assert users_data["users"][0]["email"] == test_email
    assert users_data["users"][0]["total_logins"] == 3

    # Cleanup
    db = SessionLocal()
    u_del = db.query(User).filter(User.email == test_email).first()
    if u_del:
        db.delete(u_del)
    db.query(UserActivity).filter(UserActivity.user_email == test_email).delete()
    db.commit()
    db.close()
