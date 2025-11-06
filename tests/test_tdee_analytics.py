"""
Unit Tests for TDEE Analytics System

Tests TDEE snapshot tracking, chart generation, water weight detection,
goal prediction, and data export functionality.
"""

import pytest
import os
import tempfile
import json
import csv
from datetime import date, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tdee_analytics import (
    TDEESnapshot,
    WaterWeightAlert,
    GoalPrediction,
    TDEEHistoricalTracker,
    create_tdee_trend_chart,
    create_weight_progress_chart,
    detect_water_weight_spikes,
    predict_goal_date,
    export_tdee_data_csv,
    export_tdee_data_json,
    generate_weekly_comparison
)


def create_test_snapshot(**kwargs):
    """Helper to create TDEESnapshot with defaults for testing"""
    defaults = {
        'snapshot_id': None,
        'date': "2025-10-15",
        'formula_tdee': 2400,
        'adaptive_tdee': 2350,
        'tdee_delta': -50,
        'average_intake_14d': 2100.0,
        'weight_lbs': 210.0,
        'trend_weight_lbs': 209.5,
        'weight_change_14d': -2.0,
        'goal_rate_lbs_week': -1.0,
        'actual_rate_lbs_week': -1.2,
        'percent_deviation': 20.0,
        'recommended_calories': 2100,
        'calorie_adjustment': 0,
        'recommended_protein_g': 210.0,
        'recommended_carbs_g': 200.0,
        'recommended_fat_g': 70.0,
        'phase': "cut"
    }
    defaults.update(kwargs)
    return TDEESnapshot(**defaults)


