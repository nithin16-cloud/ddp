"""
Unit tests for Order ID generation and specimen priority dispatcher algorithm.
"""
import re
from unittest.mock import MagicMock
from routers.bookings_router import generate_booking_id, compute_specimen_priority
from models import Booking, BookingItem


class TestBookingAndDispatcher:
    """Tests UUID-based collision-free Order ID and specimen priority scoring."""

    def test_order_id_generation_format_and_entropy(self):
        db_mock = MagicMock()
        db_mock.query().filter().first.return_value = None

        ids = {generate_booking_id(db_mock) for _ in range(100)}
        assert len(ids) == 100  # all unique
        for oid in ids:
            assert re.match(r"^ORD-[0-9A-F]{8}$", oid)

    def test_priority_score_stat_vs_routine(self):
        b_routine = Booking(
            urgency="Standard",
            current_stage="Intake Queued",
            items=[BookingItem(test_name="Lipid Profile")]
        )
        b_stat = Booking(
            urgency="STAT",
            current_stage="Intake Queued",
            items=[BookingItem(test_name="Lipid Profile")]
        )

        p_routine = compute_specimen_priority(b_routine)
        p_stat = compute_specimen_priority(b_stat)

        # STAT adds +100 vs Routine +20
        assert p_stat["score"] > p_routine["score"]
        assert p_stat["tier"] == "CRITICAL_STAT"

    def test_priority_score_edta_lysis_factor(self):
        b_edta = Booking(
            urgency="Standard",
            current_stage="Sample Collected",
            items=[BookingItem(test_name="Complete Blood Count (CBC)")]
        )
        b_serum = Booking(
            urgency="Standard",
            current_stage="Sample Collected",
            items=[BookingItem(test_name="Thyroid Panel")]
        )

        p_edta = compute_specimen_priority(b_edta)
        p_serum = compute_specimen_priority(b_serum)

        # EDTA (+35) vs Serum (+15)
        assert p_edta["score"] == p_serum["score"] + 20
