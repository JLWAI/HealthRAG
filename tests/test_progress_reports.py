"""
Unit Tests for Monthly Progress Reports

Tests monthly progress report generation with comprehensive analytics
combining weight, TDEE, measurements, nutrition, and workout data.
"""

import pytest
import os
import tempfile
from datetime import date, timedelta
from unittest.mock import Mock, MagicMock, patch

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from progress_reports import (
    MonthlyProgressReport,
    generate_monthly_progress_report,
    create_monthly_report_visualization
)
from adaptive_tdee import WeightEntry, WeightTracker
from tdee_analytics import TDEESnapshot, TDEEHistoricalTracker
from body_measurements import BodyMeasurement, MeasurementComparison, BodyMeasurementTracker
from workout_models import WorkoutSession


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


class TestMonthlyProgressReportGeneration:
    """Test monthly progress report generation with mocked dependencies"""

    @pytest.fixture
    def mock_trackers(self):
        """Create mocked tracker instances for testing"""
        # Create temporary databases for real trackers
        with tempfile.NamedTemporaryFile(delete=False, suffix='_weight.db') as f:
            weight_db = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='_tdee.db') as f:
            tdee_db = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='_measurements.db') as f:
            measurements_db = f.name

        weight_tracker = WeightTracker(db_path=weight_db)
        tdee_tracker = TDEEHistoricalTracker(db_path=tdee_db)
        measurement_tracker = BodyMeasurementTracker(db_path=measurements_db)
        food_logger = Mock()
        workout_db = Mock()

        yield {
            'weight': weight_tracker,
            'tdee': tdee_tracker,
            'measurements': measurement_tracker,
            'food': food_logger,
            'workout': workout_db,
            'db_paths': [weight_db, tdee_db, measurements_db]
        }

        # Cleanup
        for db_path in [weight_db, tdee_db, measurements_db]:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_generate_report_cutting_phase_success(self, mock_trackers):
        """Test generating report for successful cutting phase"""
        # Setup weight data (losing 8 lbs over 4 weeks)
        base_date = date(2025, 10, 1)
        for i in range(28):  # 4 weeks
            log_date = (base_date + timedelta(days=i)).isoformat()
            weight = 210.0 - (i * 0.29)  # ~8 lbs over 28 days
            mock_trackers['weight'].log_weight(weight, log_date=log_date)

        # Setup TDEE snapshots (weekly)
        for i in range(4):
            snapshot = create_test_snapshot(
                date=(base_date + timedelta(weeks=i)).isoformat(),
                adaptive_tdee=2350 - i * 10
            )
            mock_trackers['tdee'].save_snapshot(snapshot)

        # Setup body measurements
        m_start = BodyMeasurement(
            measurement_id=None,
            date="2025-10-01",
            waist_inches=38.0,
            chest_inches=42.0,
            bicep_left_inches=15.0
        )
        m_end = BodyMeasurement(
            measurement_id=None,
            date="2025-10-28",
            waist_inches=36.0,
            chest_inches=42.0,
            bicep_left_inches=15.1
        )
        mock_trackers['measurements'].log_measurements(m_start)
        mock_trackers['measurements'].log_measurements(m_end)

        # Mock food logger
        mock_summary = Mock()
        mock_summary.entries_logged = 1
        mock_summary.total_calories = 2100
        mock_summary.total_protein = 210
        mock_trackers['food'].get_daily_summary = Mock(return_value=mock_summary)

        # Mock workout database
        mock_session = Mock()
        mock_session.session_id = 1
        mock_trackers['workout'].get_sessions_in_date_range = Mock(return_value=[mock_session] * 16)
        mock_trackers['workout'].get_sets_by_session = Mock(return_value=[])

        # Generate report
        report = generate_monthly_progress_report(
            month=10,
            year=2025,
            weight_tracker=mock_trackers['weight'],
            tdee_tracker=mock_trackers['tdee'],
            measurement_tracker=mock_trackers['measurements'],
            food_logger=mock_trackers['food'],
            workout_db=mock_trackers['workout'],
            phase="cut"
        )

        # Verify report
        assert report is not None
        assert report.phase == "cut"
        assert report.start_weight_lbs == pytest.approx(210.0, abs=0.1)
        assert report.end_weight_lbs == pytest.approx(202.0, abs=1.0)
        assert report.trend_weight_change_lbs is not None
        assert report.trend_weight_change_lbs < 0  # Weight should be down

        # Verify achievements were detected
        assert len(report.achievements) > 0

        # Verify overall rating
        assert report.overall_rating in ["Excellent", "Good", "Fair", "Needs Attention"]

    def test_generate_report_bulking_phase(self, mock_trackers):
        """Test generating report for bulking phase"""
        # Setup weight data (gaining 3 lbs over 4 weeks)
        base_date = date(2025, 10, 1)
        for i in range(28):
            log_date = (base_date + timedelta(days=i)).isoformat()
            weight = 180.0 + (i * 0.11)  # ~3 lbs gain
            mock_trackers['weight'].log_weight(weight, log_date=log_date)

        # Setup TDEE snapshots
        for i in range(4):
            snapshot = create_test_snapshot(
                date=(base_date + timedelta(weeks=i)).isoformat(),
                formula_tdee=2800,
                adaptive_tdee=2850 + i * 10,
                tdee_delta=50,
                goal_rate_lbs_week=0.75,
                recommended_calories=3200,
                recommended_protein_g=200.0,
                recommended_carbs_g=350.0,
                recommended_fat_g=90.0,
                phase="bulk"
            )
            mock_trackers['tdee'].save_snapshot(snapshot)

        # Mock other dependencies
        mock_trackers['food'].get_daily_summary = Mock(return_value=Mock(entries_logged=1, total_calories=3200, total_protein=200))
        mock_trackers['workout'].get_sessions_in_date_range = Mock(return_value=[Mock(session_id=i) for i in range(16)])
        mock_trackers['workout'].get_sets_by_session = Mock(return_value=[])

        # Generate report
        report = generate_monthly_progress_report(
            month=10,
            year=2025,
            weight_tracker=mock_trackers['weight'],
            tdee_tracker=mock_trackers['tdee'],
            measurement_tracker=mock_trackers['measurements'],
            food_logger=mock_trackers['food'],
            workout_db=mock_trackers['workout'],
            phase="bulk"
        )

        # Verify bulking progress
        assert report.phase == "bulk"
        assert report.trend_weight_change_lbs is not None
        assert report.trend_weight_change_lbs > 0  # Weight should be up
        assert len(report.achievements) > 0

    def test_generate_report_low_compliance(self, mock_trackers):
        """Test report with poor tracking compliance"""
        # Minimal weight data
        base_date = date(2025, 10, 1)
        mock_trackers['weight'].log_weight(210.0, log_date=base_date.isoformat())
        mock_trackers['weight'].log_weight(209.0, log_date=(base_date + timedelta(days=27)).isoformat())

        # Mock food logger with low compliance (only 10 days logged)
        call_count = 0
        def mock_summary(date_str):
            nonlocal call_count
            call_count += 1
            if call_count <= 10:  # Only 10 days logged
                return Mock(entries_logged=1, total_calories=2100, total_protein=210)
            else:
                return Mock(entries_logged=0, total_calories=0, total_protein=0)

        mock_trackers['food'].get_daily_summary = mock_summary

        # Mock minimal workouts (only 6 sessions)
        mock_trackers['workout'].get_sessions_in_date_range = Mock(return_value=[Mock(session_id=i) for i in range(6)])
        mock_trackers['workout'].get_sets_by_session = Mock(return_value=[])

        # Generate report
        report = generate_monthly_progress_report(
            month=10,
            year=2025,
            weight_tracker=mock_trackers['weight'],
            tdee_tracker=mock_trackers['tdee'],
            measurement_tracker=mock_trackers['measurements'],
            food_logger=mock_trackers['food'],
            workout_db=mock_trackers['workout'],
            phase="cut"
        )

        # Verify poor compliance detected
        assert report.nutrition_compliance_pct < 50
        assert report.workouts_completed < 12
        assert len(report.areas_for_improvement) > 0
        assert len(report.recommendations) > 0
        assert report.overall_rating in ["Fair", "Needs Attention"]

    def test_generate_report_with_measurements(self, mock_trackers):
        """Test report including body measurement changes"""
        # Setup weight
        base_date = date(2025, 10, 1)
        mock_trackers['weight'].log_weight(210.0, log_date=base_date.isoformat())
        mock_trackers['weight'].log_weight(205.0, log_date=(base_date + timedelta(days=27)).isoformat())

        # Setup measurements showing fat loss + muscle retention
        m_start = BodyMeasurement(
            measurement_id=None,
            date="2025-10-01",
            waist_inches=38.0,
            chest_inches=42.0,
            bicep_left_inches=15.0,
            bicep_right_inches=15.0
        )
        m_end = BodyMeasurement(
            measurement_id=None,
            date="2025-10-28",
            waist_inches=36.0,  # Fat loss
            chest_inches=42.0,  # Maintained
            bicep_left_inches=15.2,  # Slight muscle gain
            bicep_right_inches=15.2
        )
        mock_trackers['measurements'].log_measurements(m_start)
        mock_trackers['measurements'].log_measurements(m_end)

        # Mock other dependencies
        mock_trackers['food'].get_daily_summary = Mock(return_value=Mock(entries_logged=1, total_calories=2100, total_protein=210))
        mock_trackers['workout'].get_sessions_in_date_range = Mock(return_value=[Mock(session_id=i) for i in range(16)])
        mock_trackers['workout'].get_sets_by_session = Mock(return_value=[])

        # Generate report
        report = generate_monthly_progress_report(
            month=10,
            year=2025,
            weight_tracker=mock_trackers['weight'],
            tdee_tracker=mock_trackers['tdee'],
            measurement_tracker=mock_trackers['measurements'],
            food_logger=mock_trackers['food'],
            workout_db=mock_trackers['workout'],
            phase="cut"
        )

        # Verify measurement comparison included
        assert report.measurement_changes is not None
        assert report.measurement_changes.changes['waist_inches'] < 0  # Waist decreased
        assert report.measurement_changes.changes['bicep_left_inches'] > 0  # Bicep increased

        # Should have achievement for muscle retention
        achievement_text = " ".join(report.achievements).lower()
        assert "waist" in achievement_text or "arms" in achievement_text

    def test_generate_report_metabolic_adaptation(self, mock_trackers):
        """Test report detecting significant metabolic adaptation"""
        # Setup weight
        base_date = date(2025, 10, 1)
        mock_trackers['weight'].log_weight(210.0, log_date=base_date.isoformat())

        # Setup TDEE showing significant drop (metabolic adaptation)
        snapshot_start = create_test_snapshot(
            date="2025-10-01",
            adaptive_tdee=2400,
            tdee_delta=0
        )
        snapshot_end = create_test_snapshot(
            date="2025-10-28",
            adaptive_tdee=2150,  # 250 cal drop!
            tdee_delta=-250,
            recommended_calories=1850,
            calorie_adjustment=-250
        )
        mock_trackers['tdee'].save_snapshot(snapshot_start)
        mock_trackers['tdee'].save_snapshot(snapshot_end)

        # Mock other dependencies
        mock_trackers['food'].get_daily_summary = Mock(return_value=Mock(entries_logged=1, total_calories=2100, total_protein=210))
        mock_trackers['workout'].get_sessions_in_date_range = Mock(return_value=[Mock(session_id=i) for i in range(12)])
        mock_trackers['workout'].get_sets_by_session = Mock(return_value=[])

        # Generate report
        report = generate_monthly_progress_report(
            month=10,
            year=2025,
            weight_tracker=mock_trackers['weight'],
            tdee_tracker=mock_trackers['tdee'],
            measurement_tracker=mock_trackers['measurements'],
            food_logger=mock_trackers['food'],
            workout_db=mock_trackers['workout'],
            phase="cut"
        )

        # Verify metabolic adaptation detected
        assert report.tdee_change == -250
        assert report.metabolic_adaptation_pct is not None

        # Should have recommendation about diet break or reverse diet
        recommendations_text = " ".join(report.recommendations).lower()
        assert "diet break" in recommendations_text or "reverse diet" in recommendations_text


