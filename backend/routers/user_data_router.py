import csv
import io
from datetime import datetime, time, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from database import get_db
from models import User, UserRole, UserActivity
from dependencies import require_role

router = APIRouter(
    prefix="/admin/user-data",
    tags=["Admin User Data & Audits"],
    dependencies=[Depends(require_role(UserRole.admin))]
)


@router.get("/summary")
def get_user_data_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Summary KPI metrics for administrator console."""
    now_utc = datetime.now(timezone.utc)
    start_of_today = datetime.combine(now_utc.date(), time.min).replace(tzinfo=timezone.utc)

    total_users = db.query(func.count(User.id)).scalar() or 0

    # New sign-ups today
    signups_today = db.query(func.count(UserActivity.id)).filter(
        UserActivity.event_type == "Signed up",
        UserActivity.created_at >= start_of_today
    ).scalar() or 0

    # Successful logins today
    logins_today = db.query(func.count(UserActivity.id)).filter(
        UserActivity.event_type == "Logged in",
        UserActivity.created_at >= start_of_today
    ).scalar() or 0

    # Failed logins today
    failed_today = db.query(func.count(UserActivity.id)).filter(
        UserActivity.event_type == "Failed login",
        UserActivity.created_at >= start_of_today
    ).scalar() or 0

    return {
        "total_users": total_users,
        "signups_today": signups_today,
        "logins_today": logins_today,
        "failed_today": failed_today
    }


@router.get("/users")
def get_users_list(
    q: Optional[str] = Query(None, description="Search by email or name"),
    role: Optional[str] = Query(None, description="Filter by role: patient, technician, admin"),
    sort_by: str = Query("created_at", description="Field to sort by: created_at, email, name"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Fetch paginated registered users with their sign-up date, last login, and total logins."""
    query = db.query(User)

    if q:
        search_filter = f"%{q.strip()}%"
        query = query.filter((User.email.ilike(search_filter)) | (User.name.ilike(search_filter)))

    if role and role.lower() in ["patient", "technician", "admin"]:
        query = query.filter(User.role == UserRole(role.lower()))

    total_count = query.count()

    if sort_dir.lower() == "asc":
        if sort_by == "email":
            query = query.order_by(asc(User.email))
        elif sort_by == "name":
            query = query.order_by(asc(User.name))
        else:
            query = query.order_by(asc(User.created_at))
    else:
        if sort_by == "email":
            query = query.order_by(desc(User.email))
        elif sort_by == "name":
            query = query.order_by(desc(User.name))
        else:
            query = query.order_by(desc(User.created_at))

    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()

    user_records = []
    for u in users:
        last_login_row = db.query(UserActivity.created_at).filter(
            UserActivity.user_email == u.email,
            UserActivity.event_type == "Logged in"
        ).order_by(desc(UserActivity.created_at)).first()

        login_count = db.query(func.count(UserActivity.id)).filter(
            UserActivity.user_email == u.email,
            UserActivity.event_type == "Logged in"
        ).scalar() or 0

        user_records.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": last_login_row[0].isoformat() if last_login_row and last_login_row[0] else None,
            "total_logins": login_count
        })

    return {
        "users": user_records,
        "total": total_count,
        "page": page,
        "page_size": page_size
    }


@router.get("/activity")
def get_user_activity(
    q: Optional[str] = Query(None, description="Search by email"),
    role: Optional[str] = Query(None, description="Filter by role"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    start_date: Optional[str] = Query(None, description="Filter start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Filter end date YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Fetch paginated audit log of sign-up, login, and failed login events."""
    query = db.query(UserActivity)

    if q:
        query = query.filter(UserActivity.user_email.ilike(f"%{q.strip()}%"))

    if role and role.lower() in ["patient", "technician", "admin"]:
        query = query.filter(UserActivity.role == role.lower())

    if event_type:
        query = query.filter(UserActivity.event_type == event_type.strip())

    if start_date:
        try:
            s_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d")
            query = query.filter(UserActivity.created_at >= s_dt)
        except ValueError:
            pass

    if end_date:
        try:
            e_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(UserActivity.created_at <= e_dt)
        except ValueError:
            pass

    total_count = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(desc(UserActivity.created_at)).offset(offset).limit(page_size).all()

    activity_records = []
    for act in items:
        activity_records.append({
            "id": act.id,
            "user_email": act.user_email,
            "role": act.role,
            "event_type": act.event_type,
            "ip_address": act.ip_address,
            "user_agent": act.user_agent,
            "created_at": act.created_at.isoformat() if act.created_at else None
        })

    return {
        "activities": activity_records,
        "total": total_count,
        "page": page,
        "page_size": page_size
    }


@router.get("/activity/export")
def export_activity_csv(
    q: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Export filtered user activity records as downloadable CSV."""
    query = db.query(UserActivity)

    if q:
        query = query.filter(UserActivity.user_email.ilike(f"%{q.strip()}%"))
    if role and role.lower() in ["patient", "technician", "admin"]:
        query = query.filter(UserActivity.role == role.lower())
    if event_type:
        query = query.filter(UserActivity.event_type == event_type.strip())
    if start_date:
        try:
            s_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d")
            query = query.filter(UserActivity.created_at >= s_dt)
        except ValueError:
            pass
    if end_date:
        try:
            e_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(UserActivity.created_at <= e_dt)
        except ValueError:
            pass

    items = query.order_by(desc(UserActivity.created_at)).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp (ISO)", "User Email", "Role", "Event Type", "Client IP", "User Agent"])

    for act in items:
        ts = act.created_at.isoformat() if act.created_at else ""
        writer.writerow([
            ts,
            act.user_email,
            act.role or "N/A",
            act.event_type,
            act.ip_address or "N/A",
            act.user_agent or "N/A"
        ])

    output.seek(0)
    filename = f"labline_user_activity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

