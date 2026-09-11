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


# ==================== Fair-Workload Specimen Priority Dispatcher ====================

CERTIFIED_TECHNICIANS = [
    {"name": "Varshith Gowda", "station": "Station 4 - Automated Hematology & Photometry", "max_capacity": 5},
    {"name": "Rupesh Patel", "station": "Station 2 - Clinical Biochemistry & Immunoassay", "max_capacity": 5},
    {"name": "Dr. Yatish Rao", "station": "Station 1 - High-Complexity Pathology & Reviews", "max_capacity": 4}
]


def compute_specimen_priority(booking: Booking) -> dict:
    """
    Algorithmic Priority Score Formulation:
    PriorityScore = W_urgency + W_decay + W_stage
    - Urgency: STAT emergency (+100) vs Routine (+20)
    - Tube Degradation: EDTA Purple Tube (+35) vs Fluoride (+25) vs Serum (+15)
    - Processing Stage: In-Transit / Processing (+15 to +20)
    """
    score = 0
    factors = []

    # 1. Urgency Weight
    if (booking.urgency or "").upper() == "STAT":
        score += 100
        factors.append("Emergency STAT Urgency (+100)")
    else:
        score += 20
        factors.append("Standard Routine Scheduling (+20)")

    # 2. Pre-Analytical Tube Stability / Cellular Lysis Factor
    test_names = [item.test_name.lower() for item in booking.items]
    if any("cbc" in t or "blood count" in t for t in test_names):
        score += 35
        factors.append("EDTA Whole Blood High-Lysis Risk (+35)")
    elif any("glucose" in t or "sugar" in t or "hba1c" in t for t in test_names):
        score += 25
        factors.append("Glycolytic Preservation Window (+25)")
    else:
        score += 15
        factors.append("Standard Serum Stability (+15)")

    # 3. Pipeline Urgency
    stage = (booking.current_stage or "").lower()
    if "processing" in stage:
        score += 20
        factors.append("Active Analyzer Processing (+20)")
    elif "transit" in stage:
        score += 15
        factors.append("In-Transit Cold Chain (+15)")
    elif "collected" in stage:
        score += 10
        factors.append("Sample Collected (+10)")
    else:
        score += 5
        factors.append("Intake Queued (+5)")

    tier = "CRITICAL_STAT" if score >= 120 else "HIGH_PRIORITY" if score >= 60 else "ROUTINE"
    return {
        "score": score,
        "tier": tier,
        "factors": factors
    }


@router.get("/priority/worklist")
def get_prioritized_worklist(db: Session = Depends(get_db)):
    """
    Returns all active specimens ranked by algorithmic Priority Score (descending),
    illustrating real-time priority queue scheduling.
    """
    active_bookings = db.query(Booking).filter(
        Booking.current_stage.notin_(["Completed", "Report Generated"])
    ).all()

    prioritized = []
    for b in active_bookings:
        p_info = compute_specimen_priority(b)
        prioritized.append({
            "booking_id": b.id,
            "patient_name": b.patient_name,
            "urgency": b.urgency,
            "current_stage": b.current_stage,
            "technician": b.technician or "Unassigned",
            "tests": [item.test_name for item in b.items],
            "priority_score": p_info["score"],
            "priority_tier": p_info["tier"],
            "priority_factors": p_info["factors"],
            "sample_tube_barcode": b.sample_tube_barcode or f"BC-{b.id}"
        })

    # Sort descending by priority score (Max-Heap / Priority Queue ordering)
    prioritized.sort(key=lambda x: x["priority_score"], reverse=True)

    # Attach recommended rank order
    for idx, item in enumerate(prioritized, 1):
        item["rank"] = idx

    return prioritized


@router.post("/dispatch/auto-balance")
def run_fair_workload_dispatcher(db: Session = Depends(get_db)):
    """
    Greedy Min-Load Priority Dispatcher:
    1. Calculates current active workload per certified technician.
    2. Identifies all unassigned or pending specimens and scores them via Priority Engine.
    3. Greedily allocates highest priority specimens to the least-burdened technician.
    """
    # 1. Calculate active baseline loads for certified technicians
    tech_names = [t["name"] for t in CERTIFIED_TECHNICIANS]
    current_loads = {}
    for name in tech_names:
        count = db.query(Booking).filter(
            Booking.technician.ilike(f"%{name}%"),
            Booking.current_stage.notin_(["Completed", "Report Generated"])
        ).count()
        current_loads[name] = count

    initial_loads = dict(current_loads)

    # 2. Get unassigned or pending specimens
    active_bookings = db.query(Booking).filter(
        Booking.current_stage.notin_(["Completed", "Report Generated"])
    ).all()

    # Filter specimens that need assignment (unassigned or placeholder)
    targets = [
        b for b in active_bookings
        if not b.technician or b.technician.lower() in ("unassigned", "not assigned", "pending", "")
    ]

    # If all are already assigned, allow full rebalancing across active specimens
    if not targets and active_bookings:
        targets = active_bookings
        # Reset loads for rebalancing
        current_loads = {name: 0 for name in tech_names}

    # Score each target specimen
    scored_targets = []
    for b in targets:
        p_info = compute_specimen_priority(b)
        scored_targets.append((p_info["score"], p_info, b))

    # Sort targets descending by priority score (highest priority first)
    scored_targets.sort(key=lambda x: x[0], reverse=True)

    allocations = []
    for score, p_info, b in scored_targets:
        # Greedy Choice: Assign to technician with minimum current load
        best_tech = min(current_loads.keys(), key=lambda k: current_loads[k])
        b.technician = best_tech
        current_loads[best_tech] += 1

        allocations.append({
            "booking_id": b.id,
            "patient_name": b.patient_name,
            "urgency": b.urgency,
            "assigned_technician": best_tech,
            "priority_score": score,
            "tier": p_info["tier"],
            "reason": f"Priority score {score} routed to {best_tech} (load was {current_loads[best_tech] - 1})"
        })

    db.commit()

    return {
        "success": True,
        "algorithm": "Greedy Min-Load Priority Dispatcher (O(N log N + N * M))",
        "total_dispatched": len(allocations),
        "initial_workloads": initial_loads,
        "balanced_workloads": current_loads,
        "allocations": allocations,
        "message": f"Successfully distributed {len(allocations)} clinical specimens across {len(tech_names)} technicians."
    }

