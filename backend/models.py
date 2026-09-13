import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text,
    Enum, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
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
    phone = Column(String(30), nullable=True)
    station = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    bookings = relationship("Booking", back_populates="user")


class Test(Base):
    __tablename__ = "tests"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(80), nullable=False)
    price = Column(Float, nullable=False)
    sample_type = Column(String(120), nullable=False)
    tube_cap_class = Column(String(60), nullable=True, default="tube-cap-edta")
    turnaround = Column(String(60), nullable=True, default="4 Hours")
    fasting = Column(Boolean, default=False)
    fasting_hours = Column(Integer, nullable=True, default=0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    parameters = relationship("TestParameter", back_populates="test", cascade="all, delete-orphan")


class TestParameter(Base):
    __tablename__ = "test_parameters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    test_id = Column(String(50), ForeignKey("tests.id"), nullable=False)
    key = Column(String(50), nullable=False)
    label = Column(String(150), nullable=False)
    unit = Column(String(50), nullable=False)
    min_val = Column(Float, nullable=False)
    max_val = Column(Float, nullable=False)
    default_val = Column(Float, nullable=True)

    test = relationship("Test", back_populates="parameters")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(40), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    patient_name = Column(String(120), nullable=False)
    patient_age = Column(Integer, nullable=False)
    patient_gender = Column(String(20), nullable=False)
    patient_phone = Column(String(30), nullable=False)
    patient_email = Column(String(150), nullable=False)
    collection_type = Column(String(30), nullable=False, default="Home Collection")
    address = Column(String(255), nullable=True)
    date = Column(String(30), nullable=False)
    time_slot = Column(String(60), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)
    payment_status = Column(String(30), nullable=False, default="Pending")
    payment_method = Column(String(30), nullable=False, default="UPI")
    transaction_id = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="Pending")
    current_stage = Column(String(50), nullable=False, default="Booked")
    phlebotomist = Column(String(120), nullable=True)
    technician = Column(String(120), nullable=True)
    urgency = Column(String(30), nullable=False, default="Standard")
    sample_tube_barcode = Column(String(60), nullable=True)
    temperature_telemetry = Column(String(80), nullable=True)
    technician_notes = Column(Text, nullable=True)
    report_hash = Column(String(64), nullable=True)
    is_certified = Column(Boolean, default=False)
    certified_at = Column(String(40), nullable=True)
    time_booked = Column(DateTime(timezone=True), nullable=True)
    time_collected = Column(DateTime(timezone=True), nullable=True)
    time_in_transit = Column(DateTime(timezone=True), nullable=True)
    time_processing = Column(DateTime(timezone=True), nullable=True)
    time_completed = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookings")
    items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="booking", cascade="all, delete-orphan")
    results = relationship("ParameterResult", back_populates="booking", cascade="all, delete-orphan")


class BookingItem(Base):
    __tablename__ = "booking_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(String(40), ForeignKey("bookings.id"), nullable=False)
    test_id = Column(String(50), ForeignKey("tests.id"), nullable=False)
    test_name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)

    booking = relationship("Booking", back_populates="items")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(String(40), ForeignKey("bookings.id"), nullable=False)
    transaction_id = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(String(30), nullable=False, default="UPI")
    status = Column(String(30), nullable=False, default="Success")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    booking = relationship("Booking", back_populates="payments")


class ParameterResult(Base):
    __tablename__ = "parameter_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    booking_id = Column(String(40), ForeignKey("bookings.id"), nullable=False)
    parameter_key = Column(String(50), nullable=False)
    observed_value = Column(Float, nullable=False)
    status_flag = Column(String(30), nullable=False, default="Normal")
    marker_pct = Column(Float, nullable=True)

    booking = relationship("Booking", back_populates="results")


class Phlebotomist(Base):
    __tablename__ = "phlebotomists"

    id = Column(String(40), primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(30), nullable=False)
    active_pickups = Column(Integer, default=0)
    rating = Column(Float, default=5.0)
