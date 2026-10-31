import re
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User, UserRole, UserActivity
from services.seed_service import seed_initial_data
from utils.tz import format_ist, IST_TIMEZONE

client = TestClient(app)


def test_ist_timestamp_events_and_users_directory():
    """
    Strict verification requirement:
    1. Sign up a new user.
    2. Log in twice with valid credentials.
    3. Fail one login on purpose with incorrect password.
    4. Query /admin/user-data/activity and verify all events appear with:
       - correct email
       - correct event type
       - HH:MM time and DD/MM/YY date in IST
       - ordered newest first
    5. Query /admin/user-data/users and verify:
       - strictly 1 row for that user
       - sign-up time in HH:MM DD/MM/YY IST
       - last login time in HH:MM DD/MM/YY IST
       - total logins == 2
    6. Verify that a user who has never logged in shows 'Never logged in'.
    """
    seed_initial_data()
    test_email = "ist_test_patient@example.com"
    never_logged_email = "never_logged_patient@example.com"

    # Cleanup any leftovers
    db = SessionLocal()
    for e in (test_email, never_logged_email):
        u = db.query(User).filter(User.email == e).first()
        if u:
            db.delete(u)
        db.query(UserActivity).filter(UserActivity.user_email == e).delete()
    db.commit()
    db.close()

    # Step 1: Sign up new user
    signup_res = client.post("/auth/signup", json={
        "name": "Ananya Sharma",
        "email": test_email,
        "password": "Password123!",
        "role": "patient"
    })
    assert signup_res.status_code == 201, signup_res.text

    # Step 2: Log in twice
    login1_res = client.post("/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login1_res.status_code == 200, login1_res.text

    login2_res = client.post("/auth/login", json={"email": test_email, "password": "Password123!"})
    assert login2_res.status_code == 200, login2_res.text

    # Step 3: Fail one login on purpose
    failed_login_res = client.post("/auth/login", json={"email": test_email, "password": "WrongPassword!"})
    assert failed_login_res.status_code == 401

    # Step 4: Create a user who has never logged in (sign up only via direct seed or admin)
    db = SessionLocal()
    never_user = User(
        name="Pooja Rao",
        email=never_logged_email,
        hashed_password="dummy_hash_never_login",
        role=UserRole.patient,
        created_at=datetime.now(timezone.utc)
    )
    db.add(never_user)
    db.commit()
    db.close()

    # Step 5: Login as Admin to query User Data endpoints
    admin_login = client.post("/auth/login", json={"email": "nithin@gmail.com", "password": "12345678"})
    assert admin_login.status_code == 200, admin_login.text
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Step 6: Verify /admin/user-data/activity
    act_res = client.get(f"/admin/user-data/activity?q={test_email}", headers=admin_headers)
    assert act_res.status_code == 200, act_res.text
    activities = act_res.json()["activities"]

    # Must have exactly 4 events for this user
    assert len(activities) == 4, f"Expected 4 activity rows, found {len(activities)}"

    # Must be newest first:
    # 0: Failed login
    # 1: Logged in (login 2)
    # 2: Logged in (login 1)
    # 3: Signed up
    expected_sequence = ["Failed login", "Logged in", "Logged in", "Signed up"]
    actual_sequence = [a["event_type"] for a in activities]
    assert actual_sequence == expected_sequence, f"Expected {expected_sequence}, got {actual_sequence}"

    # Regex for HH:MM DD/MM/YY (e.g. 14:32 31/10/26)
    timestamp_pattern = re.compile(r"^\d{2}:\d{2}\s+\d{2}/\d{2}/\d{2}$")

    now_ist = datetime.now(timezone.utc).astimezone(IST_TIMEZONE)
    current_time_str = now_ist.strftime("%H:%M")
    current_date_str = now_ist.strftime("%d/%m/%y")

    for act in activities:
        assert act["user_email"] == test_email
        formatted_ts = act["created_at_formatted"]
        assert timestamp_pattern.match(formatted_ts), f"Invalid IST format: {formatted_ts}"
        
        # Verify date portion is exact DD/MM/YY
        parts = formatted_ts.split()
        time_part, date_part = parts[0], parts[1]
        assert date_part == current_date_str, f"Date mismatch: expected {current_date_str}, got {date_part}"
        
        # Verify time portion has no seconds, 24-hr format (e.g. HH:MM)
        assert len(time_part) == 5 and time_part[2] == ":"

    # Step 7: Verify /admin/user-data/users for the active user
    users_res = client.get(f"/admin/user-data/users?q={test_email}", headers=admin_headers)
    assert users_res.status_code == 200, users_res.text
    user_rows = users_res.json()["users"]
    assert len(user_rows) == 1, f"Expected exactly 1 user row, found {len(user_rows)}"
    user_entry = user_rows[0]

    assert user_entry["email"] == test_email
    assert user_entry["total_logins"] == 2
    assert timestamp_pattern.match(user_entry["created_at_formatted"])
    assert timestamp_pattern.match(user_entry["last_login_formatted"])

    # Step 8: Verify user who has never logged in shows 'Never logged in'
    never_res = client.get(f"/admin/user-data/users?q={never_logged_email}", headers=admin_headers)
    assert never_res.status_code == 200, never_res.text
    never_rows = never_res.json()["users"]
    assert len(never_rows) == 1
    never_entry = never_rows[0]

    assert never_entry["email"] == never_logged_email
    assert never_entry["last_login"] is None
    assert never_entry["last_login_formatted"] == "Never logged in"
    assert never_entry["total_logins"] == 0
    assert timestamp_pattern.match(never_entry["created_at_formatted"])

    # Step 9: Verify CSV Export includes Time & Date (IST) column formatted as HH:MM DD/MM/YY
    csv_res = client.get(f"/admin/user-data/activity/export?q={test_email}", headers=admin_headers)
    assert csv_res.status_code == 200
    csv_text = csv_res.text
    csv_lines = [line.strip() for line in csv_text.splitlines() if line.strip()]
    assert len(csv_lines) >= 5  # Header + 4 activity rows
    assert "Time & Date (IST)" in csv_lines[0]
    for row in csv_lines[1:5]:
        first_col = row.split(",")[0].replace('"', '')
        assert timestamp_pattern.match(first_col), f"CSV column not in HH:MM DD/MM/YY IST format: {first_col}"

    # Cleanup
    db = SessionLocal()
    for e in (test_email, never_logged_email):
        u = db.query(User).filter(User.email == e).first()
        if u:
            db.delete(u)
        db.query(UserActivity).filter(UserActivity.user_email == e).delete()
    db.commit()
    db.close()
