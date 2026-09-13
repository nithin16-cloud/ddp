from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Booking, ParameterResult, TestParameter, User, UserRole
from schemas import ResultSubmit, ParameterResultOut
from dependencies import require_role

router = APIRouter(prefix="/results", tags=["Clinical Results & Validation"])


def calculate_status_and_pct(val: float, min_val: float, max_val: float) -> tuple[str, float]:
    """
    Evaluates clinical reference range and flags:
    Normal, Low, High, Critical Low, Critical High
    Also calculates gauge marker percentage between 0 and 100.
    """
    span = max_val - min_val if max_val > min_val else 1.0

    # Marker position percentage across 0 to 100%
    # Normal range is mapped between ~25% and 75%
    pct = 25.0 + ((val - min_val) / span) * 50.0
    pct = max(5.0, min(95.0, round(pct, 1)))

    # Bug 7 fix: threshold aligned to 0.70 (matches frontend evaluateParameter)
    if val < (min_val * 0.70):
        return "Critical", pct
    elif val > (max_val * 1.35):
        return "Critical", pct
    elif val < min_val:
        return "Low", pct
    elif val > max_val:
        return "High", pct
    else:
        return "Normal", pct


@router.get("/{booking_id}", response_model=List[ParameterResultOut])
def get_results_by_booking(booking_id: str, db: Session = Depends(get_db)):
    results = db.query(ParameterResult).filter(ParameterResult.booking_id == booking_id).all()
    return results


@router.post("/{booking_id}", response_model=List[ParameterResultOut], status_code=status.HTTP_200_OK)
def submit_results(
    booking_id: str,
    submission: ResultSubmit,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.technician, UserRole.admin))
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    # Reject result submission if the booking has not reached Processing stage
    ALLOWED_STAGES = {"processing", "in-transit", "sample collected", "report generated"}
    current = (booking.current_stage or "").lower()
    if not any(s in current for s in ALLOWED_STAGES):
        raise HTTPException(
            status_code=400,
            detail=f"Results can only be submitted for bookings in Processing stage or beyond. Current stage: '{booking.current_stage}'"
        )

    saved_results = []
    has_critical = False
    booking_test_ids = [item.test_id for item in booking.items]

    for item in submission.results:
        # Lookup parameter definition scoped to tests belonging to this booking (Issue #2 fix)
        param = db.query(TestParameter).filter(
            TestParameter.key == item.parameter_key,
            TestParameter.test_id.in_(booking_test_ids)
        ).first()
        if not param:
            param = db.query(TestParameter).filter(TestParameter.key == item.parameter_key).first()

        min_v = param.min_val if param else 0.0
        max_v = param.max_val if param else 100.0

        flag, marker_pct = calculate_status_and_pct(item.observed_value, min_v, max_v)
        if flag == "Critical":
            has_critical = True

        # Check if result already exists for this booking & parameter
        existing = db.query(ParameterResult).filter(
            ParameterResult.booking_id == booking_id,
            ParameterResult.parameter_key == item.parameter_key
        ).first()

        if existing:
            existing.observed_value = item.observed_value
            existing.status_flag = flag
            existing.marker_pct = marker_pct
            saved_results.append(existing)
        else:
            new_res = ParameterResult(
                booking_id=booking_id,
                parameter_key=item.parameter_key,
                observed_value=item.observed_value,
                status_flag=flag,
                marker_pct=marker_pct
            )
            db.add(new_res)
            saved_results.append(new_res)

    # Advance booking status
    booking.current_stage = "Results Certified"
    booking.status = "Completed"
    booking.time_completed = datetime.now()
    if submission.technician_notes:
        booking.technician_notes = submission.technician_notes

    db.commit()
    for r in saved_results:
        db.refresh(r)

    return saved_results
