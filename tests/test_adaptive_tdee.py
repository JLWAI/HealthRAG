"""
Unit Tests for Adaptive TDEE System

Tests EWMA trend weight calculation, weight tracking database,
and trend analysis functionality.
"""

import pytest
import os
import tempfile
from datetime import date, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adaptive_tdee import (
    calculate_trend_weight,
    calculate_simple_moving_average,
    WeightEntry,
    WeightTrend,
    WeightTracker
)


class TestEWMATrendWeight:
    """Test EWMA trend weight calculation"""

    def test_monotonic_weight_loss(self):
        """Test EWMA with steady weight loss (210 → 205 lbs)"""
        weights = [210.0, 209.0, 208.0, 207.0, 206.0, 205.0]
        trend = calculate_trend_weight(weights, alpha=0.3)

        # Verify trend exists for all weights
        assert len(trend) == len(weights)

        # Verify trend is smoothed (less volatile than actual)
        assert trend[0] == 210.0  # First weight unchanged
        assert trend[-1] < weights[0]  # Overall downward trend
        assert trend[-1] > weights[-1]  # Trend lags behind actual (smoothing)

        # Verify decreasing trend
        for i in range(1, len(trend)):
            assert trend[i] < trend[i-1], f"Trend should decrease: {trend[i]} >= {trend[i-1]}"

    def test_minor_fluctuations(self):
        """Test EWMA smooths daily fluctuations (208, 209, 208, 207)"""
        weights = [208.0, 209.0, 208.0, 207.0]
        trend = calculate_trend_weight(weights, alpha=0.3)

        assert len(trend) == 4

        # EWMA should smooth the spike at day 2
        assert trend[0] == 208.0
        assert trend[1] > trend[0]  # Trend goes up (but less than actual)
        assert trend[1] < 209.0  # But not as much as actual weight
        assert trend[2] < trend[1]  # Trend starts going back down
        assert trend[3] < trend[2]  # Continues downward

        # Verify smoothing: trend is less volatile than actual
        actual_range = max(weights) - min(weights)
        trend_range = max(trend) - min(trend)
        assert trend_range < actual_range, "Trend should be less volatile than actual"

    def test_empty_list(self):
        """Test handling of empty weight list"""
        trend = calculate_trend_weight([])
        assert trend == []

    def test_single_weight(self):
        """Test handling of single weight point"""
        trend = calculate_trend_weight([210.0])
        assert trend == [210.0]

    def test_two_weights(self):
        """Test minimum viable trend (2 points)"""
        weights = [210.0, 209.0]
        trend = calculate_trend_weight(weights, alpha=0.3)

        assert len(trend) == 2
        assert trend[0] == 210.0
        assert trend[1] == pytest.approx(209.7)  # 0.3 * 209 + 0.7 * 210

    def test_alpha_parameter(self):
        """Test different alpha values affect smoothing"""
        weights = [210.0, 205.0]  # Large drop

        # High alpha (0.9) = more reactive
        trend_high = calculate_trend_weight(weights, alpha=0.9)
        assert trend_high[1] == pytest.approx(205.5)  # 0.9 * 205 + 0.1 * 210

        # Low alpha (0.1) = more smoothed
        trend_low = calculate_trend_weight(weights, alpha=0.1)
        assert trend_low[1] == pytest.approx(209.5)  # 0.1 * 205 + 0.9 * 210

        # High alpha reacts more to new data
        assert trend_high[1] < trend_low[1]

    def test_invalid_alpha(self):
        """Test validation of alpha parameter"""
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            calculate_trend_weight([210.0, 209.0], alpha=1.5)

        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            calculate_trend_weight([210.0, 209.0], alpha=0.0)

        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            calculate_trend_weight([210.0, 209.0], alpha=-0.3)

    def test_invalid_weights(self):
        """Test handling of invalid weight values"""
        with pytest.raises(ValueError, match="All weights must be valid numbers"):
            calculate_trend_weight([210.0, None, 208.0])

        with pytest.raises(ValueError, match="All weights must be valid numbers"):
            calculate_trend_weight([210.0, "invalid", 208.0])


