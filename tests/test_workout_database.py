"""
Tests for Workout Database System

Tests SQLite database operations for workout tracking:
- Workout session CRUD operations
- Exercise log storage and retrieval
- Set logging and queries
- Exercise progress tracking
- Data integrity and foreign keys
"""

import pytest
import os
import tempfile
from datetime import date, datetime, timedelta
from src.workout_database import WorkoutDatabase
from src.workout_models import WorkoutSession, ExerciseLog, WorkoutSet, ExerciseProgress


@pytest.fixture
def temp_db_path(tmp_path):
    """Create temporary database path"""
    return str(tmp_path / "test_workouts.db")


@pytest.fixture
def db(temp_db_path):
    """Create WorkoutDatabase instance with temp database"""
    return WorkoutDatabase(temp_db_path)


@pytest.fixture
def sample_session():
    """Create sample workout session"""
    session = WorkoutSession(
        date=date.today(),
        muscle_group="Chest & Triceps",
        duration_minutes=45,
        completed=True,
        notes="Great workout"
    )

    # Add bench press
    bench = session.add_exercise(
        exercise_name="Barbell Bench Press",
        target_sets=3,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )
    bench.add_set(225, 12, 2)
    bench.add_set(225, 10, 2)
    bench.add_set(225, 9, 3)

    # Add incline press
    incline = session.add_exercise(
        exercise_name="Incline Dumbbell Press",
        target_sets=3,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )
    incline.add_set(80, 12, 2)
    incline.add_set(80, 11, 2)
    incline.add_set(80, 10, 2)

    return session


class TestDatabaseInitialization:
    """Test database setup and initialization"""

    def test_database_creates_file(self, temp_db_path):
        """Test that database file is created"""
        db = WorkoutDatabase(temp_db_path)
        assert os.path.exists(temp_db_path)

    def test_database_creates_tables(self, db):
        """Test that all required tables are created"""
        conn = db._get_connection()
        cursor = conn.cursor()

        # Check workout_sessions table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_sessions'")
        assert cursor.fetchone() is not None

        # Check exercise_logs table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise_logs'")
        assert cursor.fetchone() is not None

        # Check workout_sets table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workout_sets'")
        assert cursor.fetchone() is not None

        # Check exercise_progress table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='exercise_progress'")
        assert cursor.fetchone() is not None

        conn.close()

    def test_database_creates_indices(self, db):
        """Test that indices are created for performance"""
        conn = db._get_connection()
        cursor = conn.cursor()

        # Check for indices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indices = [row[0] for row in cursor.fetchall()]

        assert any('sessions_date' in idx for idx in indices)
        assert any('logs_exercise' in idx for idx in indices)
        assert any('sets_log' in idx for idx in indices)

        conn.close()


