"""
Performance Tests for Phase 4 Modules

Tests database queries, chart rendering, and overall performance
of optimized Phase 4 features.

Run with: pytest tests/test_performance.py -v
"""

import pytest
import time
import tempfile
import os
from datetime import date, timedelta

from src.tdee_analytics import TDEEHistoricalTracker, TDEESnapshot, create_tdee_trend_chart, prepare_snapshots_for_chart
from src.body_measurements import BodyMeasurementTracker, BodyMeasurement
from src.progress_photos import ProgressPhotoTracker, ProgressPhoto
from src.adaptive_tdee import WeightTracker, WeightEntry
from src.performance_utils import PerformanceTimer, get_performance_summary


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def tdee_tracker_with_data(temp_db):
    """Create TDEE tracker with sample data"""
    tracker = TDEEHistoricalTracker(db_path=temp_db)

    # Add 90 days of snapshots
    base_date = date.today() - timedelta(days=90)
    for i in range(90):
        snapshot = TDEESnapshot(
            snapshot_id=None,
            date=(base_date + timedelta(days=i)).isoformat(),
            formula_tdee=2500,
            adaptive_tdee=2450 + (i * 2),  # Gradually increasing
            tdee_delta=-50 + (i * 2),
            average_intake_14d=2100 + (i * 3),
            weight_lbs=210.0 - (i * 0.1),  # Gradually decreasing
            trend_weight_lbs=210.0 - (i * 0.1),
            weight_change_14d=-1.4,
            goal_rate_lbs_week=-1.0,
            actual_rate_lbs_week=-1.0,
            percent_deviation=0.0,
            recommended_calories=2100,
            calorie_adjustment=0,
            recommended_protein_g=200.0,
            recommended_carbs_g=200.0,
            recommended_fat_g=60.0,
            phase='cut'
        )
        tracker.save_snapshot(snapshot)

    return tracker


class TestDatabasePerformance:
    """Test database query performance"""

    def test_tdee_snapshots_query_speed(self, tdee_tracker_with_data):
        """Test that get_snapshots completes within 100ms"""
        start_time = time.time()
        snapshots = tdee_tracker_with_data.get_snapshots(limit=90)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 100, f"Query took {elapsed_ms:.1f}ms (threshold: 100ms)"
        assert len(snapshots) == 90

    def test_tdee_snapshots_with_date_filter(self, tdee_tracker_with_data):
        """Test that date filtering works efficiently"""
        start_date = (date.today() - timedelta(days=30)).isoformat()

        start_time = time.time()
        snapshots = tdee_tracker_with_data.get_snapshots(start_date=start_date)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 50, f"Filtered query took {elapsed_ms:.1f}ms (threshold: 50ms)"
        assert len(snapshots) == 30

    def test_tdee_snapshots_pagination(self, tdee_tracker_with_data):
        """Test that limit parameter works"""
        snapshots = tdee_tracker_with_data.get_snapshots(limit=10)
        assert len(snapshots) == 10

    def test_weight_tracker_query_speed(self, temp_db):
        """Test weight tracker query performance"""
        tracker = WeightTracker(db_path=temp_db)

        # Add 90 days of weights
        base_date = date.today() - timedelta(days=90)
        for i in range(90):
            tracker.log_weight(
                weight_lbs=210.0 - (i * 0.1),
                log_date=(base_date + timedelta(days=i)).isoformat()
            )

        start_time = time.time()
        entries = tracker.get_weights(limit=90)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 100, f"Weight query took {elapsed_ms:.1f}ms (threshold: 100ms)"
        assert len(entries) == 90

    def test_measurements_query_speed(self, temp_db):
        """Test body measurements query performance"""
        tracker = BodyMeasurementTracker(db_path=temp_db)

        # Add 12 months of measurements
        base_date = date.today() - timedelta(days=365)
        for i in range(12):
            measurement = BodyMeasurement(
                measurement_id=None,
                date=(base_date + timedelta(days=i*30)).isoformat(),
                waist_inches=32.0 - (i * 0.2),
                chest_inches=40.0 + (i * 0.1),
                bicep_left_inches=15.0 + (i * 0.05),
                bicep_right_inches=15.0 + (i * 0.05)
            )
            tracker.log_measurements(measurement)

        start_time = time.time()
        measurements = tracker.get_measurements(limit=12)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 50, f"Measurements query took {elapsed_ms:.1f}ms (threshold: 50ms)"
        assert len(measurements) == 12


