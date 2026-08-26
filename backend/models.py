import enum

from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func

from database import Base


class UserRole(str, enum.Enum):
    patient = "patient"
    technician = "technician"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.patient)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
