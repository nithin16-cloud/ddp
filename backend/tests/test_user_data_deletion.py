import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User, UserRole, UserActivity, Booking
from auth import hash_password
from config import settings
from services.seed_service import seed_initial_data

client = TestClient(app)


def test_user_deletion_workflow():
    seed_initial_data()
    # 1. Login as Admin
    admin_res = client.post("/auth/login", json={"email": settings.ADMIN_EMAIL, "password": "12345678"})
    assert admin_res.status_code == 200, admin_res.text
    admin_token = admin_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Login as Technician
    tech_res = client.post("/auth/login", json={"email": "yashas@gmail.com", "password": "12345678"})
    assert tech_res.status_code == 200, tech_res.text
    tech_token = tech_res.json()["access_token"]
    tech_headers = {"Authorization": f"Bearer {tech_token}"}

    # 3. Create a temporary patient user in DB
    db = SessionLocal()
    temp_email = "testpatient_deleteme@gmail.com"
    existing = db.query(User).filter(User.email == temp_email).first()
    if existing:
        db.query(Booking).filter(Booking.user_id == existing.id).update({Booking.user_id: None})
        db.delete(existing)
        db.commit()

    temp_patient = User(
        name="Test Patient Deletable",
        email=temp_email,
        hashed_password=hash_password("password123"),
        role=UserRole.patient,
        phone="+919876543210"
    )
    db.add(temp_patient)
    db.commit()
    db.refresh(temp_patient)
    target_id = temp_patient.id
    db.close()

    # 4. Technician cannot delete users (403 Forbidden)
    forbidden_res = client.delete(f"/admin/user-data/users/{target_id}", headers=tech_headers)
    assert forbidden_res.status_code == 403, forbidden_res.text

    # 5. Admin cannot delete self (400 Bad Request)
    admin_user_data = client.get(f"/admin/user-data/users?q={settings.ADMIN_EMAIL}", headers=admin_headers).json()
    admin_user_id = admin_user_data["users"][0]["id"]
    self_del_res = client.delete(f"/admin/user-data/users/{admin_user_id}", headers=admin_headers)
    assert self_del_res.status_code == 400, self_del_res.text
    assert "Self-deletion prohibited" in self_del_res.json()["detail"]

    # 6. Admin deletes the target patient (200 OK)
    del_res = client.delete(f"/admin/user-data/users/{target_id}", headers=admin_headers)
    assert del_res.status_code == 200, del_res.text
    del_data = del_res.json()
    assert del_data["success"] is True
    assert del_data["email"] == temp_email

    # 7. Verify user is removed from database
    db = SessionLocal()
    deleted_user = db.query(User).filter(User.id == target_id).first()
    assert deleted_user is None

    # 8. Verify activity log records "Account deleted"
    activity = db.query(UserActivity).filter(
        UserActivity.user_email == temp_email,
        UserActivity.event_type == "Account deleted"
    ).first()
    assert activity is not None
    assert "Deleted by admin" in activity.user_agent
    db.close()

    # 9. Deleting already deleted user returns 404
    not_found_res = client.delete(f"/admin/user-data/users/{target_id}", headers=admin_headers)
    assert not_found_res.status_code == 404