class TestTDEEHistoricalTracker:
    """Test TDEEHistoricalTracker database operations"""

    @pytest.fixture
    def tracker(self):
        """Create temporary TDEE tracker for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = TDEEHistoricalTracker(db_path=db_path)
        yield tracker

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_init_creates_database(self, tracker):
        """Test that initialization creates database"""
        assert os.path.exists(tracker.db_path)

    def test_save_snapshot_basic(self, tracker):
        """Test saving a basic TDEE snapshot"""
        snapshot = create_test_snapshot(
            confidence_score=0.85
        )

        snapshot_id = tracker.save_snapshot(snapshot)
        assert snapshot_id > 0

        # Retrieve and verify
        snapshots = tracker.get_snapshots()
        assert len(snapshots) == 1
        assert snapshots[0].adaptive_tdee == 2350
        assert snapshots[0].phase == "cut"

    def test_save_snapshot_duplicate_date_replaces(self, tracker):
        """Test that saving same date replaces old snapshot"""
        # First snapshot
        s1 = create_test_snapshot(
            date="2025-10-15",
            adaptive_tdee=2350,
            recommended_calories=2100
        )
        tracker.save_snapshot(s1)

        # Second snapshot (same date, different TDEE)
        s2 = create_test_snapshot(
            date="2025-10-15",
            adaptive_tdee=2320,  # Updated
            tdee_delta=-80,
            recommended_calories=2050,  # Updated
            calorie_adjustment=-50,
            recommended_carbs_g=190.0
        )
        tracker.save_snapshot(s2)

        # Should only have 1 entry with updated values
        snapshots = tracker.get_snapshots()
        assert len(snapshots) == 1
        assert snapshots[0].adaptive_tdee == 2320
        assert snapshots[0].recommended_calories == 2050

    def test_get_snapshots_all(self, tracker):
        """Test retrieving all snapshots"""
        # Save 5 snapshots
        for i in range(5):
            snapshot = create_test_snapshot(
                date=(date(2025, 10, 1) + timedelta(days=i * 7)).isoformat(),
                adaptive_tdee=2350 - i * 10,
                tdee_delta=-50 - i * 10
            )
            tracker.save_snapshot(snapshot)

        snapshots = tracker.get_snapshots()
        assert len(snapshots) == 5

        # Should be ordered newest first
        assert snapshots[0].date == "2025-10-29"
        assert snapshots[-1].date == "2025-10-01"

    def test_get_snapshots_date_range(self, tracker):
        """Test filtering snapshots by date range"""
        # Save snapshots across 5 weeks
        for i in range(5):
            snapshot = create_test_snapshot(
                date=(date(2025, 10, 1) + timedelta(weeks=i)).isoformat()
            )
            tracker.save_snapshot(snapshot)

        # Get middle 3 weeks
        snapshots = tracker.get_snapshots(
            start_date="2025-10-08",
            end_date="2025-10-22"
        )

        assert len(snapshots) == 3

    def test_get_snapshots_limit(self, tracker):
        """Test limiting number of returned snapshots"""
        # Save 10 snapshots
        for i in range(10):
            snapshot = create_test_snapshot(
                date=(date(2025, 10, 1) + timedelta(days=i)).isoformat()
            )
            tracker.save_snapshot(snapshot)

        snapshots = tracker.get_snapshots(limit=5)
        assert len(snapshots) == 5

    def test_get_latest_snapshot(self, tracker):
        """Test retrieving most recent snapshot"""
        # Save 3 snapshots
        for i in range(3):
            snapshot = create_test_snapshot(
                date=(date(2025, 10, 1) + timedelta(days=i)).isoformat(),
                adaptive_tdee=2350 - i * 10
            )
            tracker.save_snapshot(snapshot)

        latest = tracker.get_latest_snapshot()
        assert latest is not None
        assert latest.date == "2025-10-03"
        assert latest.adaptive_tdee == 2330

    def test_get_latest_snapshot_empty(self, tracker):
        """Test getting latest when no snapshots exist"""
        latest = tracker.get_latest_snapshot()
        assert latest is None


class TestChartGeneration:
    """Test Plotly chart generation functions"""

    def test_create_tdee_trend_chart_empty(self):
        """Test chart creation with no data"""
        # Empty tuples for new caching-optimized signature
        fig = create_tdee_trend_chart(snapshot_dates=(), snapshot_data=())

        assert fig is not None
        # Should have annotation indicating no data
        assert len(fig.layout.annotations) > 0

    def test_create_tdee_trend_chart_with_data(self):
        """Test chart creation with snapshot data"""
        # Prepare data in tuple format for caching-optimized function
        dates = []
        data_tuples = []
        for i in range(10):
            date_str = (date(2025, 10, 1) + timedelta(days=i * 3)).isoformat()
            formula_tdee = 2400
            adaptive_tdee = 2350 - i * 5
            avg_intake = 2100.0 - i * 10

            dates.append(date_str)
            data_tuples.append((formula_tdee, adaptive_tdee, avg_intake))

        fig = create_tdee_trend_chart(
            snapshot_dates=tuple(dates),
            snapshot_data=tuple(data_tuples)
        )

        assert fig is not None
        assert len(fig.data) == 3  # Formula, Adaptive, Average Intake
        assert fig.layout.title.text == 'TDEE Trend Over Time'

    def test_create_weight_progress_chart_empty(self):
        """Test weight chart with no data"""
        # Empty tuples for new caching-optimized signature
        fig = create_weight_progress_chart(weight_dates=(), weight_data=())

        assert fig is not None
        # Should have annotation indicating no data
        assert len(fig.layout.annotations) > 0

    def test_create_weight_progress_chart_with_data(self):
        """Test weight chart with data"""
        # Prepare data in tuple format for caching-optimized function
        dates = []
        data_tuples = []
        for i in range(14):
            date_str = (date(2025, 10, 1) + timedelta(days=i)).isoformat()
            actual_weight = 210.0 - i * 0.5
            trend_weight = 210.0 - i * 0.4  # Smoother trend

            dates.append(date_str)
            data_tuples.append((actual_weight, trend_weight))

        fig = create_weight_progress_chart(
            weight_dates=tuple(dates),
            weight_data=tuple(data_tuples)
        )

        assert fig is not None
        assert len(fig.data) == 2  # Daily weight + Trend weight
        assert fig.layout.title.text == 'Weight Progress: Daily vs. Trend'


class TestWaterWeightDetection:
    """Test water weight spike detection"""

    def test_detect_water_weight_spikes_none(self):
        """Test detection with no spikes (normal fluctuation)"""
        weight_entries = []
        for i in range(7):
            date_str = (date(2025, 10, 1) + timedelta(days=i)).isoformat()
            actual = 210.0 - i * 0.3
            trend = 210.0 - i * 0.3
            weight_entries.append((date_str, actual, trend))

        alerts = detect_water_weight_spikes(weight_entries, threshold_lbs=2.0)
        assert len(alerts) == 0

    def test_detect_water_weight_spike_increase(self):
        """Test detection of water weight spike (increase)"""
        weight_entries = [
            ("2025-10-01", 210.0, 210.0),
            ("2025-10-02", 209.5, 209.7),
            ("2025-10-03", 212.0, 209.4),  # Spike: +2.6 lbs
            ("2025-10-04", 209.0, 209.3)
        ]

        alerts = detect_water_weight_spikes(weight_entries, threshold_lbs=2.0)
        assert len(alerts) == 1
        assert alerts[0].is_spike is True
        assert alerts[0].is_drop is False
        assert alerts[0].deviation_lbs == pytest.approx(2.6, abs=0.1)
        assert "sodium" in alerts[0].likely_causes[0].lower()

    def test_detect_water_weight_drop(self):
        """Test detection of water weight drop (decrease)"""
        weight_entries = [
            ("2025-10-01", 210.0, 210.0),
            ("2025-10-02", 209.7, 209.7),
            ("2025-10-03", 207.0, 209.4),  # Drop: -2.4 lbs
            ("2025-10-04", 209.2, 209.1)
        ]

        alerts = detect_water_weight_spikes(weight_entries, threshold_lbs=2.0)
        assert len(alerts) == 1
        assert alerts[0].is_spike is False
        assert alerts[0].is_drop is True
        assert alerts[0].deviation_lbs == pytest.approx(-2.4, abs=0.1)

    def test_detect_water_weight_custom_threshold(self):
        """Test detection with custom threshold"""
        weight_entries = [
            ("2025-10-01", 210.0, 210.0),
            ("2025-10-02", 211.5, 210.0),  # 1.5 lb spike
        ]

        # With 2.0 lb threshold: no alert
        alerts_high = detect_water_weight_spikes(weight_entries, threshold_lbs=2.0)
        assert len(alerts_high) == 0

        # With 1.0 lb threshold: alert
        alerts_low = detect_water_weight_spikes(weight_entries, threshold_lbs=1.0)
        assert len(alerts_low) == 1


class TestGoalPrediction:
    """Test goal date prediction"""

    def test_predict_goal_date_cutting(self):
        """Test prediction for cutting phase"""
        prediction = predict_goal_date(
            current_weight_lbs=210.0,
            goal_weight_lbs=200.0,
            current_rate_lbs_week=-1.0,
            data_days=30
        )

        assert prediction.weight_to_go == 10.0
        assert prediction.predicted_weeks == 10.0  # 10 lbs / 1 lb per week
        assert prediction.confidence == "High"  # 30 days of data

        # Verify alternative scenarios
        assert prediction.best_case_weeks < prediction.predicted_weeks
        assert prediction.worst_case_weeks > prediction.predicted_weeks

    def test_predict_goal_date_bulking(self):
        """Test prediction for bulking phase"""
        prediction = predict_goal_date(
            current_weight_lbs=180.0,
            goal_weight_lbs=195.0,
            current_rate_lbs_week=0.75,
            data_days=20
        )

        assert prediction.weight_to_go == 15.0
        assert prediction.predicted_weeks == 20.0  # 15 lbs / 0.75 lb per week
        assert prediction.confidence == "Medium"  # 20 days of data

    def test_predict_goal_date_slow_progress(self):
        """Test prediction with very slow progress"""
        prediction = predict_goal_date(
            current_weight_lbs=210.0,
            goal_weight_lbs=200.0,
            current_rate_lbs_week=-0.05,  # Very slow
            data_days=10
        )

        # Should use default slow rate (0.5 lb/week) due to minimal progress
        assert prediction.predicted_weeks > 10
        assert prediction.confidence == "Low"  # Only 10 days of data

    def test_predict_goal_date_zero_rate(self):
        """Test prediction with zero rate of change"""
        prediction = predict_goal_date(
            current_weight_lbs=210.0,
            goal_weight_lbs=200.0,
            current_rate_lbs_week=0.0,  # No progress
            data_days=14
        )

        # Should assume default slow cut rate
        assert prediction.predicted_weeks == 20.0  # 10 lbs / 0.5 lb per week


class TestDataExport:
    """Test CSV and JSON export functions"""

    def test_export_tdee_data_csv(self):
        """Test exporting snapshots to CSV"""
        snapshots = []
        for i in range(3):
            snapshot = create_test_snapshot(
                snapshot_id=i + 1,
                date=(date(2025, 10, 1) + timedelta(days=i * 7)).isoformat(),
                adaptive_tdee=2350 - i * 10,
                tdee_delta=-50 - i * 10
            )
            snapshots.append(snapshot)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            output_path = f.name

        export_tdee_data_csv(snapshots, output_path)

        # Verify file exists and has content
        assert os.path.exists(output_path)

        # Read and verify CSV
        with open(output_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 3
            assert rows[0]['formula_tdee'] == '2400'
            assert rows[0]['phase'] == 'cut'

        # Cleanup
        os.remove(output_path)

    def test_export_tdee_data_csv_empty_raises_error(self):
        """Test that exporting empty snapshots raises error"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            output_path = f.name

        with pytest.raises(ValueError, match="No snapshots to export"):
            export_tdee_data_csv([], output_path)

        # Cleanup
        os.remove(output_path)

    def test_export_tdee_data_json(self):
        """Test exporting snapshots to JSON"""
        snapshots = []
        for i in range(3):
            snapshot = create_test_snapshot(
                snapshot_id=i + 1,
                date=(date(2025, 10, 1) + timedelta(days=i * 7)).isoformat(),
                adaptive_tdee=2350 - i * 10,
                tdee_delta=-50 - i * 10
            )
            snapshots.append(snapshot)

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_path = f.name

        export_tdee_data_json(snapshots, output_path)

        # Verify file exists and has content
        assert os.path.exists(output_path)

        # Read and verify JSON
        with open(output_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 3
            assert data[0]['formula_tdee'] == 2400
            assert data[0]['phase'] == 'cut'

        # Cleanup
        os.remove(output_path)

    def test_export_tdee_data_json_empty_raises_error(self):
        """Test that exporting empty snapshots raises error"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_path = f.name

        with pytest.raises(ValueError, match="No snapshots to export"):
            export_tdee_data_json([], output_path)

        # Cleanup
        os.remove(output_path)


class TestWeeklyComparison:
    """Test weekly comparison function"""

    def test_generate_weekly_comparison_basic(self):
        """Test basic weekly comparison"""
        this_week = create_test_snapshot(
            snapshot_id=2,
            date="2025-10-15",
            adaptive_tdee=2320,
            tdee_delta=-80,
            average_intake_14d=2050.0,
            trend_weight_lbs=208.0,
            actual_rate_lbs_week=-1.1,
            recommended_calories=2050,
            calorie_adjustment=-50
        )

        last_week = create_test_snapshot(
            snapshot_id=1,
            date="2025-10-08",
            trend_weight_lbs=209.0,
            actual_rate_lbs_week=-1.0
        )

        comparison = generate_weekly_comparison(this_week, last_week)

        assert comparison['weight_change_lbs'] == -1.0
        assert comparison['tdee_change_cal'] == -30
        assert comparison['intake_change_cal'] == -50
        assert comparison['rate_change_lbs_week'] == pytest.approx(-0.1)
        assert "progress" in comparison['progress_summary'].lower()

    def test_generate_weekly_comparison_cutting_progress(self):
        """Test comparison summary for cutting phase with good progress"""
        this_week = create_test_snapshot(
            snapshot_id=2,
            date="2025-10-15",
            adaptive_tdee=2320,
            tdee_delta=-80,
            trend_weight_lbs=207.0,
            recommended_calories=2050,
            calorie_adjustment=-50
        )

        last_week = create_test_snapshot(
            snapshot_id=1,
            date="2025-10-08",
            trend_weight_lbs=208.5
        )

        comparison = generate_weekly_comparison(this_week, last_week)

        # Weight down 1.5 lbs during cut = good progress
        assert comparison['weight_change_lbs'] == -1.5
        assert "good" in comparison['progress_summary'].lower() or "excellent" in comparison['progress_summary'].lower()

    def test_generate_weekly_comparison_bulking_progress(self):
        """Test comparison summary for bulking phase"""
        this_week = create_test_snapshot(
            snapshot_id=2,
            date="2025-10-15",
            formula_tdee=2800,
            adaptive_tdee=2850,
            tdee_delta=50,
            trend_weight_lbs=186.0,
            goal_rate_lbs_week=0.5,
            recommended_calories=3200,
            recommended_protein_g=210.0,
            recommended_carbs_g=300.0,
            recommended_fat_g=90.0,
            phase="bulk"
        )

        last_week = create_test_snapshot(
            snapshot_id=1,
            date="2025-10-08",
            formula_tdee=2800,
            adaptive_tdee=2820,
            tdee_delta=20,
            trend_weight_lbs=185.5,
            goal_rate_lbs_week=0.5,
            recommended_calories=3200,
            recommended_protein_g=210.0,
            recommended_carbs_g=300.0,
            recommended_fat_g=90.0,
            phase="bulk"
        )

        comparison = generate_weekly_comparison(this_week, last_week)

        # Weight up 0.5 lbs during bulk = good controlled gain
        assert comparison['weight_change_lbs'] == 0.5
        assert "great" in comparison['progress_summary'].lower()


@pytest.mark.integration
class TestTDEEAnalyticsWorkflow:
    """Integration tests for complete TDEE analytics workflow"""

    def test_complete_analytics_workflow(self):
        """Test complete workflow: snapshots, charts, export"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = TDEEHistoricalTracker(db_path=db_path)

        # Save 4 weeks of snapshots
        snapshots = []
        for i in range(4):
            snapshot = create_test_snapshot(
                date=(date(2025, 10, 1) + timedelta(weeks=i)).isoformat(),
                adaptive_tdee=2350 - i * 20,
                tdee_delta=-50 - i * 20,
                average_intake_14d=2100.0 - i * 30,
                weight_lbs=210.0 - i * 2,
                trend_weight_lbs=210.0 - i * 1.8,
                weight_change_14d=-1.8,
                actual_rate_lbs_week=-1.3,
                percent_deviation=30.0,
                recommended_calories=2100 - i * 30,
                calorie_adjustment=-30 if i > 0 else 0,
                recommended_carbs_g=200.0 - i * 10,
                confidence_score=0.8 + i * 0.05
            )
            tracker.save_snapshot(snapshot)
            snapshots.append(snapshot)

        # Verify snapshots saved
        assert tracker.get_latest_snapshot() is not None

        # Generate charts (convert to tuple format)
        dates = tuple(s.date for s in snapshots)
        data_tuples = tuple((s.formula_tdee, s.adaptive_tdee, s.average_intake_14d) for s in snapshots)
        trend_chart = create_tdee_trend_chart(snapshot_dates=dates, snapshot_data=data_tuples)
        assert trend_chart is not None

        # Export to CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            csv_path = f.name
        export_tdee_data_csv(snapshots, csv_path)
        assert os.path.exists(csv_path)

        # Export to JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json_path = f.name
        export_tdee_data_json(snapshots, json_path)
        assert os.path.exists(json_path)

        # Weekly comparison
        comparison = generate_weekly_comparison(snapshots[-1], snapshots[-2])
        assert comparison is not None
        assert comparison['weight_change_lbs'] is not None

        # Cleanup
        os.remove(db_path)
        os.remove(csv_path)
        os.remove(json_path)
