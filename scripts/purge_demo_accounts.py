#!/usr/bin/env python3
"""
LabLine Database Cleanup & Account Verification Script
Deletes legacy demo accounts, purges demo names, and ensures the two authorized staff accounts:
1. Administrator: nithin@gmail.com / 12345678
2. Technician:    yashas@gmail.com / 12345678
"""

import os
import sys

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal, engine, Base
import models
from auth import hash_password, verify_password

def run_purge():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("[1/5] Purging obsolete demo accounts by email...")
        old_emails = ["admin@labline.com", "yashasrao@gmail.com"]
        deleted_by_email = db.query(models.User).filter(models.User.email.in_(old_emails)).delete(synchronize_session=False)
        print(f"      Deleted {deleted_by_email} user(s).")

        print("[2/5] Purging legacy demo accounts by name...")
        demo_names = ["Nitish Kumar", "Varshith Gowda", "Aryan Sharma"]
        total_name_deleted = 0
        for name in demo_names:
            count = db.query(models.User).filter(
                models.User.name.like(f"%{name}%"),
                models.User.email != "nithinshetty1166@gmail.com"
            ).delete(synchronize_session=False)
            total_name_deleted += count
        print(f"      Deleted {total_name_deleted} user(s).")

        print("[3/5] Updating legacy phlebotomist entries...")
        phlebs = db.query(models.Phlebotomist).filter(models.Phlebotomist.name == "Varshith Gowda").all()
        for p in phlebs:
            p.name = "Vijay Nair"
        print(f"      Updated {len(phlebs)} phlebotomist record(s).")

        print("[4/5] Verifying administrator account (nithinshetty1166@gmail.com)...")
        admin_email = os.getenv("ADMIN_EMAIL") or os.getenv("LABLINE_ADMIN_EMAIL") or "nithinshetty1166@gmail.com"
        admin_pass = os.getenv("ADMIN_PASSWORD") or os.getenv("LABLINE_ADMIN_PASSWORD") or "12345678"

        admin = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin:
            admin = models.User(
                name="System Administrator",
                email=admin_email,
                hashed_password=hash_password(admin_pass),
                role=models.UserRole.admin,
                phone="+91 98450 11223",
                station="Central Diagnostic Laboratory"
            )
            db.add(admin)
            print(f"      Created admin account for {admin_email}.")
        else:
            admin.role = models.UserRole.admin
            admin.name = "System Administrator"
            if not verify_password(admin_pass, admin.hashed_password):
                admin.hashed_password = hash_password(admin_pass)
            print(f"      Verified admin account for {admin_email}.")

        # Purge any other admin accounts
        other_admins = db.query(models.User).filter(
            models.User.role == models.UserRole.admin,
            models.User.email != admin_email
        ).all()
        for oa in other_admins:
            db.delete(oa)
            print(f"      Removed extraneous admin account: {oa.email}")

        print("[5/5] Verifying technician account (yashas@gmail.com)...")
        tech_email = os.getenv("TECH_EMAIL") or os.getenv("LABLINE_TECH_EMAIL") or "yashas@gmail.com"
        tech_pass = os.getenv("TECH_PASSWORD") or os.getenv("LABLINE_TECH_PASSWORD") or "12345678"

        tech = db.query(models.User).filter(models.User.email == tech_email).first()
        if not tech:
            tech = models.User(
                name="Lead Technologist (Yashas)",
                email=tech_email,
                hashed_password=hash_password(tech_pass),
                role=models.UserRole.technician,
                phone="+91 98450 44556",
                station="Station 1 - Central Diagnostics & Hematology"
            )
            db.add(tech)
            print(f"      Created technician account for {tech_email}.")
        else:
            tech.role = models.UserRole.technician
            tech.name = "Lead Technologist (Yashas)"
            if not verify_password(tech_pass, tech.hashed_password):
                tech.hashed_password = hash_password(tech_pass)
            print(f"      Verified technician account for {tech_email}.")

        # Purge any other technician accounts
        other_techs = db.query(models.User).filter(
            models.User.role == models.UserRole.technician,
            models.User.email != tech_email
        ).all()
        for ot in other_techs:
            db.delete(ot)
            print(f"      Removed extraneous technician account: {ot.email}")

        db.commit()
        print("\nSUCCESS: All obsolete accounts purged. Authorized Admin & Technician active.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: Failed to purge accounts: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_purge()
