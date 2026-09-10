from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict
from models import UserRole


# ==================== User & Auth Schemas ====================
class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.patient
    phone: Optional[str] = None
    station: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole
    phone: Optional[str] = None
    station: Optional[str] = None
    created_at: Optional[datetime] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ==================== Test Parameter Schemas ====================
class TestParameterBase(BaseModel):
    key: str
    label: str
    unit: str
    min_val: float
    max_val: float
    default_val: Optional[float] = None


class TestParameterCreate(TestParameterBase):
    pass


class TestParameterOut(TestParameterBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    test_id: str


# ==================== Test Catalog Schemas ====================
class TestBase(BaseModel):
    name: str
    category: str
    price: float
    sample_type: str
    tube_cap_class: Optional[str] = "tube-cap-edta"
    turnaround: Optional[str] = "4 Hours"
    fasting: Optional[bool] = False
    fasting_hours: Optional[int] = 0
    description: Optional[str] = None
    is_active: Optional[bool] = True


class TestCreate(TestBase):
    id: str
    parameters: Optional[List[TestParameterCreate]] = []


class TestUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    sample_type: Optional[str] = None
    tube_cap_class: Optional[str] = None
    turnaround: Optional[str] = None
    fasting: Optional[bool] = None
    fasting_hours: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TestOut(TestBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parameters: List[TestParameterOut] = []


# ==================== Booking Schemas ====================
class BookingItemCreate(BaseModel):
    test_id: str


class BookingItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: str
    test_id: str
    test_name: str
    price: float


class BookingCreate(BaseModel):
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_phone: str
    patient_email: EmailStr
    collection_type: str = "Home Collection"
    address: Optional[str] = None
    date: str
    time_slot: str
    test_ids: List[str]
    payment_method: Optional[str] = "UPI"
    urgency: Optional[str] = "Standard"


class BookingStageUpdate(BaseModel):
    stage: str
    technician_notes: Optional[str] = None


class BookingAssignUpdate(BaseModel):
    technician: Optional[str] = None
    phlebotomist: Optional[str] = None


class ParameterResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: str
    parameter_key: str
    observed_value: float
    status_flag: str
    marker_pct: Optional[float] = None


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: Optional[int] = None
    patient_name: str
    patient_age: int
    patient_gender: str
    patient_phone: str
    patient_email: str
    collection_type: str
    address: Optional[str] = None
    date: str
    time_slot: str
    total_amount: float
    payment_status: str
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    current_stage: str
    phlebotomist: Optional[str] = None
    technician: Optional[str] = None
    urgency: str
    sample_tube_barcode: Optional[str] = None
    temperature_telemetry: Optional[str] = None
    technician_notes: Optional[str] = None
    time_booked: Optional[str] = None
    time_collected: Optional[str] = None
    time_in_transit: Optional[str] = None
    time_processing: Optional[str] = None
    time_completed: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[BookingItemOut] = []
    results: List[ParameterResultOut] = []


# ==================== Payment Schemas ====================
class PaymentCreate(BaseModel):
    booking_id: str
    amount: float
    method: str = "UPI"


class PaymentVerify(BaseModel):
    booking_id: str
    transaction_id: str
    status: str = "Success"


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: str
    transaction_id: str
    amount: float
    method: str
    status: str
    created_at: Optional[datetime] = None


# ==================== Results Schemas ====================
class ResultEntryItem(BaseModel):
    parameter_key: str
    observed_value: float


class ResultSubmit(BaseModel):
    results: List[ResultEntryItem]
    technician_notes: Optional[str] = None


# ==================== Analytics Schemas ====================
class AnalyticsSummary(BaseModel):
    total_bookings: int
    total_revenue: float
    pending_bookings: int
    completed_bookings: int
    critical_flags_count: int
    active_technicians: int
    active_phlebotomists: int