class TestMonthlyReportVisualization:
    """Test monthly report visualization"""

    def test_create_monthly_report_visualization(self):
        """Test creating Plotly visualization for monthly report"""
        # Create sample report
        report = MonthlyProgressReport(
            month_start="2025-10-01",
            month_end="2025-10-31",
            phase="cut",
            start_weight_lbs=210.0,
            end_weight_lbs=205.0,
            weight_change_lbs=-5.0,
            trend_weight_change_lbs=-4.5,
            measurement_changes=None,
            avg_daily_calories=2100.0,
            avg_daily_protein_g=210.0,
            nutrition_compliance_pct=85.0,
            days_logged=26,
            start_tdee=2400,
            end_tdee=2350,
            tdee_change=-50,
            metabolic_adaptation_pct=-2.1,
            workouts_completed=16,
            total_volume_kg=12000.0,
            volume_change_pct=None,
            achievements=["Lost 4.5 lbs", "Excellent tracking"],
            areas_for_improvement=[],
            recommendations=["Continue current approach"],
            overall_rating="Excellent",
            summary="Outstanding month!"
        )

        fig = create_monthly_report_visualization(report)

        assert fig is not None
        # Should have 4 subplots (2 rows x 2 cols)
        assert len(fig.data) == 4

    def test_create_visualization_cutting_phase(self):
        """Test visualization shows correct indicators for cutting"""
        report = MonthlyProgressReport(
            month_start="2025-10-01",
            month_end="2025-10-31",
            phase="cut",
            start_weight_lbs=210.0,
            end_weight_lbs=205.0,
            weight_change_lbs=-5.0,
            trend_weight_change_lbs=-5.0,
            measurement_changes=None,
            avg_daily_calories=2100.0,
            avg_daily_protein_g=210.0,
            nutrition_compliance_pct=90.0,
            days_logged=28,
            start_tdee=2400,
            end_tdee=2350,
            tdee_change=-50,
            metabolic_adaptation_pct=-2.1,
            workouts_completed=16,
            total_volume_kg=12000.0,
            volume_change_pct=None,
            achievements=[],
            areas_for_improvement=[],
            recommendations=[],
            overall_rating="Excellent",
            summary="Great month"
        )

        fig = create_monthly_report_visualization(report)
        assert fig is not None

    def test_create_visualization_bulking_phase(self):
        """Test visualization shows correct indicators for bulking"""
        report = MonthlyProgressReport(
            month_start="2025-10-01",
            month_end="2025-10-31",
            phase="bulk",
            start_weight_lbs=180.0,
            end_weight_lbs=183.0,
            weight_change_lbs=3.0,
            trend_weight_change_lbs=3.0,
            measurement_changes=None,
            avg_daily_calories=3200.0,
            avg_daily_protein_g=200.0,
            nutrition_compliance_pct=85.0,
            days_logged=26,
            start_tdee=2800,
            end_tdee=2850,
            tdee_change=50,
            metabolic_adaptation_pct=1.8,
            workouts_completed=16,
            total_volume_kg=15000.0,
            volume_change_pct=None,
            achievements=[],
            areas_for_improvement=[],
            recommendations=[],
            overall_rating="Good",
            summary="Solid bulk"
        )

        fig = create_monthly_report_visualization(report)
        assert fig is not None


