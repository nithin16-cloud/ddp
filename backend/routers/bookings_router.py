import random
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Booking, BookingItem, Test, Phlebotomist
from schemas import (
    BookingCreate, BookingOut, BookingStageUpdate, BookingAssignUpdate
)

router = APIRouter(prefix="/bookings", tags=["Bookings & Specimen Tracking"])


def generate_booking_id(db: Session) -> str:
    """Generate a clean human-readable Order ID like ORD-4821"""
    while True:
        num = random.randint(1000, 9999)
        new_id = f"ORD-{num}"
        existing = db.query(Booking).filter(Booking.id == new_id).first()
        if not existing:
            return new_id


def generate_barcode(booking_id: str) -> str:
    return f"BC-{booking_id.replace('ORD-', '')}-{random.randint(100, 999)}"


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db)
):
    if not booking_in.test_ids:
        raise HTTPException(status_code=400, detail="At least one test must be selected")

    # Fetch tests from DB
    tests = db.query(Test).filter(Test.id.in_(booking_in.test_ids)).all()
    if not tests:
        raise HTTPException(status_code=400, detail="None of the selected tests were found")

    booking_id = generate_booking_id(db)
    barcode = generate_barcode(booking_id)
    total_amount = sum(t.price for t in tests)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Pick an available phlebotomist if home collection
    phleb_name = "Not Assigned"
    if booking_in.collection_type.lower().startswith("home"):
        first_phleb = db.query(Phlebotomist).first()
        if first_phleb:
            phleb_name = first_phleb.name

    new_booking = Booking(
        id=booking_id,
        patient_name=booking_in.patient_name,
        patient_age=booking_in.patient_age,
        patient_gender=booking_in.patient_gender,
        patient_phone=booking_in.patient_phone,
        patient_email=str(booking_in.patient_email),
        collection_type=booking_in.collection_type,
        address=booking_in.address,
        date=booking_in.date,
        time_slot=booking_in.time_slot,
        total_amount=total_amount,
        payment_status="Success" if booking_in.payment_method != "Cash" else "Pending",
        payment_method=booking_in.payment_method or "UPI",
        transaction_id=f"TXN-{random.randint(100000, 999999)}" if booking_in.payment_method != "Cash" else None,
        status="Confirmed",
        current_stage="Booked",
        phlebotomist=phleb_name,
        technician="Unassigned",
        urgency=booking_in.urgency or "Standard",
        sample_tube_barcode=barcode,
        temperature_telemetry="4.2°C (Cold Chain OK)",
        time_booked=now_str
    )
    db.add(new_booking)
    db.flush()

    for t in tests:
        item = BookingItem(
            booking_id=new_booking.id,
            test_id=t.id,
            test_name=t.name,
            price=t.price
        )
        db.add(item)

    db.commit()
    db.refresh(new_booking)
    return new_booking


@router.get("", response_model=List[BookingOut])
def get_bookings(
    email: Optional[str] = None,
    stage: Optional[str] = None,
    status_filter: Optional[str] = None,
    urgency: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Booking)
    if email:
        query = query.filter(Booking.patient_email.ilike(f"%{email}%"))
    if stage:
        query = query.filter(Booking.current_stage.ilike(f"%{stage}%"))
    if status_filter:
        query = query.filter(Booking.status.ilike(f"%{status_filter}%"))
    if urgency:
        query = query.filter(Booking.urgency.ilike(f"%{urgency}%"))

    return query.order_by(Booking.created_at.desc()).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking_by_id(booking_id: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")
    return booking


@router.put("/{booking_id}/stage", response_model=BookingOut)
def advance_booking_stage(
    booking_id: str,
    stage_in: BookingStageUpdate,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    new_stage = stage_in.stage
    booking.current_stage = new_stage
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Update lifecycle timestamps based on stage
    if "collected" in new_stage.lower():
        booking.time_collected = now_str
    elif "transit" in new_stage.lower():
        booking.time_in_transit = now_str
    elif "processing" in new_stage.lower():
        booking.time_processing = now_str
    elif "certified" in new_stage.lower() or "completed" in new_stage.lower():
        booking.time_completed = now_str
        booking.status = "Completed"

    if stage_in.technician_notes:
        booking.technician_notes = stage_in.technician_notes

    db.commit()
    db.refresh(booking)
    return booking


@router.put("/{booking_id}/assign", response_model=BookingOut)
def assign_technician_phlebotomist(
    booking_id: str,
    assign_in: BookingAssignUpdate,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    if assign_in.technician is not None:
        booking.technician = assign_in.technician
    if assign_in.phlebotomist is not None:
        booking.phlebotomist = assign_in.phlebotomist

    db.commit()
    db.refresh(booking)
    return booking
