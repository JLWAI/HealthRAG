"""
Tests for Workout Models

Tests the dataclass models used for workout tracking:
- WorkoutSet (individual set data)
- ExerciseLog (exercise with sets)
- WorkoutSession (complete workout)
- ExerciseProgress (progress tracking)
"""

import pytest
from datetime import date, datetime, timedelta
from src.workout_models import WorkoutSet, ExerciseLog, WorkoutSession, ExerciseProgress


class TestWorkoutSet:
    """Test WorkoutSet dataclass"""

    def test_create_workout_set(self):
        """Test creating a WorkoutSet"""
        workout_set = WorkoutSet(
            set_number=1,
            weight_lbs=225,
            reps_completed=10,
            rir=2,
            exercise_name="Barbell Bench Press",
            notes="Felt strong"
        )

        assert workout_set.weight_lbs == 225
        assert workout_set.reps_completed == 10
        assert workout_set.rir == 2
        assert workout_set.notes == "Felt strong"

    def test_workout_set_default_notes(self):
        """Test WorkoutSet with no notes"""
        workout_set = WorkoutSet(
            set_number=1,
            weight_lbs=315,
            reps_completed=8,
            rir=2
        )

        assert workout_set.notes is None

    def test_workout_set_volume_calculation(self):
        """Test volume calculation (weight × reps)"""
        workout_set = WorkoutSet(set_number=1, weight_lbs=225, reps_completed=10, rir=2)

        volume = workout_set.weight_lbs * workout_set.reps_completed
        assert volume == 2250

    def test_workout_set_zero_weight_bodyweight(self):
        """Test bodyweight exercises (0 lbs)"""
        workout_set = WorkoutSet(set_number=1, weight_lbs=0, reps_completed=10, rir=2)

        assert workout_set.weight_lbs == 0
        assert workout_set.reps_completed == 10

    def test_workout_set_fractional_weight(self):
        """Test fractional weights (e.g., 2.5 lb plates)"""
        workout_set = WorkoutSet(set_number=1, weight_lbs=227.5, reps_completed=10, rir=2)

        assert workout_set.weight_lbs == 227.5


