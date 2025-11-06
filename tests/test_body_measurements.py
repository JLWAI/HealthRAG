"""
Unit Tests for Body Measurements Tracking System

Tests measurement logging, retrieval, comparison, and progress tracking.
"""

import pytest
import os
import tempfile
from datetime import date, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from body_measurements import (
    BodyMeasurement,
    MeasurementComparison,
    BodyMeasurementTracker
)


class TestBodyMeasurementTracker:
    """Test BodyMeasurementTracker database operations"""

    @pytest.fixture
    def tracker(self):
        """Create temporary measurement tracker for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = BodyMeasurementTracker(db_path=db_path)
        yield tracker

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_init_creates_database(self, tracker):
        """Test that initialization creates database"""
        assert os.path.exists(tracker.db_path)

    def test_log_measurements_full(self, tracker):
        """Test logging complete measurement set"""
        measurement = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            neck_inches=15.5,
            chest_inches=42.0,
            shoulders_inches=48.0,
            bicep_left_inches=15.0,
            bicep_right_inches=15.0,
            forearm_left_inches=12.0,
            forearm_right_inches=12.0,
            waist_inches=36.0,
            hips_inches=40.0,
            thigh_left_inches=24.0,
            thigh_right_inches=24.0,
            calf_left_inches=15.5,
            calf_right_inches=15.5,
            notes="Starting measurements"
        )

        measurement_id = tracker.log_measurements(measurement)
        assert measurement_id > 0

        # Retrieve and verify
        measurements = tracker.get_measurements()
        assert len(measurements) == 1
        assert measurements[0].waist_inches == 36.0
        assert measurements[0].chest_inches == 42.0

    def test_log_measurements_partial(self, tracker):
        """Test logging with only some measurements"""
        measurement = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=36.0,
            chest_inches=42.0,
            bicep_left_inches=15.0
            # Other fields left as None
        )

        measurement_id = tracker.log_measurements(measurement)
        assert measurement_id > 0

        retrieved = tracker.get_measurements()[0]
        assert retrieved.waist_inches == 36.0
        assert retrieved.neck_inches is None

    def test_log_measurements_duplicate_date_replaces(self, tracker):
        """Test that logging same date replaces old entry"""
        # First measurement
        m1 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=36.0,
            chest_inches=42.0
        )
        tracker.log_measurements(m1)

        # Second measurement (same date, different values)
        m2 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=35.5,
            chest_inches=42.5
        )
        tracker.log_measurements(m2)

        # Should only have 1 entry with updated values
        measurements = tracker.get_measurements()
        assert len(measurements) == 1
        assert measurements[0].waist_inches == 35.5
        assert measurements[0].chest_inches == 42.5

    def test_get_measurements_all(self, tracker):
        """Test retrieving all measurements"""
        # Log 3 measurements
        for i in range(3):
            m = BodyMeasurement(
                measurement_id=None,
                date=(date(2025, 10, 1) + timedelta(days=i)).isoformat(),
                waist_inches=36.0 - i * 0.5,
                chest_inches=42.0
            )
            tracker.log_measurements(m)

        measurements = tracker.get_measurements()
        assert len(measurements) == 3

        # Should be ordered newest first
        assert measurements[0].date == "2025-10-03"
        assert measurements[-1].date == "2025-10-01"

    def test_get_measurements_date_range(self, tracker):
        """Test filtering measurements by date range"""
        # Log measurements across 5 days
        for i in range(5):
            m = BodyMeasurement(
                measurement_id=None,
                date=(date(2025, 10, 1) + timedelta(days=i * 7)).isoformat(),
                waist_inches=36.0
            )
            tracker.log_measurements(m)

        # Get middle 3 weeks
        measurements = tracker.get_measurements(
            start_date="2025-10-08",
            end_date="2025-10-22"
        )

        assert len(measurements) == 3

    def test_get_measurements_limit(self, tracker):
        """Test limiting number of returned measurements"""
        # Log 10 measurements
        for i in range(10):
            m = BodyMeasurement(
                measurement_id=None,
                date=(date(2025, 10, 1) + timedelta(days=i)).isoformat(),
                waist_inches=36.0
            )
            tracker.log_measurements(m)

        measurements = tracker.get_measurements(limit=5)
        assert len(measurements) == 5

    def test_get_latest_measurement(self, tracker):
        """Test retrieving most recent measurement"""
        # Log 3 measurements
        for i in range(3):
            m = BodyMeasurement(
                measurement_id=None,
                date=(date(2025, 10, 1) + timedelta(days=i)).isoformat(),
                waist_inches=36.0 - i
            )
            tracker.log_measurements(m)

        latest = tracker.get_latest_measurement()
        assert latest is not None
        assert latest.date == "2025-10-03"
        assert latest.waist_inches == 34.0

    def test_get_latest_measurement_empty(self, tracker):
        """Test getting latest when no measurements exist"""
        latest = tracker.get_latest_measurement()
        assert latest is None

    def test_compare_measurements_basic(self, tracker):
        """Test comparing two measurement dates"""
        # Week 1
        m1 = BodyMeasurement(
            measurement_id=None,
            date="2025-09-01",
            waist_inches=36.0,
            chest_inches=42.0,
            bicep_left_inches=15.0,
            thigh_left_inches=24.0
        )
        tracker.log_measurements(m1)

        # Week 8
        m2 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-27",
            waist_inches=34.5,
            chest_inches=42.5,
            bicep_left_inches=15.2,
            thigh_left_inches=23.5
        )
        tracker.log_measurements(m2)

        comparison = tracker.compare_measurements("2025-10-27", "2025-09-01")

        assert comparison is not None
        assert comparison.days_between == 56  # 8 weeks
        assert comparison.changes['waist_inches'] == -1.5
        assert comparison.changes['chest_inches'] == 0.5
        assert comparison.changes['bicep_left_inches'] == 0.2
        assert comparison.total_inches_lost == 2.0  # Waist + thigh
        assert comparison.total_inches_gained == 0.7  # Chest + bicep
        assert comparison.net_change == pytest.approx(-1.3, abs=0.1)

    def test_compare_measurements_not_found(self, tracker):
        """Test comparison when one date doesn't exist"""
        m1 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-01",
            waist_inches=36.0
        )
        tracker.log_measurements(m1)

        comparison = tracker.compare_measurements("2025-10-01", "2025-09-01")
        assert comparison is None

    def test_get_measurement_progress(self, tracker):
        """Test getting measurement progress over time"""
        # Log measurements weekly for 12 weeks
        base_date = date.today() - timedelta(days=84)  # 12 weeks ago
        for i in range(12):
            m = BodyMeasurement(
                measurement_id=None,
                date=(base_date + timedelta(weeks=i)).isoformat(),
                waist_inches=36.0 - i * 0.2,
                chest_inches=42.0 + i * 0.1,
                bicep_left_inches=15.0 + i * 0.05
            )
            tracker.log_measurements(m)

        progress = tracker.get_measurement_progress(days=90)

        assert 'waist_inches' in progress
        assert 'chest_inches' in progress
        assert 'bicep_left_inches' in progress

        # Should have 12 data points
        assert len(progress['waist_inches']) == 12
        assert len(progress['chest_inches']) == 12

        # Verify values are tuples of (date, value)
        first_waist = progress['waist_inches'][0]
        assert isinstance(first_waist, tuple)
        assert len(first_waist) == 2
        assert first_waist[1] == 36.0

    def test_delete_measurement(self, tracker):
        """Test deleting measurement by date"""
        m = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=36.0
        )
        tracker.log_measurements(m)

        # Verify exists
        measurements = tracker.get_measurements()
        assert len(measurements) == 1

        # Delete
        deleted = tracker.delete_measurement("2025-10-15")
        assert deleted is True

        # Verify gone
        measurements = tracker.get_measurements()
        assert len(measurements) == 0

    def test_delete_measurement_not_found(self, tracker):
        """Test deleting nonexistent measurement"""
        deleted = tracker.delete_measurement("2025-01-01")
        assert deleted is False

    def test_calculate_waist_to_hip_ratio_male(self, tracker):
        """Test WHR calculation for male"""
        measurement = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=36.0,
            hips_inches=40.0
        )

        whr = tracker.calculate_waist_to_hip_ratio(measurement)
        assert whr == pytest.approx(0.9, abs=0.01)  # 36/40 = 0.9

    def test_calculate_waist_to_hip_ratio_female(self, tracker):
        """Test WHR calculation for female (typically lower)"""
        measurement = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=28.0,
            hips_inches=38.0
        )

        whr = tracker.calculate_waist_to_hip_ratio(measurement)
        assert whr == pytest.approx(0.737, abs=0.01)  # 28/38

    def test_calculate_waist_to_hip_ratio_missing_data(self, tracker):
        """Test WHR calculation with missing measurements"""
        # Missing hips
        m1 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            waist_inches=36.0
        )
        assert tracker.calculate_waist_to_hip_ratio(m1) is None

        # Missing waist
        m2 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-15",
            hips_inches=40.0
        )
        assert tracker.calculate_waist_to_hip_ratio(m2) is None


