import csv
import io
from datetime import datetime, time, timezone, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc

from database import get_db
from models import User, UserRole, UserActivity, Booking
from dependencies import require_role
from utils.tz import to_iso_utc, format_ist, IST_TIMEZONE

router = APIRouter(
    prefix="/admin/user-data",
    tags=["Admin User Data & Audits"],
    dependencies=[Depends(require_role(UserRole.admin))]
)


@router.get("/summary")
def get_user_data_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Summary KPI metrics for administrator console calculated relative to Indian Standard Time (IST)."""
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc.astimezone(IST_TIMEZONE)
    start_of_today_ist = datetime.combine(now_ist.date(), time.min).replace(tzinfo=IST_TIMEZONE)
    start_of_today_utc = start_of_today_ist.astimezone(timezone.utc)

    # Distinct registered users by normalized email
    total_users = db.query(func.count(func.distinct(func.lower(User.email)))).scalar() or 0

    # Distinct user sign-ups today in IST
    signups_today = db.query(func.count(func.distinct(func.lower(UserActivity.user_email)))).filter(
        UserActivity.event_type == "Signed up",
        UserActivity.created_at >= start_of_today_utc
    ).scalar() or 0

    # Distinct user login sessions today in IST
    logins_today = db.query(func.count(func.distinct(func.lower(UserActivity.user_email)))).filter(
        UserActivity.event_type == "Logged in",
        UserActivity.created_at >= start_of_today_utc
    ).scalar() or 0

    # Failed logins today in IST
    failed_today = db.query(func.count(UserActivity.id)).filter(
        UserActivity.event_type == "Failed login",
        UserActivity.created_at >= start_of_today_utc
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
    """Fetch paginated registered users with strictly 1 row per unique user (no duplication or redundancy)."""
    query = db.query(User)

    if q:
        search_filter = f"%{q.strip().lower()}%"
        query = query.filter((func.lower(User.email).like(search_filter)) | (func.lower(User.name).like(search_filter)))

    if role and role.lower() in ["patient", "technician", "admin"]:
        query = query.filter(User.role == UserRole(role.lower()))

    # Apply database ordering
    if sort_dir.lower() == "asc":
        if sort_by == "email":
            query = query.order_by(asc(func.lower(User.email)))
        elif sort_by == "name":
            query = query.order_by(asc(func.lower(User.name)))
        else:
            query = query.order_by(asc(User.created_at))
    else:
        if sort_by == "email":
            query = query.order_by(desc(func.lower(User.email)))
        elif sort_by == "name":
            query = query.order_by(desc(func.lower(User.name)))
        else:
            query = query.order_by(desc(User.created_at))

    raw_users = query.all()

    # Deduplicate strictly by lowercase email to guarantee zero redundant rows for any user
    unique_users_dict = {}
    for u in raw_users:
        clean_email = (u.email or "").strip().lower()
        if not clean_email:
            continue
        if clean_email not in unique_users_dict:
            unique_users_dict[clean_email] = u
        else:
            # If multiple rows exist for the same email, keep the primary record
            existing_u = unique_users_dict[clean_email]
            if existing_u.role != UserRole.admin and u.role == UserRole.admin:
                unique_users_dict[clean_email] = u

    unique_users = list(unique_users_dict.values())
    total_count = len(unique_users)

    # Paginate over deduplicated users
    offset = (page - 1) * page_size
    paged_users = unique_users[offset:offset + page_size]

    user_records = []
    for u in paged_users:
        clean_email = (u.email or "").strip().lower()
        last_login_row = db.query(UserActivity.created_at).filter(
            func.lower(UserActivity.user_email) == clean_email,
            UserActivity.event_type == "Logged in"
        ).order_by(desc(UserActivity.created_at)).first()

        login_count = db.query(func.count(UserActivity.id)).filter(
            func.lower(UserActivity.user_email) == clean_email,
            UserActivity.event_type == "Logged in"
        ).scalar() or 0

        user_records.append({
            "id": u.id,
            "name": u.name,
            "email": clean_email,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
            "created_at": to_iso_utc(u.created_at),
            "created_at_formatted": format_ist(u.created_at, default_empty="Never logged in"),
            "last_login": to_iso_utc(last_login_row[0]) if last_login_row and last_login_row[0] else None,
            "last_login_formatted": format_ist(last_login_row[0], default_empty="Never logged in") if last_login_row and last_login_row[0] else "Never logged in",
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
            s_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d").replace(tzinfo=IST_TIMEZONE)
            query = query.filter(UserActivity.created_at >= s_dt.astimezone(timezone.utc))
        except ValueError:
            pass

    if end_date:
        try:
            e_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=IST_TIMEZONE)
            query = query.filter(UserActivity.created_at <= e_dt.astimezone(timezone.utc))
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
            "created_at": to_iso_utc(act.created_at),
            "created_at_formatted": format_ist(act.created_at, default_empty="Never logged in")
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
    """Export filtered user activity records as downloadable CSV with exact IST timestamps."""
    query = db.query(UserActivity)

    if q:
        query = query.filter(UserActivity.user_email.ilike(f"%{q.strip()}%"))
    if role and role.lower() in ["patient", "technician", "admin"]:
        query = query.filter(UserActivity.role == role.lower())
    if event_type:
        query = query.filter(UserActivity.event_type == event_type.strip())
    if start_date:
        try:
            s_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d").replace(tzinfo=IST_TIMEZONE)
            query = query.filter(UserActivity.created_at >= s_dt.astimezone(timezone.utc))
        except ValueError:
            pass
    if end_date:
        try:
            e_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=IST_TIMEZONE)
            query = query.filter(UserActivity.created_at <= e_dt.astimezone(timezone.utc))
        except ValueError:
            pass

    items = query.order_by(desc(UserActivity.created_at)).limit(5000).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Time & Date (IST)", "User Email (Gmail)", "Role", "Event Type", "Client IP", "User Agent"])

    for act in items:
        ts = format_ist(act.created_at, default_empty="Never logged in")
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


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    current_admin: User = Depends(require_role(UserRole.admin)),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Permanently delete a registered user account from the platform.
    - Prevents self-deletion of the active admin.
    - Disassociates foreign keys (sets Booking.user_id to None) to preserve medical audit records.
    - Records an 'Account deleted' audit log event in UserActivity.
    """
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found."
        )

    # Protect against self-deletion
    if target_user.id == current_admin.id or target_user.email.strip().lower() == current_admin.email.strip().lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Self-deletion prohibited: You cannot remove your own active administrator account."
        )

    deleted_email = target_user.email
    deleted_role = target_user.role.value if hasattr(target_user.role, "value") else str(target_user.role)

    # Detach any existing bookings so historical records remain intact without violating foreign keys
    db.query(Booking).filter(Booking.user_id == target_user.id).update({Booking.user_id: None})

    # Record deletion in activity log
    client_ip = request.client.host if (request and request.client) else "127.0.0.1"
    raw_ua = request.headers.get("user-agent", "Admin Console") if request else "Admin Console"

    act_log = UserActivity(
        user_email=deleted_email,
        role=deleted_role,
        event_type="Account deleted",
        ip_address=client_ip,
        user_agent=f"Deleted by admin {current_admin.email} | {raw_ua}"[:250]
    )
    db.add(act_log)

    # Delete the target user and any duplicate case-variants for this email
    all_matching = db.query(User).filter(func.lower(User.email) == deleted_email.strip().lower()).all()
    for u in all_matching:
        db.query(Booking).filter(Booking.user_id == u.id).update({Booking.user_id: None})
        db.delete(u)
    db.commit()

    return {
        "success": True,
        "message": f"User account '{deleted_email}' was permanently removed.",
        "user_id": user_id,
        "email": deleted_email
    }


