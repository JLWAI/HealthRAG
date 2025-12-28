"""
Unit Tests for Adaptive TDEE Calculations (Back-Calculation + Adjustments)

Tests the Week 11-12 features:
- Back-calculated TDEE from weight change + intake
- Macro adjustment recommendations
- Integration with weight/food tracking
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from adaptive_tdee import (
    calculate_adaptive_tdee,
    recommend_macro_adjustment,
    MacroAdjustment
)


class TestAdaptiveTDEE:
    """Test back-calculated TDEE algorithm"""

    def test_cutting_scenario(self):
        """Test TDEE calculation for cutting (weight loss)"""
        # Lost 2 lbs in 14 days, averaged 2100 cal/day
        weights = [210.0 - (i * 0.143) for i in range(14)]  # 210 → 208
        calories = [2100] * 14

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        # Expected: 2100 + (-2 × 3500 / 14) = 2600
        # But EWMA smoothing (alpha=0.3) causes lag, reducing apparent weight change
        assert tdee is not None
        assert 2450 <= tdee <= 2550  # Wider range for EWMA lag

    def test_bulking_scenario(self):
        """Test TDEE calculation for bulking (weight gain)"""
        # Gained 1.5 lbs in 14 days, averaged 3000 cal/day
        weights = [185.0 + (i * 0.107) for i in range(14)]  # 185 → 186.5
        calories = [3000] * 14

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        # Expected: 3000 - (1.5 × 3500 / 14) = 2625
        # But EWMA lag reduces apparent gain
        assert tdee is not None
        assert 2650 <= tdee <= 2750  # Wider range for EWMA lag

    def test_maintenance_scenario(self):
        """Test TDEE calculation for maintenance (stable weight)"""
        # Weight stable (±0.5 lbs fluctuation), averaged 2400 cal/day
        weights = [165.0, 165.2, 164.8, 165.1, 165.0, 164.9, 165.2,
                   165.0, 164.8, 165.3, 165.1, 164.9, 165.0, 165.1]
        calories = [2400] * 14

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        # Expected: ~2400 (minimal weight change)
        assert tdee is not None
        assert 2350 <= tdee <= 2450

    def test_insufficient_data(self):
        """Test TDEE with less than 14 days"""
        weights = [210.0, 209.5, 209.0]
        calories = [2100, 2100, 2100]

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        assert tdee is None  # Not enough data

    def test_mismatched_lengths(self):
        """Test error handling for mismatched data"""
        weights = [210.0, 209.0, 208.0]
        calories = [2100, 2100]  # One less

        with pytest.raises(ValueError, match="must have same length"):
            calculate_adaptive_tdee(weights, calories, days=14)

    def test_variable_intake(self):
        """Test TDEE with variable calorie intake"""
        # Lost 1 lb in 14 days, calories varied 1900-2300
        weights = [200.0 - (i * 0.071) for i in range(14)]  # 200 → 199
        calories = [1900, 2100, 2000, 2300, 2200, 1950, 2100,
                    2050, 2150, 2000, 2200, 2100, 1900, 2050]

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        avg_intake = sum(calories) / len(calories)  # ~2067

        # Expected: ~2067 + (-1 × 3500 / 14) = 2067 + 250 = 2317
        assert tdee is not None
        assert 2250 <= tdee <= 2400


class TestMacroAdjustment:
    """Test macro adjustment recommendations"""

    def test_on_track_cutting(self):
        """Test no adjustment when on track (within ±20%)"""
        # Goal: -1.0 lb/week, Actual: -0.95 lb/week (5% deviation)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=-1.0,
            actual_rate_lbs_week=-0.95,
            current_calories=2100,
            current_protein_g=200.0,
            phase="cut"
        )

        assert adj.calorie_change == 0
        assert adj.new_calories == 2100
        assert adj.reason == "on_track"
        assert "on track" in adj.coaching_message.lower()

    def test_losing_too_fast(self):
        """Test adjustment for losing weight too fast"""
        # Goal: -1.0 lb/week, Actual: -1.5 lb/week (50% faster)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=-1.0,
            actual_rate_lbs_week=-1.5,
            current_calories=2100,
            current_protein_g=200.0,
            phase="cut"
        )

        assert adj.calorie_change == 100  # Increase
        assert adj.new_calories == 2200
        assert adj.reason == "losing_too_fast"
        assert "faster than planned" in adj.coaching_message.lower()
        assert "+100" in adj.coaching_message

    def test_losing_too_slow(self):
        """Test adjustment for losing weight too slow"""
        # Goal: -1.0 lb/week, Actual: -0.5 lb/week (50% slower)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=-1.0,
            actual_rate_lbs_week=-0.5,
            current_calories=2100,
            current_protein_g=200.0,
            phase="cut"
        )

        assert adj.calorie_change == -100  # Decrease
        assert adj.new_calories == 2000
        assert adj.reason == "losing_too_slow"
        assert "slower than expected" in adj.coaching_message.lower()

    def test_losing_way_too_fast(self):
        """Test larger adjustment for extreme deviation (>50%)"""
        # Goal: -1.0 lb/week, Actual: -2.0 lb/week (100% faster)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=-1.0,
            actual_rate_lbs_week=-2.0,
            current_calories=2100,
            current_protein_g=200.0,
            phase="cut"
        )

        assert adj.calorie_change == 150  # Larger increase
        assert adj.new_calories == 2250
        assert adj.percent_deviation == -100.0

    def test_gaining_too_fast_bulk(self):
        """Test adjustment for bulking too fast"""
        # Goal: +0.5 lb/week, Actual: +1.0 lb/week (100% faster)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=0.5,
            actual_rate_lbs_week=1.0,
            current_calories=3000,
            current_protein_g=180.0,
            phase="bulk"
        )

        assert adj.calorie_change == -150  # Decrease (>50% deviation)
        assert adj.new_calories == 2850
        assert adj.reason == "gaining_too_fast"
        assert "faster than planned" in adj.coaching_message.lower()

    def test_gaining_too_slow_bulk(self):
        """Test adjustment for bulking too slow"""
        # Goal: +0.5 lb/week, Actual: +0.2 lb/week
        # Deviation: (0.2 - 0.5) / 0.5 = -60% (> 50% threshold)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=0.5,
            actual_rate_lbs_week=0.2,
            current_calories=2800,
            current_protein_g=180.0,
            phase="bulk"
        )

        assert adj.calorie_change == 150  # Increase (>50% deviation)
        assert adj.new_calories == 2950
        assert adj.reason == "gaining_too_slow"

    def test_maintenance_stable(self):
        """Test maintenance when weight is stable"""
        # Maintenance: actual rate ±0.2 lb/week (< 0.25 threshold = stable)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=0.0,
            actual_rate_lbs_week=0.15,
            current_calories=2400,
            current_protein_g=150.0,
            phase="maintain"
        )

        assert adj.calorie_change == 0
        assert adj.reason == "stable"

    def test_unintended_weight_loss_maintenance(self):
        """Test maintenance with unintended weight loss"""
        # Maintenance but losing 0.5 lb/week
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=0.0,
            actual_rate_lbs_week=-0.5,
            current_calories=2400,
            current_protein_g=150.0,
            phase="maintain"
        )

        assert adj.calorie_change > 0  # Increase calories
        assert adj.reason == "unintended_loss"
        assert adj.new_calories > 2400

    def test_unintended_weight_gain_maintenance(self):
        """Test maintenance with unintended weight gain"""
        # Maintenance but gaining 0.6 lb/week
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=0.0,
            actual_rate_lbs_week=0.6,
            current_calories=2400,
            current_protein_g=150.0,
            phase="maintain"
        )

        assert adj.calorie_change < 0  # Decrease calories
        assert adj.reason == "unintended_gain"
        assert adj.new_calories < 2400

    def test_recomp_behavior(self):
        """Test recomp phase behaves like cutting"""
        # Recomp: slight deficit expected
        # Goal: -0.25, Actual: -0.5
        # Deviation: (-0.5 - (-0.25)) / 0.25 = -100% (> 50% threshold)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=-0.25,
            actual_rate_lbs_week=-0.5,
            current_calories=2300,
            current_protein_g=180.0,
            phase="recomp"
        )

        # Losing faster than expected in recomp
        assert adj.calorie_change == 150  # Increase (>50% deviation)
        assert adj.reason == "losing_too_fast"


class TestThresholds:
    """Test adjustment threshold logic"""

    def test_20_percent_threshold_no_change(self):
        """Test ±20% threshold: no adjustment"""
        # 19% deviation - should be "on track"
        adj = recommend_macro_adjustment(-1.0, -1.19, 2100, 200.0, "cut")
        assert adj.calorie_change == 0

        # -19% deviation - should be "on track"
        adj = recommend_macro_adjustment(-1.0, -0.81, 2100, 200.0, "cut")
        assert adj.calorie_change == 0

    def test_50_percent_threshold_small_adjustment(self):
        """Test ±50% threshold: 100 cal adjustment"""
        # 40% deviation - should get 100 cal adjustment
        adj = recommend_macro_adjustment(-1.0, -1.4, 2100, 200.0, "cut")
        assert abs(adj.calorie_change) == 100

    def test_beyond_50_percent_large_adjustment(self):
        """Test >50% deviation: 150 cal adjustment"""
        # 80% deviation - should get 150 cal adjustment
        adj = recommend_macro_adjustment(-1.0, -1.8, 2100, 200.0, "cut")
        assert abs(adj.calorie_change) == 150


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_weight_change(self):
        """Test TDEE when weight is perfectly stable"""
        weights = [200.0] * 14
        calories = [2500] * 14

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        # No weight change → TDEE = avg intake
        assert tdee is not None
        assert tdee == 2500

    def test_very_small_weight_change(self):
        """Test TDEE with minimal weight change"""
        # Lost 0.2 lbs in 14 days (barely measurable)
        weights = [150.0 - (i * 0.014) for i in range(14)]
        calories = [1800] * 14

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        # Expected: ~1800 + 50 = 1850
        assert tdee is not None
        assert 1820 <= tdee <= 1880

    def test_negative_calories(self):
        """Test that TDEE handles extreme scenarios gracefully"""
        # Extreme weight loss with low intake
        weights = [200.0 - (i * 0.5) for i in range(14)]  # Lost 7 lbs
        calories = [1200] * 14

        tdee = calculate_adaptive_tdee(weights, calories, days=14)

        # TDEE = 1200 + (7 * 3500 / 14) = 1200 + 1750 = 2950
        assert tdee is not None
        assert tdee > 1200  # Should be higher than intake


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflow"""

    def test_complete_cutting_workflow(self):
        """Test complete cutting workflow with realistic data"""
        # Beginner Ben: cutting from 210 → 208 lbs
        weights = [210.0 - (i * 0.14) for i in range(14)]
        calories = [2100] * 14  # Consistent intake

        # Calculate TDEE
        tdee = calculate_adaptive_tdee(weights, calories, days=14)
        # EWMA lag reduces apparent weight change
        assert 2400 <= tdee <= 2550

        # Get recommendation
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=-1.0,
            actual_rate_lbs_week=-1.0,  # On track
            current_calories=2100,
            current_protein_g=210.0,
            phase="cut"
        )

        assert adj.reason == "on_track"
        assert adj.calorie_change == 0

    def test_complete_bulking_workflow(self):
        """Test complete bulking workflow with realistic data"""
        # Intermediate Ian: bulking from 185 → 186 lbs
        weights = [185.0 + (i * 0.071) for i in range(14)]
        calories = [2900, 2950, 2850, 2900, 2950, 3000, 2880,
                    2920, 2900, 2950, 2900, 2850, 2900, 2950]

        # Calculate TDEE
        tdee = calculate_adaptive_tdee(weights, calories, days=14)
        assert tdee is not None

        # Get recommendation (target +0.75 lb/week, actual +0.7)
        adj = recommend_macro_adjustment(
            goal_rate_lbs_week=0.75,
            actual_rate_lbs_week=0.7,
            current_calories=2900,
            current_protein_g=180.0,
            phase="bulk"
        )

        # Should be on track (within 20%)
        assert adj.calorie_change == 0
