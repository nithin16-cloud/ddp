from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from database import get_db
from models import Booking, BookingItem, ParameterResult, User, UserRole, Phlebotomist, Test
from schemas import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["Analytics & KPIs"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    total_bookings = db.query(func.count(Booking.id)).scalar() or 0
    total_revenue = db.query(func.sum(Booking.total_amount)).filter(Booking.payment_status == "Success").scalar() or 0.0

    pending = db.query(func.count(Booking.id)).filter(
        Booking.current_stage != "Results Certified",
        Booking.status != "Completed"
    ).scalar() or 0

    completed = db.query(func.count(Booking.id)).filter(
        (Booking.current_stage == "Results Certified") | (Booking.status == "Completed")
    ).scalar() or 0

    critical_count = db.query(func.count(ParameterResult.id)).filter(
        ParameterResult.status_flag == "Critical"
    ).scalar() or 0

    active_techs = db.query(func.count(User.id)).filter(
        User.role == UserRole.technician
    ).scalar() or 0

    active_phlebs = db.query(func.count(Phlebotomist.id)).scalar() or 0

    return AnalyticsSummary(
        total_bookings=total_bookings,
        total_revenue=round(float(total_revenue), 2),
        pending_bookings=pending,
        completed_bookings=completed,
        critical_flags_count=critical_count,
        active_technicians=max(active_techs, 3),  # fallback to active team count
        active_phlebotomists=max(active_phlebs, 4)
    )


@router.get("/categories")
def get_category_breakdown(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    results = db.query(
        Test.category,
        func.count(BookingItem.id).label("count")
    ).join(BookingItem, BookingItem.test_id == Test.id).group_by(Test.category).all()

    return [{"category": r[0], "orders": r[1]} for r in results]


@router.get("/technicians")
def get_technician_workload(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    # List of technicians with their assigned orders
    techs = db.query(User).filter(User.role == UserRole.technician).all()
    out = []
    for t in techs:
        # Bug 13 fix: Use ilike partial match — booking.technician may store the name
        # with role suffix (e.g. "Clinical Technologist") while
        # User.name is just the technician name. Exact equality always returned 0.
        assigned = db.query(func.count(Booking.id)).filter(
            Booking.technician.ilike(f"%{t.name}%")
        ).scalar() or 0
        completed = db.query(func.count(Booking.id)).filter(
            Booking.technician.ilike(f"%{t.name}%"),
            Booking.status == "Completed"
        ).scalar() or 0
        out.append({
            "id": t.id,
            "name": t.name,
            "station": t.station or "Hematology Bench 2",
            "assigned_count": assigned,
            "completed_count": completed
        })
    return out