class TestSaveSession:
    """Test saving workout sessions"""

    def test_save_session_returns_id(self, db, sample_session):
        """Test that saving session returns session_id"""
        session_id = db.save_session(sample_session)
        assert session_id > 0
        assert sample_session.session_id == session_id

    def test_save_session_persists_data(self, db, sample_session):
        """Test that session data is persisted"""
        session_id = db.save_session(sample_session)

        # Retrieve and verify
        retrieved = db.get_session(session_id)
        assert retrieved is not None
        assert retrieved.muscle_group == "Chest & Triceps"
        assert retrieved.duration_minutes == 45
        assert retrieved.completed is True
        assert retrieved.notes == "Great workout"

    def test_save_session_saves_exercises(self, db, sample_session):
        """Test that exercises are saved with session"""
        session_id = db.save_session(sample_session)

        retrieved = db.get_session(session_id)
        assert len(retrieved.exercises) == 2
        assert retrieved.exercises[0].exercise_name == "Barbell Bench Press"
        assert retrieved.exercises[1].exercise_name == "Incline Dumbbell Press"

    def test_save_session_saves_sets(self, db, sample_session):
        """Test that sets are saved for each exercise"""
        session_id = db.save_session(sample_session)

        retrieved = db.get_session(session_id)
        bench_sets = retrieved.exercises[0].sets
        assert len(bench_sets) == 3
        assert bench_sets[0].weight_lbs == 225
        assert bench_sets[0].reps_completed == 12
        assert bench_sets[0].rir == 2

    def test_save_session_creates_foreign_keys(self, db, sample_session):
        """Test that foreign key relationships are maintained"""
        session_id = db.save_session(sample_session)

        conn = db._get_connection()
        cursor = conn.cursor()

        # Check exercise_logs reference session_id
        cursor.execute('SELECT session_id FROM exercise_logs WHERE session_id = ?', (session_id,))
        assert len(cursor.fetchall()) == 2

        # Check workout_sets reference log_id
        cursor.execute('SELECT log_id FROM exercise_logs WHERE session_id = ?', (session_id,))
        log_ids = [row[0] for row in cursor.fetchall()]

        for log_id in log_ids:
            cursor.execute('SELECT * FROM workout_sets WHERE log_id = ?', (log_id,))
            assert len(cursor.fetchall()) > 0

        conn.close()

    def test_save_multiple_sessions(self, db, sample_session):
        """Test saving multiple sessions"""
        session_id_1 = db.save_session(sample_session)

        # Create second session
        session2 = WorkoutSession(
            date=date.today() - timedelta(days=1),
            muscle_group="Back & Biceps"
        )
        back_ex = session2.add_exercise("Barbell Row", 3, 8, 12, 2)
        back_ex.add_set(185, 10, 2)

        session_id_2 = db.save_session(session2)

        assert session_id_2 > session_id_1
        assert db.get_session(session_id_1) is not None
        assert db.get_session(session_id_2) is not None


class TestRetrieveSessions:
    """Test retrieving workout sessions"""

    def test_get_nonexistent_session(self, db):
        """Test getting session that doesn't exist"""
        retrieved = db.get_session(999)
        assert retrieved is None

    def test_get_session_by_id(self, db, sample_session):
        """Test retrieving session by ID"""
        session_id = db.save_session(sample_session)
        retrieved = db.get_session(session_id)

        assert retrieved.session_id == session_id
        assert retrieved.muscle_group == sample_session.muscle_group

    def test_get_sessions_by_date_range(self, db):
        """Test retrieving sessions within date range"""
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        # Create sessions on different dates
        session1 = WorkoutSession(date=two_days_ago, muscle_group="Chest")
        session1.add_exercise("Bench Press", 3, 8, 12, 2).add_set(225, 10, 2)
        db.save_session(session1)

        session2 = WorkoutSession(date=yesterday, muscle_group="Back")
        session2.add_exercise("Barbell Row", 3, 8, 12, 2).add_set(185, 10, 2)
        db.save_session(session2)

        session3 = WorkoutSession(date=today, muscle_group="Legs")
        session3.add_exercise("Squat", 3, 8, 12, 2).add_set(315, 10, 2)
        db.save_session(session3)

        # Query date range
        sessions = db.get_sessions_by_date_range(yesterday, today)

        assert len(sessions) == 2
        assert sessions[0].date == today  # Most recent first
        assert sessions[1].date == yesterday

    def test_get_latest_session_for_muscle(self, db):
        """Test getting most recent session for muscle group"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create two chest sessions
        session1 = WorkoutSession(date=yesterday, muscle_group="Chest")
        session1.add_exercise("Bench Press", 3, 8, 12, 2).add_set(225, 10, 2)
        db.save_session(session1)

        session2 = WorkoutSession(date=today, muscle_group="Chest")
        session2.add_exercise("Bench Press", 3, 8, 12, 2).add_set(230, 10, 2)
        db.save_session(session2)

        # Get latest
        latest = db.get_latest_session_for_muscle("Chest")

        assert latest.date == today
        assert latest.exercises[0].sets[0].weight_lbs == 230

    def test_get_latest_session_nonexistent_muscle(self, db):
        """Test getting latest session for muscle group that hasn't been trained"""
        latest = db.get_latest_session_for_muscle("Nonexistent")
        assert latest is None