@pytest.mark.integration
class TestBodyMeasurementWorkflow:
    """Integration tests for complete measurement tracking workflow"""

    def test_cutting_phase_progress_tracking(self):
        """Test tracking measurements during a cutting phase"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = BodyMeasurementTracker(db_path=db_path)

        # Week 1 (starting)
        week1 = BodyMeasurement(
            measurement_id=None,
            date="2025-09-01",
            neck_inches=16.0,
            chest_inches=42.0,
            waist_inches=38.0,
            hips_inches=40.0,
            bicep_left_inches=15.0,
            bicep_right_inches=15.0,
            thigh_left_inches=24.0,
            thigh_right_inches=24.0,
            notes="Starting cut"
        )
        tracker.log_measurements(week1)

        # Week 4 (mid-point)
        week4 = BodyMeasurement(
            measurement_id=None,
            date="2025-09-29",
            neck_inches=15.8,
            chest_inches=42.0,
            waist_inches=37.0,
            hips_inches=39.5,
            bicep_left_inches=15.0,
            bicep_right_inches=15.0,
            thigh_left_inches=23.8,
            thigh_right_inches=23.8,
            notes="4 weeks in"
        )
        tracker.log_measurements(week4)

        # Week 8 (end)
        week8 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-27",
            neck_inches=15.5,
            chest_inches=42.0,
            waist_inches=35.5,
            hips_inches=39.0,
            bicep_left_inches=15.1,
            bicep_right_inches=15.1,
            thigh_left_inches=23.5,
            thigh_right_inches=23.5,
            notes="8 weeks complete"
        )
        tracker.log_measurements(week8)

        # Compare start to end
        comparison = tracker.compare_measurements("2025-10-27", "2025-09-01")

        assert comparison is not None
        assert comparison.days_between == 56

        # Verify fat loss (waist, hips down)
        assert comparison.changes['waist_inches'] == -2.5
        assert comparison.changes['hips_inches'] == -1.0

        # Verify muscle retention (chest same, biceps slightly up)
        assert comparison.changes['chest_inches'] == 0.0
        assert comparison.changes['bicep_left_inches'] == pytest.approx(0.1)

        # Calculate WHR improvement
        whr_start = tracker.calculate_waist_to_hip_ratio(week1)
        whr_end = tracker.calculate_waist_to_hip_ratio(week8)
        assert whr_end < whr_start  # Health risk improved

        # Get progress over 90 days
        progress = tracker.get_measurement_progress(days=90)
        assert len(progress['waist_inches']) == 3  # 3 measurement points

        # Verify waist trend is decreasing
        waist_values = [v for _, v in progress['waist_inches']]
        assert waist_values[0] > waist_values[-1]

        # Cleanup
        os.remove(db_path)

    def test_bulking_phase_progress_tracking(self):
        """Test tracking measurements during a bulking phase"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        tracker = BodyMeasurementTracker(db_path=db_path)

        # Week 1
        week1 = BodyMeasurement(
            measurement_id=None,
            date="2025-09-01",
            chest_inches=40.0,
            bicep_left_inches=14.5,
            bicep_right_inches=14.5,
            thigh_left_inches=23.0,
            thigh_right_inches=23.0,
            waist_inches=32.0
        )
        tracker.log_measurements(week1)

        # Week 8
        week8 = BodyMeasurement(
            measurement_id=None,
            date="2025-10-27",
            chest_inches=41.0,
            bicep_left_inches=15.0,
            bicep_right_inches=15.0,
            thigh_left_inches=23.5,
            thigh_right_inches=23.5,
            waist_inches=32.5
        )
        tracker.log_measurements(week8)

        comparison = tracker.compare_measurements("2025-10-27", "2025-09-01")

        # Verify muscle growth
        assert comparison.changes['chest_inches'] == 1.0
        assert comparison.changes['bicep_left_inches'] == 0.5
        assert comparison.changes['thigh_left_inches'] == 0.5

        # Verify controlled fat gain (waist minimal increase)
        assert comparison.changes['waist_inches'] == 0.5
        assert comparison.total_inches_gained > comparison.total_inches_lost

        # Cleanup
        os.remove(db_path)