class TestExerciseLog:
    """Test ExerciseLog dataclass"""

    def test_create_exercise_log(self):
        """Test creating an ExerciseLog"""
        exercise_log = ExerciseLog(
            exercise_name="Barbell Bench Press",
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2,
            notes="Focus on form"
        )

        assert exercise_log.exercise_name == "Barbell Bench Press"
        assert exercise_log.target_sets == 3
        assert exercise_log.target_reps_min == 8
        assert exercise_log.target_reps_max == 12
        assert exercise_log.target_rir == 2
        assert len(exercise_log.sets) == 0

    def test_add_set_to_exercise_log(self):
        """Test adding sets to exercise log"""
        exercise_log = ExerciseLog(
            exercise_name="Barbell Bench Press",
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        exercise_log.add_set(225, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 9, 3)

        assert len(exercise_log.sets) == 3
        assert exercise_log.sets[0].weight_lbs == 225
        assert exercise_log.sets[0].reps_completed == 12

    def test_exercise_log_get_total_sets(self):
        """Test getting total number of sets"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 10, 2)

        assert exercise_log.get_total_sets() == 3

    def test_exercise_log_get_total_reps(self):
        """Test getting total reps across all sets"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 8, 2)
        exercise_log.add_set(225, 6, 3)

        assert exercise_log.get_total_reps() == 24  # 10 + 8 + 6

    def test_exercise_log_get_total_volume(self):
        """Test getting total volume (weight × reps)"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 10, 2)  # 2250
        exercise_log.add_set(225, 10, 2)  # 2250
        exercise_log.add_set(225, 10, 2)  # 2250

        assert exercise_log.get_total_volume() == 6750

    def test_exercise_log_get_average_weight(self):
        """Test getting average weight across sets"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(220, 10, 2)
        exercise_log.add_set(215, 10, 2)

        avg_weight = exercise_log.get_average_weight()
        assert avg_weight == 220  # (225 + 220 + 215) / 3

    def test_exercise_log_get_average_reps(self):
        """Test getting average reps across sets"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 8, 2)

        avg_reps = exercise_log.get_average_reps()
        assert avg_reps == 10  # (12 + 10 + 8) / 3

    def test_exercise_log_get_average_rir(self):
        """Test getting average RIR across sets"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 10, 3)
        exercise_log.add_set(225, 10, 1)

        avg_rir = exercise_log.get_average_rir()
        assert avg_rir == 2  # (2 + 3 + 1) / 3

    def test_exercise_log_empty_sets(self):
        """Test statistics with no sets"""
        exercise_log = ExerciseLog("Bench Press", 3, 8, 12, 2)

        assert exercise_log.get_total_sets() == 0
        assert exercise_log.get_total_reps() == 0
        assert exercise_log.get_total_volume() == 0
        assert exercise_log.get_average_weight() == 0.0
        assert exercise_log.get_average_reps() == 0.0
        assert exercise_log.get_average_rir() == 0.0


class TestWorkoutSession:
    """Test WorkoutSession dataclass"""

    def test_create_workout_session(self):
        """Test creating a WorkoutSession"""
        session = WorkoutSession(
            date=date.today(),
            muscle_group="Chest & Triceps",
            duration_minutes=45,
            completed=True,
            notes="Great workout"
        )

        assert session.date == date.today()
        assert session.muscle_group == "Chest & Triceps"
        assert session.duration_minutes == 45
        assert session.completed is True
        assert session.notes == "Great workout"
        assert len(session.exercises) == 0

    def test_workout_session_default_values(self):
        """Test WorkoutSession with default values"""
        session = WorkoutSession(
            date=date.today(),
            muscle_group="Chest"
        )

        assert session.duration_minutes is None
        assert session.completed is False
        assert session.notes is None
        assert len(session.exercises) == 0

    def test_add_exercise_to_session(self):
        """Test adding exercise to session"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")

        exercise = session.add_exercise(
            exercise_name="Barbell Bench Press",
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert len(session.exercises) == 1
        assert session.exercises[0].exercise_name == "Barbell Bench Press"
        assert exercise is session.exercises[0]  # Returns the added exercise

    def test_add_multiple_exercises(self):
        """Test adding multiple exercises"""
        session = WorkoutSession(date=date.today(), muscle_group="Upper Body")

        session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        session.add_exercise("Incline Dumbbell Press", 3, 8, 12, 2)
        session.add_exercise("Cable Flyes", 3, 10, 15, 2)

        assert len(session.exercises) == 3

    def test_get_total_sets_across_exercises(self):
        """Test getting total sets across all exercises"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")

        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 10, 2)
        bench.add_set(225, 10, 2)
        bench.add_set(225, 10, 2)

        incline = session.add_exercise("Incline Dumbbell Press", 3, 8, 12, 2)
        incline.add_set(80, 10, 2)
        incline.add_set(80, 10, 2)

        assert session.get_total_sets() == 5

    def test_get_total_volume_across_exercises(self):
        """Test getting total volume across all exercises"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")

        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 10, 2)  # 2250
        bench.add_set(225, 10, 2)  # 2250

        incline = session.add_exercise("Incline Dumbbell Press", 3, 8, 12, 2)
        incline.add_set(80, 10, 2)  # 800

        assert session.get_total_volume() == 5300  # 2250 + 2250 + 800

    def test_get_exercises_by_name(self):
        """Test getting specific exercise by name"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")

        session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        session.add_exercise("Incline Dumbbell Press", 3, 8, 12, 2)

        bench = session.get_exercise("Barbell Bench Press")
        assert bench is not None
        assert bench.exercise_name == "Barbell Bench Press"

    def test_get_nonexistent_exercise(self):
        """Test getting exercise that doesn't exist"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")
        session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)

        nonexistent = session.get_exercise("Squat")
        assert nonexistent is None

    def test_workout_summary_basic(self):
        """Test getting workout summary"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")

        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 10, 2)
        bench.add_set(225, 10, 2)

        summary = session.get_summary()

        assert "Chest" in summary
        assert "2 sets" in summary
        assert "4500 lbs" in summary  # Volume

    def test_empty_workout_session(self):
        """Test workout session with no exercises"""
        session = WorkoutSession(date=date.today(), muscle_group="Chest")

        assert session.get_total_sets() == 0
        assert session.get_total_volume() == 0