class TestExerciseProgress:
    """Test exercise progress tracking"""

    def test_exercise_progress_created_on_first_log(self, db):
        """Test that progress entry is created for new exercise"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")
        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 10, 2)

        db.save_session(session)

        progress = db.get_exercise_progress("Barbell Bench Press")
        assert progress is not None
        assert progress.exercise_name == "Barbell Bench Press"
        assert progress.first_logged == date.today()
        assert progress.last_logged == date.today()

    def test_exercise_progress_tracks_best_weight(self, db):
        """Test that progress tracks best weight × reps"""
        today = date.today()

        # First workout: 225 lbs × 10 reps
        session1 = WorkoutSession(date=today - timedelta(days=7), muscle_group="Chest")
        bench1 = session1.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench1.add_set(225, 10, 2)
        db.save_session(session1)

        # Second workout: 230 lbs × 12 reps (better)
        session2 = WorkoutSession(date=today, muscle_group="Chest")
        bench2 = session2.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench2.add_set(230, 12, 2)
        db.save_session(session2)

        progress = db.get_exercise_progress("Barbell Bench Press")
        assert progress.best_weight == 230
        assert progress.best_reps_at_weight == 12

    def test_exercise_progress_accumulates_volume(self, db):
        """Test that total volume accumulates"""
        session1 = WorkoutSession(date=date.today() - timedelta(days=7), muscle_group="Chest")
        bench1 = session1.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench1.add_set(225, 10, 2)  # 2250 lbs volume
        bench1.add_set(225, 10, 2)  # 2250 lbs volume
        db.save_session(session1)

        session2 = WorkoutSession(date=date.today(), muscle_group="Chest")
        bench2 = session2.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench2.add_set(225, 10, 2)  # 2250 lbs volume
        db.save_session(session2)

        progress = db.get_exercise_progress("Barbell Bench Press")
        expected_volume = 2250 + 2250 + 2250
        assert progress.total_volume == expected_volume

    def test_exercise_progress_counts_total_sets(self, db):
        """Test that total sets are counted"""
        session1 = WorkoutSession(date=date.today() - timedelta(days=7), muscle_group="Chest")
        bench1 = session1.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench1.add_set(225, 10, 2)
        bench1.add_set(225, 10, 2)
        bench1.add_set(225, 10, 2)
        db.save_session(session1)

        session2 = WorkoutSession(date=date.today(), muscle_group="Chest")
        bench2 = session2.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench2.add_set(225, 10, 2)
        bench2.add_set(225, 10, 2)
        db.save_session(session2)

        progress = db.get_exercise_progress("Barbell Bench Press")
        assert progress.total_sets == 5

    def test_exercise_progress_tracks_avg_rir(self, db):
        """Test that average RIR is calculated"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")
        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 10, 2)  # RIR 2
        bench.add_set(225, 10, 3)  # RIR 3
        bench.add_set(225, 10, 1)  # RIR 1
        db.save_session(session)

        progress = db.get_exercise_progress("Barbell Bench Press")
        assert progress.avg_rir == 2.0  # (2 + 3 + 1) / 3

    def test_exercise_progress_nonexistent_exercise(self, db):
        """Test getting progress for exercise that hasn't been logged"""
        progress = db.get_exercise_progress("Nonexistent Exercise")
        assert progress is None


