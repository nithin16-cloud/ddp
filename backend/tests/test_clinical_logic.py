"""
Unit tests for LabLine clinical reference range flagging and gauge logic.
Tests calculate_status_and_pct() across all clinical ranges and edge cases.
"""
import pytest
from routers.results_router import calculate_status_and_pct


class TestClinicalStatusCalculation:
    """Tests calculate_status_and_pct against clinical reference intervals."""

    def test_normal_value_middle_of_range(self):
        # Hb reference range: 13.0 - 17.0, val = 15.0
        status, pct = calculate_status_and_pct(15.0, 13.0, 17.0)
        assert status == "Normal"
        assert 45.0 <= pct <= 55.0

    def test_normal_at_exact_boundaries(self):
        status_min, _ = calculate_status_and_pct(13.0, 13.0, 17.0)
        assert status_min == "Normal"

        status_max, _ = calculate_status_and_pct(17.0, 13.0, 17.0)
        assert status_max == "Normal"

    def test_mildly_low_value(self):
        # Below min_val (13.0) but above critical cutoff (13.0 * 0.70 = 9.1)
        # e.g., 11.5
        status, pct = calculate_status_and_pct(11.5, 13.0, 17.0)
        assert status == "Low"
        assert pct < 25.0

    def test_critical_low_value(self):
        # Below critical threshold (< 0.70 * min_val)
        # 13.0 * 0.70 = 9.1, val = 8.5
        status, pct = calculate_status_and_pct(8.5, 13.0, 17.0)
        assert status == "Critical"
        assert pct >= 5.0  # bounded to at least 5.0%

    def test_mildly_high_value(self):
        # Above max_val (17.0) but below critical cutoff (17.0 * 1.35 = 22.95)
        # e.g., 18.5
        status, pct = calculate_status_and_pct(18.5, 13.0, 17.0)
        assert status == "High"
        assert pct > 65.0

    def test_critical_high_value(self):
        # Above critical threshold (> 1.35 * max_val)
        # 17.0 * 1.35 = 22.95, val = 24.0
        status, pct = calculate_status_and_pct(24.0, 13.0, 17.0)
        assert status == "Critical"
        assert pct <= 95.0  # bounded to at most 95.0%

    def test_percentage_bounds_clamping(self):
        # Extreme negative/zero value
        _, pct_extreme_low = calculate_status_and_pct(0.1, 100.0, 200.0)
        assert pct_extreme_low == 5.0

        # Extreme high value
        _, pct_extreme_high = calculate_status_and_pct(9999.0, 10.0, 20.0)
        assert pct_extreme_high == 95.0

    def test_zero_span_handling(self):
        # min_val == max_val should not crash with DivisionByZero
        status, pct = calculate_status_and_pct(5.0, 5.0, 5.0)
        assert status == "Normal"
        assert 5.0 <= pct <= 95.0
