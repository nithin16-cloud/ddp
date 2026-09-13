"""
Unit tests for Pydantic input validation on patient fields in BookingCreate (Issue #8).
"""
import pytest
from pydantic import ValidationError
from schemas import BookingCreate


class TestPatientValidation:
    """Validates patient age, gender, name, and phone inputs."""

    def valid_payload(self, **overrides):
        payload = {
            "patient_name": "Rohan Sharma",
            "patient_age": 35,
            "patient_gender": "Male",
            "patient_phone": "+91 98451 22341",
            "patient_email": "rohan@example.com",
            "collection_type": "Home Collection",
            "address": "123 Indiranagar, Bengaluru",
            "date": "2026-09-15",
            "time_slot": "08:00 AM - 09:00 AM",
            "test_ids": ["cbc"],
            "payment_method": "UPI",
            "urgency": "Standard"
        }
        payload.update(overrides)
        return payload

    def test_valid_booking_passes(self):
        booking = BookingCreate(**self.valid_payload())
        assert booking.patient_name == "Rohan Sharma"
        assert booking.patient_age == 35
        assert booking.patient_gender == "Male"

    def test_negative_age_rejected(self):
        with pytest.raises(ValidationError) as exc:
            BookingCreate(**self.valid_payload(patient_age=-5))
        assert "greater than or equal to 0" in str(exc.value)

    def test_unrealistic_age_rejected(self):
        with pytest.raises(ValidationError) as exc:
            BookingCreate(**self.valid_payload(patient_age=999))
        assert "less than or equal to 125" in str(exc.value)

    def test_gender_normalization(self):
        b1 = BookingCreate(**self.valid_payload(patient_gender="female"))
        assert b1.patient_gender == "Female"

        b2 = BookingCreate(**self.valid_payload(patient_gender="M"))
        assert b2.patient_gender == "Male"

        b3 = BookingCreate(**self.valid_payload(patient_gender="other"))
        assert b3.patient_gender == "Other"

    def test_invalid_gender_rejected(self):
        with pytest.raises(ValidationError) as exc:
            BookingCreate(**self.valid_payload(patient_gender="Unknown"))
        assert "Patient gender must be Male, Female, or Other" in str(exc.value)

    def test_name_min_length_rejected(self):
        with pytest.raises(ValidationError) as exc:
            BookingCreate(**self.valid_payload(patient_name="A"))
        assert "at least 2 characters" in str(exc.value)

    def test_invalid_phone_rejected(self):
        # Too short (< 10 chars)
        with pytest.raises(ValidationError):
            BookingCreate(**self.valid_payload(patient_phone="12345"))

        # Non-digits (contains letters)
        with pytest.raises(ValidationError) as exc_letters:
            BookingCreate(**self.valid_payload(patient_phone="98765abcde"))
        assert "10 to 15 digits" in str(exc_letters.value)