class TestLastExerciseLog:
    """Test retrieving last exercise log"""

    def test_get_last_exercise_log(self, db):
        """Test getting most recent log for an exercise"""
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Log bench press yesterday
        session1 = WorkoutSession(date=yesterday, muscle_group="Chest")
        bench1 = session1.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench1.add_set(225, 10, 2)
        db.save_session(session1)

        # Log bench press today (more recent)
        session2 = WorkoutSession(date=today, muscle_group="Chest")
        bench2 = session2.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench2.add_set(230, 12, 2)
        db.save_session(session2)

        # Get last log
        result = db.get_last_exercise_log("Barbell Bench Press")
        assert result is not None

        last_log, log_date = result
        assert log_date == today
        assert last_log.exercise_name == "Barbell Bench Press"
        assert last_log.sets[0].weight_lbs == 230

    def test_get_last_exercise_log_nonexistent(self, db):
        """Test getting last log for exercise that hasn't been logged"""
        result = db.get_last_exercise_log("Nonexistent Exercise")
        assert result is None


class TestDataIntegrity:
    """Test data integrity and edge cases"""

    def test_incomplete_session_saves(self, db):
        """Test that incomplete session can be saved"""
        session = WorkoutSession(
            date=date.today(),
            muscle_group="Chest",
            completed=False
        )
        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 10, 2)

        session_id = db.save_session(session)
        retrieved = db.get_session(session_id)

        assert retrieved.completed is False

    def test_session_with_no_exercises(self, db):
        """Test saving session with no exercises"""
        session = WorkoutSession(
            date=date.today(),
            muscle_group="Chest",
            completed=False
        )

        session_id = db.save_session(session)
        retrieved = db.get_session(session_id)

        assert len(retrieved.exercises) == 0

    def test_exercise_with_no_sets(self, db):
        """Test exercise with no sets logged"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")
        session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        # Don't add any sets

        session_id = db.save_session(session)
        retrieved = db.get_session(session_id)

        assert len(retrieved.exercises) == 1
        assert len(retrieved.exercises[0].sets) == 0

    def test_very_heavy_weights(self, db):
        """Test logging very heavy weights"""
        session = WorkoutSession(date=date.today(), muscle_group="Legs")
        squat = session.add_exercise("Barbell Back Squat", 3, 1, 3, 2)
        squat.add_set(500, 3, 2)

        session_id = db.save_session(session)
        retrieved = db.get_session(session_id)

        assert retrieved.exercises[0].sets[0].weight_lbs == 500

    def test_bodyweight_exercises(self, db):
        """Test logging bodyweight exercises (0 lbs)"""
        session = WorkoutSession(date=date.today(), muscle_group="Back")
        pullups = session.add_exercise("Pull-ups", 3, 8, 12, 2)
        pullups.add_set(0, 10, 2)  # Bodyweight

        session_id = db.save_session(session)
        retrieved = db.get_session(session_id)

        assert retrieved.exercises[0].sets[0].weight_lbs == 0

    def test_multiple_exercises_same_name_different_sessions(self, db):
        """Test same exercise in multiple sessions"""
        session1 = WorkoutSession(date=date.today() - timedelta(days=7), muscle_group="Chest")
        bench1 = session1.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench1.add_set(225, 10, 2)
        db.save_session(session1)

        session2 = WorkoutSession(date=date.today(), muscle_group="Chest")
        bench2 = session2.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench2.add_set(230, 10, 2)
        db.save_session(session2)

        # Progress should track both
        progress = db.get_exercise_progress("Barbell Bench Press")
        assert progress.total_sets == 2


class TestSessionTimestamps:
    """Test timestamp tracking"""

    def test_created_at_timestamp(self, db, sample_session):
        """Test that created_at timestamp is set"""
        session_id = db.save_session(sample_session)

        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT created_at FROM workout_sessions WHERE session_id = ?', (session_id,))
        created_at = cursor.fetchone()[0]
        conn.close()

        assert created_at is not None
        # Should be recent (within last minute)
        created_dt = datetime.fromisoformat(created_at)
        assert (datetime.now() - created_dt).total_seconds() < 60

    def test_updated_at_timestamp(self, db, sample_session):
        """Test that updated_at timestamp is set"""
        session_id = db.save_session(sample_session)

        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT updated_at FROM workout_sessions WHERE session_id = ?', (session_id,))
        updated_at = cursor.fetchone()[0]
        conn.close()

        assert updated_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
