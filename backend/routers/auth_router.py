from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserRole, UserActivity
from schemas import UserSignup, UserLogin, Token, UserOut
from auth import hash_password, verify_password, create_access_token
from dependencies import get_current_user
from config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _extract_client_info(request: Request):
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")[:255] if request.headers else None
    return ip, ua


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignup, request: Request, db: Session = Depends(get_db)):
    ip, ua = _extract_client_info(request)

    # Disallow registration as administrator through public sign-up
    if payload.role == UserRole.admin:
        fail_act = UserActivity(
            user_email=payload.email,
            role="admin",
            event_type="Failed login",
            ip_address=ip,
            user_agent=ua
        )
        db.add(fail_act)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator accounts cannot be registered via public sign-up."
        )

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Automatically record signed up event in activity log
    activity = UserActivity(
        user_email=user.email,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        event_type="Signed up",
        ip_address=ip,
        user_agent=ua
    )
    db.add(activity)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip, ua = _extract_client_info(request)

    user = db.query(User).filter(User.email == payload.email).first()

    # If user does not exist and it is not an admin/tech credential attempt,
    # auto-provision as a patient since the frontend has no sign-up form
    if not user:
        if payload.email.lower() not in (settings.ADMIN_EMAIL.lower(), settings.TECH_EMAIL.lower()):
            user = User(
                name=payload.email.split("@")[0].replace(".", " ").replace("_", " ").title(),
                email=payload.email,
                hashed_password=hash_password(payload.password),
                role=UserRole.patient,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Record sign up in activity
            signup_act = UserActivity(
                user_email=user.email,
                role="patient",
                event_type="Signed up",
                ip_address=ip,
                user_agent=ua,
            )
            db.add(signup_act)
            db.commit()
        else:
            # Failed staff login attempt
            fail_act = UserActivity(
                user_email=payload.email,
                role="admin" if payload.email.lower() == settings.ADMIN_EMAIL.lower() else "technician",
                event_type="Failed login",
                ip_address=ip,
                user_agent=ua,
            )
            db.add(fail_act)
            db.commit()
            raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Verify password
    if not verify_password(payload.password, user.hashed_password):
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
        fail_act = UserActivity(
            user_email=payload.email,
            role=role_val,
            event_type="Failed login",
            ip_address=ip,
            user_agent=ua,
        )
        db.add(fail_act)
        db.commit()
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    # Record successful login event
    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    login_act = UserActivity(
        user_email=user.email,
        role=role_val,
        event_type="Logged in",
        ip_address=ip,
        user_agent=ua,
    )
    db.add(login_act)
    db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return Token(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