@pytest.mark.integration
class TestProgressReportWorkflow:
    """Integration tests for complete progress report workflow"""

    def test_complete_monthly_report_workflow(self):
        """Test generating complete monthly report with real trackers"""
        # Create temporary databases
        with tempfile.NamedTemporaryFile(delete=False, suffix='_weight.db') as f:
            weight_db = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='_tdee.db') as f:
            tdee_db = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='_measurements.db') as f:
            measurements_db = f.name

        # Initialize trackers
        weight_tracker = WeightTracker(db_path=weight_db)
        tdee_tracker = TDEEHistoricalTracker(db_path=tdee_db)
        measurement_tracker = BodyMeasurementTracker(db_path=measurements_db)

        # Populate data for October 2025
        base_date = date(2025, 10, 1)

        # Weight data (cutting: 210 → 205 lbs)
        for i in range(31):
            log_date = (base_date + timedelta(days=i)).isoformat()
            weight = 210.0 - (i * 0.16)
            weight_tracker.log_weight(weight, log_date=log_date)

        # TDEE snapshots (weekly)
        for week in range(4):
            snapshot = create_test_snapshot(
                date=(base_date + timedelta(weeks=week)).isoformat(),
                adaptive_tdee=2350 - week * 15,
                weight_lbs=210.0 - week * 1.25,
                trend_weight_lbs=210.0 - week * 1.2,
                weight_change_14d=-1.2,
                actual_rate_lbs_week=-1.0,
                percent_deviation=0.0
            )
            tdee_tracker.save_snapshot(snapshot)

        # Body measurements
        m_start = BodyMeasurement(
            measurement_id=None,
            date="2025-10-01",
            waist_inches=38.0,
            chest_inches=42.0
        )
        m_end = BodyMeasurement(
            measurement_id=None,
            date="2025-10-31",
            waist_inches=36.5,
            chest_inches=42.0
        )
        measurement_tracker.log_measurements(m_start)
        measurement_tracker.log_measurements(m_end)

        # Mock food logger and workout DB
        food_logger = Mock()
        food_logger.get_daily_summary = Mock(return_value=Mock(entries_logged=1, total_calories=2100, total_protein=210))

        workout_db = Mock()
        workout_db.get_sessions_in_date_range = Mock(return_value=[Mock(session_id=i) for i in range(16)])
        workout_db.get_sets_by_session = Mock(return_value=[])

        # Generate report
        report = generate_monthly_progress_report(
            month=10,
            year=2025,
            weight_tracker=weight_tracker,
            tdee_tracker=tdee_tracker,
            measurement_tracker=measurement_tracker,
            food_logger=food_logger,
            workout_db=workout_db,
            phase="cut"
        )

        # Verify comprehensive report
        assert report is not None
        assert report.phase == "cut"
        assert report.start_weight_lbs == pytest.approx(210.0, abs=0.1)
        assert report.end_weight_lbs == pytest.approx(205.0, abs=1.0)
        assert report.trend_weight_change_lbs < 0
        assert report.measurement_changes is not None
        assert report.workouts_completed == 16
        assert report.overall_rating in ["Excellent", "Good", "Fair", "Needs Attention"]
        assert len(report.summary) > 0

        # Generate visualization
        fig = create_monthly_report_visualization(report)
        assert fig is not None

        # Cleanup
        os.remove(weight_db)
        os.remove(tdee_db)
        os.remove(measurements_db)
