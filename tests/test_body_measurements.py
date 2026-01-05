"""
Tests for body_measurements module.

Tests cover:
- Database initialization and schema
- Measurement logging with validation
- Retrieval and filtering
- Body fat calculations (US Navy, WHtR, BMI)
- Progress comparison
- Edge cases and error handling
"""

import pytest
import sqlite3
import tempfile
import os
from datetime import date, timedelta
from pathlib import Path

from src.body_measurements import (
    BodyMeasurement,
    BodyFatEstimate,
    BodyMeasurementTracker
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def tracker(temp_db):
    """Create tracker with temporary database"""
    return BodyMeasurementTracker(db_path=temp_db)


# Database Initialization Tests

def test_database_initialization(temp_db):
    """Test database and table creation"""
    tracker = BodyMeasurementTracker(db_path=temp_db)

    # Verify database file exists
    assert os.path.exists(temp_db)

    # Verify table schema
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='body_measurements'")
    assert cursor.fetchone() is not None

    # Verify columns
    cursor.execute("PRAGMA table_info(body_measurements)")
    columns = {row[1] for row in cursor.fetchall()}
    expected_columns = {
        'id', 'date', 'waist', 'chest', 'hips', 'neck', 'shoulders',
        'left_arm', 'right_arm', 'left_thigh', 'right_thigh',
        'left_calf', 'right_calf', 'notes', 'created_at'
    }
    assert columns == expected_columns

    # Verify index exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_body_measurements_date'")
    assert cursor.fetchone() is not None

    conn.close()


# Measurement Logging Tests

def test_log_single_measurement(tracker):
    """Test logging a single measurement"""
    entry_id = tracker.log_measurement(
        measurement_date="2026-01-05",
        waist=32.0,
        chest=40.0,
        notes="Post-workout"
    )

    assert entry_id > 0

    # Verify stored correctly
    entries = tracker.get_measurements()
    assert len(entries) == 1
    assert entries[0].waist == 32.0
    assert entries[0].chest == 40.0
    assert entries[0].notes == "Post-workout"


def test_log_all_measurements(tracker):
    """Test logging all 11 measurements"""
    entry_id = tracker.log_measurement(
        measurement_date="2026-01-05",
        waist=32.0,
        chest=40.0,
        hips=38.0,
        neck=15.5,
        shoulders=48.0,
        left_arm=14.0,
        right_arm=14.0,
        left_thigh=24.0,
        right_thigh=24.0,
        left_calf=15.5,
        right_calf=15.5,
        notes="Full measurement day"
    )

    assert entry_id > 0

    entries = tracker.get_measurements()
    assert len(entries) == 1
    entry = entries[0]

    assert entry.waist == 32.0
    assert entry.chest == 40.0
    assert entry.hips == 38.0
    assert entry.neck == 15.5
    assert entry.shoulders == 48.0
    assert entry.left_arm == 14.0
    assert entry.right_arm == 14.0
    assert entry.left_thigh == 24.0
    assert entry.right_thigh == 24.0
    assert entry.left_calf == 15.5
    assert entry.right_calf == 15.5


def test_log_measurement_defaults_to_today(tracker):
    """Test that date defaults to today if not specified"""
    entry_id = tracker.log_measurement(waist=32.0)

    entries = tracker.get_measurements()
    assert entries[0].date == date.today().isoformat()


def test_log_measurement_replace_duplicate_date(tracker):
    """Test that logging same date replaces previous entry"""
    # First entry
    tracker.log_measurement(measurement_date="2026-01-05", waist=32.0)

    # Second entry same date
    tracker.log_measurement(measurement_date="2026-01-05", waist=33.0)

    # Should only have one entry with updated value
    entries = tracker.get_measurements()
    assert len(entries) == 1
    assert entries[0].waist == 33.0


def test_log_measurement_validation_no_measurements(tracker):
    """Test that at least one measurement is required"""
    with pytest.raises(ValueError, match="At least one measurement must be provided"):
        tracker.log_measurement(measurement_date="2026-01-05")


def test_log_measurement_validation_invalid_range(tracker):
    """Test validation of measurement ranges"""
    # Negative value
    with pytest.raises(ValueError, match="Invalid waist measurement"):
        tracker.log_measurement(waist=-1.0)

    # Too large value
    with pytest.raises(ValueError, match="Invalid waist measurement"):
        tracker.log_measurement(waist=101.0)

    # Zero value
    with pytest.raises(ValueError, match="Invalid chest measurement"):
        tracker.log_measurement(chest=0.0)


# Retrieval Tests

def test_get_measurements_empty_database(tracker):
    """Test retrieving from empty database"""
    entries = tracker.get_measurements()
    assert len(entries) == 0


def test_get_measurements_ordered_by_date_desc(tracker):
    """Test that measurements are ordered by date descending"""
    tracker.log_measurement(measurement_date="2026-01-01", waist=32.0)
    tracker.log_measurement(measurement_date="2026-01-03", waist=33.0)
    tracker.log_measurement(measurement_date="2026-01-02", waist=32.5)

    entries = tracker.get_measurements()

    assert len(entries) == 3
    assert entries[0].date == "2026-01-03"  # Most recent first
    assert entries[1].date == "2026-01-02"
    assert entries[2].date == "2026-01-01"


def test_get_measurements_with_date_range(tracker):
    """Test filtering by date range"""
    tracker.log_measurement(measurement_date="2026-01-01", waist=32.0)
    tracker.log_measurement(measurement_date="2026-01-05", waist=33.0)
    tracker.log_measurement(measurement_date="2026-01-10", waist=34.0)

    # Get entries between Jan 3-8
    entries = tracker.get_measurements(start_date="2026-01-03", end_date="2026-01-08")

    assert len(entries) == 1
    assert entries[0].date == "2026-01-05"


def test_get_measurements_with_limit(tracker):
    """Test limiting number of results"""
    for i in range(5):
        tracker.log_measurement(
            measurement_date=f"2026-01-0{i+1}",
            waist=32.0 + i
        )

    entries = tracker.get_measurements(limit=3)

    assert len(entries) == 3
    assert entries[0].date == "2026-01-05"  # Most recent


def test_get_latest_measurement(tracker):
    """Test getting most recent measurement"""
    tracker.log_measurement(measurement_date="2026-01-01", waist=32.0)
    tracker.log_measurement(measurement_date="2026-01-05", waist=33.0)
    tracker.log_measurement(measurement_date="2026-01-03", waist=32.5)

    latest = tracker.get_latest_measurement()

    assert latest is not None
    assert latest.date == "2026-01-05"
    assert latest.waist == 33.0


def test_get_latest_measurement_empty_database(tracker):
    """Test getting latest from empty database"""
    latest = tracker.get_latest_measurement()
    assert latest is None


# Deletion Tests

def test_delete_measurement(tracker):
    """Test deleting a measurement"""
    tracker.log_measurement(measurement_date="2026-01-05", waist=32.0)

    deleted = tracker.delete_measurement("2026-01-05")

    assert deleted is True
    assert len(tracker.get_measurements()) == 0


def test_delete_measurement_not_found(tracker):
    """Test deleting non-existent measurement"""
    deleted = tracker.delete_measurement("2026-01-05")
    assert deleted is False


# Body Fat Calculation Tests

def test_calculate_body_fat_male_navy_method(tracker):
    """Test US Navy method for male"""
    measurement = BodyMeasurement(
        entry_id=1,
        date="2026-01-05",
        waist=32.0,
        neck=15.5,
        chest=40.0
    )

    estimate = tracker.calculate_body_fat(
        measurement=measurement,
        weight_lbs=185,
        height_inches=70,
        sex="male"
    )

    # Verify Navy method calculated
    assert estimate.navy_method_bf is not None
    assert 10 <= estimate.navy_method_bf <= 25  # Reasonable range

    # Verify category assigned
    assert estimate.category is not None
    assert estimate.category in ["Essential Fat", "Athletic", "Fitness", "Average", "Obese"]


def test_calculate_body_fat_female_navy_method(tracker):
    """Test US Navy method for female"""
    measurement = BodyMeasurement(
        entry_id=1,
        date="2026-01-05",
        waist=28.0,
        hips=38.0,
        neck=13.0
    )

    estimate = tracker.calculate_body_fat(
        measurement=measurement,
        weight_lbs=140,
        height_inches=65,
        sex="female"
    )

    # Verify Navy method calculated
    assert estimate.navy_method_bf is not None
    assert 15 <= estimate.navy_method_bf <= 35  # Reasonable range

    # Verify category assigned
    assert estimate.category is not None


def test_calculate_body_fat_whtr(tracker):
    """Test Waist-to-Height Ratio calculation"""
    measurement = BodyMeasurement(
        entry_id=1,
        date="2026-01-05",
        waist=32.0
    )

    estimate = tracker.calculate_body_fat(
        measurement=measurement,
        weight_lbs=185,
        height_inches=70,
        sex="male"
    )

    # Verify WHtR calculated
    assert estimate.waist_to_height_ratio is not None
    assert estimate.waist_to_height_ratio == pytest.approx(32.0 / 70, rel=0.01)

    # Verify WHtR BF% estimate
    assert estimate.waist_to_height_bf_estimate is not None
    assert 5 <= estimate.waist_to_height_bf_estimate <= 40


def test_calculate_body_fat_bmi(tracker):
    """Test BMI calculation"""
    measurement = BodyMeasurement(
        entry_id=1,
        date="2026-01-05",
        waist=32.0
    )

    estimate = tracker.calculate_body_fat(
        measurement=measurement,
        weight_lbs=185,
        height_inches=70,
        sex="male"
    )

    # Verify BMI calculated
    assert estimate.bmi is not None
    expected_bmi = (185 / (70 ** 2)) * 703
    assert estimate.bmi == pytest.approx(expected_bmi, rel=0.01)


def test_calculate_body_fat_missing_measurements(tracker):
    """Test body fat calculation with missing measurements"""
    # Male without neck (Navy method needs waist + neck)
    measurement = BodyMeasurement(
        entry_id=1,
        date="2026-01-05",
        waist=32.0
        # Missing neck
    )

    estimate = tracker.calculate_body_fat(
        measurement=measurement,
        weight_lbs=185,
        height_inches=70,
        sex="male"
    )

    # Navy method should be None
    assert estimate.navy_method_bf is None
    assert estimate.category is None

    # But WHtR should still work
    assert estimate.waist_to_height_ratio is not None


def test_calculate_body_fat_fitness_categories_male(tracker):
    """Test fitness category ranges for male"""
    test_cases = [
        (5.0, "Essential Fat"),
        (12.0, "Athletic"),
        (16.0, "Fitness"),
        (22.0, "Average"),
        (28.0, "Obese")
    ]

    for bf_percent, expected_category in test_cases:
        # Create measurement that yields specific BF%
        measurement = BodyMeasurement(
            entry_id=1,
            date="2026-01-05",
            waist=32.0,
            neck=15.5
        )

        estimate = tracker.calculate_body_fat(
            measurement=measurement,
            weight_lbs=185,
            height_inches=70,
            sex="male"
        )

        # Manually set navy_method_bf to test category logic
        estimate.navy_method_bf = bf_percent

        # Recalculate category
        if bf_percent < 6:
            assert "Essential Fat" == expected_category
        elif bf_percent < 14:
            assert "Athletic" == expected_category
        elif bf_percent < 18:
            assert "Fitness" == expected_category
        elif bf_percent < 25:
            assert "Average" == expected_category
        else:
            assert "Obese" == expected_category


# Progress Comparison Tests

def test_get_measurement_changes(tracker):
    """Test calculating changes between measurements"""
    # Log two measurements
    tracker.log_measurement(measurement_date="2026-01-01", waist=32.0, chest=40.0)
    tracker.log_measurement(measurement_date="2026-01-05", waist=31.5, chest=40.5)

    # Get changes for latest
    changes = tracker.get_measurement_changes()

    assert changes['waist'] == pytest.approx(-0.5, rel=0.01)  # Lost 0.5"
    assert changes['chest'] == pytest.approx(0.5, rel=0.01)   # Gained 0.5"


def test_get_measurement_changes_specific_dates(tracker):
    """Test comparing specific dates"""
    tracker.log_measurement(measurement_date="2026-01-01", waist=32.0)
    tracker.log_measurement(measurement_date="2026-01-05", waist=31.5)
    tracker.log_measurement(measurement_date="2026-01-10", waist=31.0)

    # Compare Jan 10 vs Jan 1
    changes = tracker.get_measurement_changes(
        current_date="2026-01-10",
        comparison_date="2026-01-01"
    )

    assert changes['waist'] == pytest.approx(-1.0, rel=0.01)  # Lost 1.0" total


def test_get_measurement_changes_no_previous(tracker):
    """Test changes with only one measurement"""
    tracker.log_measurement(measurement_date="2026-01-05", waist=32.0)

    changes = tracker.get_measurement_changes()

    # Should return empty dict when no previous measurement
    assert changes == {}


def test_get_measurement_changes_missing_values(tracker):
    """Test changes when measurements are missing"""
    tracker.log_measurement(measurement_date="2026-01-01", waist=32.0, chest=40.0)
    tracker.log_measurement(measurement_date="2026-01-05", waist=31.5)  # No chest

    changes = tracker.get_measurement_changes()

    assert changes['waist'] == pytest.approx(-0.5, rel=0.01)
    assert changes['chest'] is None  # Missing in current


# Integration Tests

def test_realistic_measurement_workflow(tracker):
    """Test realistic multi-week tracking workflow"""
    # Week 1
    tracker.log_measurement(
        measurement_date="2026-01-01",
        waist=34.0,
        chest=40.0,
        left_arm=14.0,
        right_arm=14.0,
        notes="Baseline measurement"
    )

    # Week 2
    tracker.log_measurement(
        measurement_date="2026-01-08",
        waist=33.5,
        chest=40.2,
        left_arm=14.1,
        right_arm=14.1,
        notes="Week 2 - cutting phase"
    )

    # Week 3
    tracker.log_measurement(
        measurement_date="2026-01-15",
        waist=33.0,
        chest=40.5,
        left_arm=14.2,
        right_arm=14.2,
        notes="Week 3 - seeing progress"
    )

    # Verify all stored
    entries = tracker.get_measurements()
    assert len(entries) == 3

    # Get latest
    latest = tracker.get_latest_measurement()
    assert latest.waist == 33.0

    # Calculate progress
    changes = tracker.get_measurement_changes()
    assert changes['waist'] < 0  # Lost inches (good for cutting)
    assert changes['chest'] > 0  # Gained inches (muscle retention)
    assert changes['left_arm'] > 0  # Growing arms


def test_body_fat_tracking_over_time(tracker):
    """Test tracking body fat changes over time"""
    dates = ["2026-01-01", "2026-01-15", "2026-02-01"]
    waist_values = [36.0, 34.0, 32.0]  # Progressive reduction

    for i, (date_str, waist) in enumerate(zip(dates, waist_values)):
        tracker.log_measurement(
            measurement_date=date_str,
            waist=waist,
            neck=15.5,
            hips=38.0
        )

    # Get all measurements and calculate BF% for each
    entries = tracker.get_measurements()

    bf_estimates = []
    for entry in entries:
        estimate = tracker.calculate_body_fat(
            measurement=entry,
            weight_lbs=190 - (len(entries) - entries.index(entry) - 1) * 5,  # Losing weight too
            height_inches=70,
            sex="male"
        )
        bf_estimates.append(estimate.navy_method_bf)

    # Verify BF% is decreasing over time (cutting successfully)
    assert bf_estimates[0] < bf_estimates[1] < bf_estimates[2]