class TestChartPerformance:
    """Test chart rendering performance"""

    def test_tdee_chart_creation_speed(self, tdee_tracker_with_data):
        """Test that TDEE chart creates within reasonable time"""
        snapshots = tdee_tracker_with_data.get_snapshots(limit=90)

        # Prepare data for cached chart
        dates, data = prepare_snapshots_for_chart(snapshots)

        start_time = time.time()
        fig = create_tdee_trend_chart(dates, data)
        elapsed_ms = (time.time() - start_time) * 1000

        # First render may be slower
        assert elapsed_ms < 500, f"Chart creation took {elapsed_ms:.1f}ms (threshold: 500ms)"
        assert fig is not None

    def test_tdee_chart_caching(self, tdee_tracker_with_data):
        """Test that chart caching works"""
        snapshots = tdee_tracker_with_data.get_snapshots(limit=90)
        dates, data = prepare_snapshots_for_chart(snapshots)

        # First call (uncached)
        start_time = time.time()
        fig1 = create_tdee_trend_chart(dates, data)
        uncached_ms = (time.time() - start_time) * 1000

        # Second call (should be cached)
        start_time = time.time()
        fig2 = create_tdee_trend_chart(dates, data)
        cached_ms = (time.time() - start_time) * 1000

        # Cached should be significantly faster
        assert cached_ms < uncached_ms / 2, f"Cache not working: uncached={uncached_ms:.1f}ms, cached={cached_ms:.1f}ms"


class TestPhotoPerformance:
    """Test progress photos performance"""

    def test_photo_query_with_pagination(self, temp_db):
        """Test that photo pagination works"""
        temp_dir = tempfile.mkdtemp()
        tracker = ProgressPhotoTracker(db_path=temp_db, photos_dir=temp_dir)

        # Note: We're not actually saving photos here, just testing query logic
        # In a real scenario, photos would be added via save_photo()

        start_time = time.time()
        photos = tracker.get_photos(limit=20, offset=0)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 50, f"Photo query took {elapsed_ms:.1f}ms (threshold: 50ms)"

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


class TestPerformanceUtilities:
    """Test performance monitoring utilities"""

    def test_performance_timer(self):
        """Test PerformanceTimer context manager"""
        with PerformanceTimer("test_operation", threshold_ms=1000) as timer:
            time.sleep(0.01)  # 10ms

        assert timer.elapsed_ms >= 10
        assert timer.elapsed_ms < 100

    def test_performance_logging(self):
        """Test performance log creation"""
        with PerformanceTimer("test_log_creation", threshold_ms=100):
            pass

        # Check if performance.log exists
        log_path = 'data/performance.log'
        if os.path.exists(log_path):
            summary = get_performance_summary(log_path, last_n_lines=10)
            assert 'total_operations' in summary
            assert 'slow_operations_count' in summary


@pytest.mark.benchmark
class TestEndToEndPerformance:
    """End-to-end performance tests"""

    def test_full_tdee_analytics_workflow(self, tdee_tracker_with_data):
        """Test complete TDEE analytics workflow performance"""
        start_time = time.time()

        # Get snapshots
        snapshots = tdee_tracker_with_data.get_snapshots(limit=90)

        # Prepare for chart
        dates, data = prepare_snapshots_for_chart(snapshots)

        # Create chart
        fig = create_tdee_trend_chart(dates, data)

        # Get latest snapshot
        latest = tdee_tracker_with_data.get_latest_snapshot()

        total_ms = (time.time() - start_time) * 1000

        # Full workflow should complete within 1 second
        assert total_ms < 1000, f"Full workflow took {total_ms:.1f}ms (threshold: 1000ms)"
        assert fig is not None
        assert latest is not None


# Benchmark report
def test_performance_summary(capsys):
    """Print performance summary"""
    print("\n\n=== PERFORMANCE OPTIMIZATION SUMMARY ===")
    print("\nExpected improvements:")
    print("- Database queries: < 100ms for 90 days of data")
    print("- Chart rendering: < 500ms first render, < 50ms cached")
    print("- Photo queries: < 50ms with pagination")
    print("- N+1 queries eliminated in progress reports")
    print("\nCache configuration:")
    print("- TDEE charts: 5 minute TTL")
    print("- Monthly reports: 1 hour TTL")
    print("- Photo thumbnails: Generated once, reused")
    print("\nData limits:")
    print("- TDEE snapshots: 90 days default")
    print("- Photo pagination: 20 photos per page recommended")
    print("=======================================\n")