class TestExerciseProgress:
    """Test ExerciseProgress dataclass"""

    def test_create_exercise_progress(self):
        """Test creating ExerciseProgress"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=30),
            last_logged=date.today()
        )

        assert progress.exercise_name == "Barbell Bench Press"
        assert progress.best_weight == 0
        assert progress.best_reps_at_weight == 0
        assert progress.total_volume == 0
        assert progress.total_sets == 0
        assert progress.avg_rir == 0
        assert progress.total_rir == 0

    def test_update_from_log(self):
        """Test updating progress from exercise log"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=7),
            last_logged=date.today() - timedelta(days=7)
        )

        # Create exercise log
        exercise_log = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        exercise_log.add_set(225, 12, 2)
        exercise_log.add_set(225, 10, 2)
        exercise_log.add_set(225, 9, 3)

        # Update progress
        progress.update_from_log(exercise_log, date.today())

        assert progress.last_logged == date.today()
        assert progress.best_weight == 225
        assert progress.best_reps_at_weight == 12
        assert progress.total_sets == 3
        assert progress.total_volume == 6975  # (225*12) + (225*10) + (225*9)

    def test_update_best_weight_progression(self):
        """Test that best weight is updated when beaten"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=14),
            last_logged=date.today() - timedelta(days=7)
        )

        # First workout: 225 lbs × 10 reps
        log1 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log1.add_set(225, 10, 2)
        progress.update_from_log(log1, date.today() - timedelta(days=7))

        assert progress.best_weight == 225
        assert progress.best_reps_at_weight == 10

        # Second workout: 230 lbs × 12 reps (better!)
        log2 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log2.add_set(230, 12, 2)
        progress.update_from_log(log2, date.today())

        assert progress.best_weight == 230
        assert progress.best_reps_at_weight == 12

    def test_update_maintains_best_if_not_beaten(self):
        """Test that best weight is maintained if not beaten"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=14),
            last_logged=date.today() - timedelta(days=7)
        )

        # First workout: 230 lbs × 12 reps (best)
        log1 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log1.add_set(230, 12, 2)
        progress.update_from_log(log1, date.today() - timedelta(days=7))

        # Second workout: 225 lbs × 10 reps (not better)
        log2 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log2.add_set(225, 10, 2)
        progress.update_from_log(log2, date.today())

        # Best should remain 230 × 12
        assert progress.best_weight == 230
        assert progress.best_reps_at_weight == 12

    def test_progress_accumulates_volume(self):
        """Test that volume accumulates over time"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=14),
            last_logged=date.today()
        )

        # First workout: 3 sets × 225 × 10
        log1 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log1.add_set(225, 10, 2)
        log1.add_set(225, 10, 2)
        log1.add_set(225, 10, 2)
        progress.update_from_log(log1, date.today() - timedelta(days=7))

        first_volume = progress.total_volume
        assert first_volume == 6750  # 3 × 225 × 10

        # Second workout: 2 sets × 230 × 10
        log2 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log2.add_set(230, 10, 2)
        log2.add_set(230, 10, 2)
        progress.update_from_log(log2, date.today())

        # Total volume should accumulate
        assert progress.total_volume == 11350  # 6750 + 4600

    def test_progress_tracks_avg_rir(self):
        """Test that average RIR is calculated correctly"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=7),
            last_logged=date.today()
        )

        # First workout: avg RIR = 2
        log1 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log1.add_set(225, 10, 2)
        log1.add_set(225, 10, 2)
        progress.update_from_log(log1, date.today() - timedelta(days=7))

        # After first workout: (2 + 2) / 2 = 2.0
        assert progress.avg_rir == 2.0
        assert progress.total_sets == 2

        # Second workout: avg RIR = 3
        log2 = ExerciseLog("Barbell Bench Press", 3, 8, 12, 2)
        log2.add_set(225, 10, 3)
        progress.update_from_log(log2, date.today())

        # After second workout: (2 + 2 + 3) / 3 = 2.33
        expected_avg = (2 + 2 + 3) / 3
        assert abs(progress.avg_rir - expected_avg) < 0.01

    def test_days_since_first_logged(self):
        """Test calculating days since first logged"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=30),
            last_logged=date.today()
        )

        days = progress.days_since_first_logged()
        assert days == 30

    def test_days_since_last_logged(self):
        """Test calculating days since last logged"""
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today() - timedelta(days=30),
            last_logged=date.today() - timedelta(days=7)
        )

        days = progress.days_since_last_logged()
        assert days == 7


class TestIntegration:
    """Test integration between models"""

    def test_complete_workout_flow(self):
        """Test complete workout flow from session to progress"""
        # Create session
        session = WorkoutSession(
            date=date.today(),
            muscle_group="Chest & Triceps",
            duration_minutes=45
        )

        # Add exercises with sets
        bench = session.add_exercise("Barbell Bench Press", 3, 8, 12, 2)
        bench.add_set(225, 12, 2)
        bench.add_set(225, 10, 2)
        bench.add_set(225, 9, 3)

        incline = session.add_exercise("Incline Dumbbell Press", 3, 8, 12, 2)
        incline.add_set(80, 12, 2)
        incline.add_set(80, 11, 2)
        incline.add_set(80, 10, 2)

        # Mark as completed
        session.completed = True

        # Verify session totals
        assert session.get_total_sets() == 6
        assert session.get_total_volume() == 9615  # (225*12 + 225*10 + 225*9) + (80*12 + 80*11 + 80*10)

        # Create progress from bench exercise
        progress = ExerciseProgress(
            exercise_name="Barbell Bench Press",
            first_logged=date.today(),
            last_logged=date.today()
        )
        progress.update_from_log(bench, date.today())

        assert progress.best_weight == 225
        assert progress.best_reps_at_weight == 12
        assert progress.total_sets == 3
        assert progress.avg_rir == (2 + 2 + 3) / 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
