import random
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Booking, Payment
from schemas import PaymentCreate, PaymentVerify, PaymentOut

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/create", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == payment_in.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{payment_in.booking_id}' not found")

    txn_id = f"PAY-{random.randint(100000, 999999)}-{random.randint(10, 99)}"
    new_payment = Payment(
        booking_id=payment_in.booking_id,
        transaction_id=txn_id,
        amount=payment_in.amount,
        method=payment_in.method,
        status="Success"
    )
    db.add(new_payment)

    booking.payment_status = "Success"
    booking.payment_method = payment_in.method
    booking.transaction_id = txn_id

    db.commit()
    db.refresh(new_payment)
    return new_payment


@router.post("/verify", response_model=PaymentOut)
def verify_payment(
    verify_in: PaymentVerify,
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(
        Payment.booking_id == verify_in.booking_id,
        Payment.transaction_id == verify_in.transaction_id
    ).first()

    if not payment:
        # Create a confirmed payment if webhook or direct simulation
        booking = db.query(Booking).filter(Booking.id == verify_in.booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail=f"Booking '{verify_in.booking_id}' not found")

        payment = Payment(
            booking_id=verify_in.booking_id,
            transaction_id=verify_in.transaction_id,
            amount=booking.total_amount,
            method="UPI",
            status=verify_in.status
        )
        db.add(payment)
        booking.payment_status = "Success"
        booking.transaction_id = verify_in.transaction_id
    else:
        payment.status = verify_in.status

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/{booking_id}", response_model=List[PaymentOut])
def get_payments_for_booking(booking_id: str, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.booking_id == booking_id).all()
