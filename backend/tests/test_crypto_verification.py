"""
Unit tests for cryptographic report hashing, tamper resistance, and uncertified report verification (Issue #3).
"""
from unittest.mock import MagicMock
from routers.reports_router import generate_report_hash, verify_report_authenticity
from models import Booking, ParameterResult, BookingItem


class TestCryptoVerification:
    """Tests SHA-256 report hash generation, tamper detection, and authenticity verification."""

    def test_report_hash_determinism(self):
        results = [
            {"key": "hb", "observed_value": 14.5, "status_flag": "Normal"},
            {"key": "wbc", "observed_value": 7500.0, "status_flag": "Normal"}
        ]
        tests = ["Complete Blood Count (CBC)"]

        hash1 = generate_report_hash("ORD-12345678", "Nithin Sharma", tests, results)
        # Reverse order of results array to verify canonical sorting
        hash2 = generate_report_hash("ORD-12345678", "Nithin Sharma", tests, list(reversed(results)))

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex string

    def test_tamper_detection(self):
        results_orig = [{"key": "hb", "observed_value": 14.5, "status_flag": "Normal"}]
        results_tampered = [{"key": "hb", "observed_value": 11.0, "status_flag": "Low"}]
        tests = ["CBC"]

        hash_orig = generate_report_hash("ORD-12345678", "Nithin Sharma", tests, results_orig)
        hash_tampered = generate_report_hash("ORD-12345678", "Nithin Sharma", tests, results_tampered)

        assert hash_orig != hash_tampered

    def test_uncertified_report_fails_verification(self):
        """Issue #3: Uncertified reports must return is_authentic = False."""
        db_mock = MagicMock()
        booking_mock = Booking(
            id="ORD-UNVERIFIED",
            patient_name="Test Patient",
            report_hash=None,
            is_certified=False,
            items=[BookingItem(test_name="CBC")]
        )
        db_mock.query().filter().first.return_value = booking_mock
        db_mock.query().filter().all.return_value = [
            ParameterResult(parameter_key="hb", observed_value=14.0, status_flag="Normal")
        ]

        verification = verify_report_authenticity("ORD-UNVERIFIED", db=db_mock)
        assert verification["is_authentic"] is False
        assert verification["verification_status"] == "UNCERTIFIED_REPORT_PENDING_APPROVAL"
        # Must not have called db_mock.commit() to certify
        db_mock.commit.assert_not_called()