class TestSimpleMovingAverage:
    """Test 7-day simple moving average"""

    def test_insufficient_data(self):
        """Test SMA with less than 7 days"""
        weights = [210.0, 209.0, 208.0]
        sma = calculate_simple_moving_average(weights, window=7)

        assert len(sma) == 3
        assert all(x is None for x in sma)

    def test_exact_window(self):
        """Test SMA with exactly 7 days"""
        weights = [210.0, 209.0, 208.0, 207.0, 206.0, 205.0, 204.0]
        sma = calculate_simple_moving_average(weights, window=7)

        assert len(sma) == 7
        assert sma[-1] == pytest.approx(207.0)  # Average of all 7
        assert all(x is None for x in sma[:-1])

    def test_sliding_window(self):
        """Test SMA with multiple windows"""
        weights = [210, 209, 208, 207, 206, 205, 204, 203]
        sma = calculate_simple_moving_average(weights, window=7)

        # First 6 should be None
        assert all(x is None for x in sma[:6])

        # 7th should be average of first 7
        assert sma[6] == pytest.approx(207.0)

        # 8th should be average of days 2-8
        assert sma[7] == pytest.approx(206.0)


class TestWeightTracker:
    """Test WeightTracker database operations"""

    @pytest.fixture
    def tracker(self):
        """Create temporary weight tracker for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = WeightTracker(db_path=db_path)
        yield tracker

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_log_weight_today(self, tracker):
        """Test logging weight for today"""
        entry_id = tracker.log_weight(210.5, notes="Morning weight")

        assert entry_id > 0

        latest = tracker.get_latest_weight()
        assert latest is not None
        assert latest.weight_lbs == 210.5
        assert latest.notes == "Morning weight"
        assert latest.date == date.today().isoformat()

    def test_log_weight_specific_date(self, tracker):
        """Test logging weight for specific date"""
        test_date = "2025-10-15"
        tracker.log_weight(209.0, log_date=test_date)

        entries = tracker.get_weights()
        assert len(entries) == 1
        assert entries[0].date == test_date
        assert entries[0].weight_lbs == 209.0

    def test_duplicate_date_replaces(self, tracker):
        """Test that logging same date replaces old entry"""
        test_date = "2025-10-15"

        tracker.log_weight(210.0, log_date=test_date, notes="First")
        tracker.log_weight(209.0, log_date=test_date, notes="Corrected")

        entries = tracker.get_weights()
        assert len(entries) == 1  # Only one entry
        assert entries[0].weight_lbs == 209.0
        assert entries[0].notes == "Corrected"

    def test_invalid_weight(self, tracker):
        """Test validation of weight values"""
        with pytest.raises(ValueError, match="Invalid weight"):
            tracker.log_weight(0)

        with pytest.raises(ValueError, match="Invalid weight"):
            tracker.log_weight(-150)

        with pytest.raises(ValueError, match="Invalid weight"):
            tracker.log_weight(1500)

    def test_get_weights_date_range(self, tracker):
        """Test retrieving weights in date range"""
        # Log weights for 10 days
        base_date = date(2025, 10, 1)
        for i in range(10):
            log_date = (base_date + timedelta(days=i)).isoformat()
            tracker.log_weight(210.0 - i, log_date=log_date)

        # Get middle 5 days
        entries = tracker.get_weights(
            start_date="2025-10-03",
            end_date="2025-10-07"
        )

        assert len(entries) == 5
        assert entries[0].date == "2025-10-07"  # Newest first
        assert entries[-1].date == "2025-10-03"  # Oldest last

    def test_get_weights_limit(self, tracker):
        """Test limiting number of returned weights"""
        # Log 10 weights
        for i in range(10):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            tracker.log_weight(210.0 - i, log_date=log_date)

        entries = tracker.get_weights(limit=5)
        assert len(entries) == 5

    def test_delete_weight(self, tracker):
        """Test deleting weight entry"""
        test_date = "2025-10-15"
        tracker.log_weight(210.0, log_date=test_date)

        # Verify exists
        entries = tracker.get_weights()
        assert len(entries) == 1

        # Delete
        deleted = tracker.delete_weight(test_date)
        assert deleted is True

        # Verify gone
        entries = tracker.get_weights()
        assert len(entries) == 0

    def test_delete_nonexistent(self, tracker):
        """Test deleting nonexistent entry"""
        deleted = tracker.delete_weight("2025-01-01")
        assert deleted is False


class TestTrendAnalysis:
    """Test weight trend analysis"""

    @pytest.fixture
    def tracker_with_data(self):
        """Create tracker with 30 days of weight data"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = WeightTracker(db_path=db_path)

        # Log 30 days of weight loss: 210 → 205 lbs
        base_date = date.today() - timedelta(days=29)
        for i in range(30):
            log_date = (base_date + timedelta(days=i)).isoformat()
            weight = 210.0 - (i * 0.17)  # ~5 lbs over 30 days
            tracker.log_weight(weight, log_date=log_date)

        yield tracker

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_trend_analysis_basic(self, tracker_with_data):
        """Test basic trend analysis"""
        trends = tracker_with_data.get_trend_analysis(days=30)

        assert len(trends) == 30
        assert all(isinstance(t, WeightTrend) for t in trends)

        # Verify trend weights exist
        assert all(t.trend_weight is not None for t in trends)

        # Verify trend is smoothed
        actual_weights = [t.actual_weight for t in trends]
        trend_weights = [t.trend_weight for t in trends]

        # Trend should be less volatile
        actual_volatility = max(actual_weights) - min(actual_weights)
        trend_volatility = max(trend_weights) - min(trend_weights)
        assert trend_volatility <= actual_volatility

    def test_trend_analysis_with_goal(self, tracker_with_data):
        """Test trend analysis with goal weight"""
        goal_weight = 200.0
        trends = tracker_with_data.get_trend_analysis(days=30, goal_weight=goal_weight)

        # Verify delta from goal
        for trend in trends:
            assert trend.delta_from_goal is not None
            expected_delta = trend.actual_weight - goal_weight
            assert trend.delta_from_goal == pytest.approx(expected_delta)

    def test_trend_analysis_rate_of_change(self, tracker_with_data):
        """Test rate of change calculation"""
        trends = tracker_with_data.get_trend_analysis(days=30)

        # With 30 days of data, should have rate of change
        assert trends[-1].rate_of_change_weekly is not None

        # Should be negative (weight loss)
        assert trends[-1].rate_of_change_weekly < 0

        # Should be approximately -1.17 lbs/week (5 lbs / 30 days * 7)
        expected_rate = -5.0 / 30 * 7
        assert trends[-1].rate_of_change_weekly == pytest.approx(expected_rate, abs=0.3)

    def test_trend_analysis_insufficient_data(self):
        """Test trend analysis with insufficient data"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = WeightTracker(db_path=db_path)

        # Only 5 days of data
        for i in range(5):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            tracker.log_weight(210.0 - i, log_date=log_date)

        trends = tracker.get_trend_analysis(days=30)

        # Should have 5 trends
        assert len(trends) == 5

        # Rate of change should be None (< 14 days)
        assert trends[-1].rate_of_change_weekly is None

        # Cleanup
        os.remove(db_path)


@pytest.mark.integration
class TestWeightTrackerIntegration:
    """Integration tests for weight tracking workflow"""

    def test_complete_workflow(self):
        """Test complete weight tracking workflow"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = WeightTracker(db_path=db_path)

        # User logs weight for 2 weeks
        base_date = date.today() - timedelta(days=13)
        for i in range(14):
            log_date = (base_date + timedelta(days=i)).isoformat()
            weight = 210.0 - (i * 0.5)  # Losing 0.5 lb/day
            tracker.log_weight(weight, log_date=log_date, notes=f"Day {i+1}")

        # Get trend analysis
        trends = tracker.get_trend_analysis(days=14, goal_weight=200.0)

        # Verify complete data
        assert len(trends) == 14
        assert all(t.trend_weight is not None for t in trends)
        assert all(t.delta_from_goal is not None for t in trends)

        # Verify trend is smoother than actual
        actual_day1 = trends[0].actual_weight
        actual_day14 = trends[-1].actual_weight
        trend_day1 = trends[0].trend_weight
        trend_day14 = trends[-1].trend_weight

        actual_change = actual_day14 - actual_day1
        trend_change = trend_day14 - trend_day1

        # Trend should show similar overall change but with less volatility
        # EWMA lags behind actual, so allow for reasonable difference
        assert abs(trend_change - actual_change) < 1.5

        # Latest weight
        latest = tracker.get_latest_weight()
        assert latest.weight_lbs == 203.5  # 210 - (13 * 0.5)

        # Cleanup
        os.remove(db_path)
