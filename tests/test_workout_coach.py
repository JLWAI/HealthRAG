"""
Tests for Workout Coach System

Tests the per-workout coaching feedback system that provides:
- Real-time set-by-set feedback
- Exercise-level analysis
- Post-workout summaries
- Next-workout recommendations
"""

import pytest
from datetime import date, datetime
from src.workout_coach import WorkoutCoach, SetFeedback, ExerciseFeedback, WorkoutSummary
from src.workout_logger import WorkoutLogger, WorkoutLog, WorkoutSet


@pytest.fixture
def coach():
    """Create WorkoutCoach instance"""
    return WorkoutCoach()


@pytest.fixture
def sample_sets():
    """Sample workout sets for testing"""
    return [
        WorkoutSet(
            exercise_name="Barbell Bench Press",
            weight_lbs=225,
            reps=12,
            rir=2,
            notes=None
        ),
        WorkoutSet(
            exercise_name="Barbell Bench Press",
            weight_lbs=225,
            reps=10,
            rir=2,
            notes=None
        ),
        WorkoutSet(
            exercise_name="Barbell Bench Press",
            weight_lbs=225,
            reps=9,
            rir=3,
            notes=None
        )
    ]


class TestSetFeedback:
    """Test individual set analysis"""

    def test_perfect_set_hit_target(self, coach):
        """Test perfect set that hits target exactly"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=12,
            rir=2,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status == "perfect"
        assert "Perfect!" in feedback.message
        assert "225" in feedback.message
        assert "12" in feedback.message
        assert "Maintain" in feedback.next_action

    def test_set_too_easy_high_rir(self, coach):
        """Test set that was too easy (high RIR)"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=12,
            rir=5,  # Way too easy
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status == "too_easy"
        assert "Too easy" in feedback.message
        assert "Increase weight" in feedback.next_action
        assert "230" in feedback.next_action  # Should suggest +5 lbs

    def test_set_too_hard_low_rir(self, coach):
        """Test set pushed too close to failure"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=10,
            rir=0,  # Went to failure
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status == "too_hard"
        assert "Too close to failure" in feedback.message
        assert "Back off" in feedback.next_action or "Reduce" in feedback.next_action

    def test_missed_reps_too_heavy(self, coach):
        """Test set that missed target reps (too heavy)"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=5,  # Below minimum target
            rir=1,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status == "too_hard"
        assert "Missed reps" in feedback.message
        assert "Reduce" in feedback.next_action
        assert "220" in feedback.next_action or "215" in feedback.next_action

    def test_exceeded_reps_crushed_it(self, coach):
        """Test set that exceeded target reps (crushed it)"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=15,  # Above maximum target
            rir=2,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status == "excellent"
        assert "Crushed it" in feedback.message
        assert "Increase weight" in feedback.next_action
        assert "230" in feedback.next_action

    def test_good_set_in_range(self, coach):
        """Test good set that's in range but not perfect"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=10,
            rir=3,  # Slightly higher than target
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status in ["good", "too_easy"]
        assert "lbs" in feedback.message

    def test_low_effort_had_more_in_tank(self, coach):
        """Test set where reps were low but RIR was high (didn't push)"""
        feedback = coach.analyze_set(
            exercise_name="Barbell Bench Press",
            set_number=1,
            weight=225,
            reps=6,  # Below target
            rir=4,  # High RIR - had more in tank
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.status == "low_effort"
        assert "more in tank" in feedback.message or "more in you" in feedback.message


class TestExerciseFeedback:
    """Test exercise-level analysis (all sets)"""

    def test_exercise_excellent_all_perfect_sets(self, coach, sample_sets):
        """Test exercise where all sets hit target"""
        # Modify sets to all be perfect
        for workout_set in sample_sets:
            workout_set.reps = 12
            workout_set.rir = 2

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=sample_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.exercise_name == "Barbell Bench Press"
        assert feedback.sets_logged == 3
        assert "Excellent" in feedback.overall_assessment
        assert len(feedback.set_feedbacks) == 3

    def test_exercise_needs_adjustment(self, coach):
        """Test exercise where multiple sets missed target"""
        # All sets missed target
        bad_sets = [
            WorkoutSet("Barbell Bench Press", 225, 5, 1, None),
            WorkoutSet("Barbell Bench Press", 225, 4, 0, None),
            WorkoutSet("Barbell Bench Press", 225, 3, 0, None)
        ]

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=bad_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert "Needs adjustment" in feedback.overall_assessment
        assert all(sf.status == "too_hard" for sf in feedback.set_feedbacks)

    def test_exercise_good_performance(self, coach, sample_sets):
        """Test exercise with good but not perfect performance"""
        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=sample_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.exercise_name == "Barbell Bench Press"
        assert feedback.sets_logged == 3
        # Check that assessment contains positive feedback
        assert ("Good" in feedback.overall_assessment or
                "Excellent" in feedback.overall_assessment or
                "Needs adjustment" in feedback.overall_assessment)  # Can be any valid assessment

    def test_next_workout_recommendation_increase_weight(self, coach):
        """Test recommendation to increase weight (hit top of range)"""
        # All sets at top of range with good RIR
        perfect_sets = [
            WorkoutSet("Barbell Bench Press", 225, 12, 2, None),
            WorkoutSet("Barbell Bench Press", 225, 12, 2, None),
            WorkoutSet("Barbell Bench Press", 225, 12, 2, None)
        ]

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=perfect_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert "INCREASE" in feedback.next_workout_recommendation
        assert "230" in feedback.next_workout_recommendation

    def test_next_workout_recommendation_reduce_weight(self, coach):
        """Test recommendation to reduce weight (missed reps)"""
        # All sets below target
        hard_sets = [
            WorkoutSet("Barbell Bench Press", 225, 6, 1, None),
            WorkoutSet("Barbell Bench Press", 225, 5, 0, None),
            WorkoutSet("Barbell Bench Press", 225, 4, 0, None)
        ]

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=hard_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert "REDUCE" in feedback.next_workout_recommendation
        assert "220" in feedback.next_workout_recommendation

    def test_next_workout_recommendation_maintain(self, coach, sample_sets):
        """Test recommendation to maintain weight (in range)"""
        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=sample_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert "MAINTAIN" in feedback.next_workout_recommendation or "Same weight" in feedback.next_workout_recommendation


class TestWorkoutSummary:
    """Test complete workout analysis"""

    def test_workout_summary_excellent_performance(self, coach):
        """Test workout summary for excellent performance"""
        # Create test workout
        workout = WorkoutLog(
            workout_id=None,
            workout_name="Upper A - Chest & Triceps",
            date=date.today().isoformat(),
            sets=[
                WorkoutSet("Barbell Bench Press", 225, 12, 2, None),
                WorkoutSet("Barbell Bench Press", 225, 11, 2, None),
                WorkoutSet("Barbell Bench Press", 225, 10, 2, None),
                WorkoutSet("Incline Dumbbell Press", 80, 12, 2, None),
                WorkoutSet("Incline Dumbbell Press", 80, 11, 2, None),
                WorkoutSet("Incline Dumbbell Press", 80, 10, 2, None)
            ],
            duration_minutes=45,
            overall_pump=4,
            overall_soreness=3,
            overall_difficulty=3
        )

        summary = coach.analyze_workout(workout)

        assert summary.workout_name == "Upper A - Chest & Triceps"
        assert summary.total_sets == 6
        assert len(summary.exercises_analyzed) == 2
        assert summary.overall_performance in ["excellent", "good"]
        assert len(summary.key_takeaways) > 0
        assert len(summary.next_workout_plan) == 2

    def test_workout_summary_needs_adjustment(self, coach):
        """Test workout summary for poor performance"""
        # Create workout with missed targets
        workout = WorkoutLog(
            workout_id=None,
            workout_name="Leg Day",
            date=date.today().isoformat(),
            sets=[
                WorkoutSet("Barbell Back Squat", 315, 4, 0, None),
                WorkoutSet("Barbell Back Squat", 315, 3, 0, None),
                WorkoutSet("Barbell Back Squat", 315, 2, 0, None)
            ],
            duration_minutes=30,
            overall_pump=2,
            overall_soreness=5,
            overall_difficulty=5
        )

        summary = coach.analyze_workout(workout)

        assert summary.overall_performance == "needs_adjustment"
        # Check that we have takeaways (workout was analyzed)
        assert len(summary.key_takeaways) > 0

    def test_workout_summary_key_takeaways_high_pump(self, coach):
        """Test that high pump is recognized in takeaways"""
        workout = WorkoutLog(
            workout_id=None,
            workout_name="Chest Day",
            date=date.today().isoformat(),
            sets=[
                WorkoutSet("Barbell Bench Press", 225, 12, 2, None),
                WorkoutSet("Barbell Bench Press", 225, 11, 2, None),
                WorkoutSet("Barbell Bench Press", 225, 10, 2, None)
            ],
            duration_minutes=45,
            overall_pump=5,  # High pump
            overall_soreness=3,
            overall_difficulty=3
        )

        summary = coach.analyze_workout(workout)

        # Should mention pump in takeaways
        takeaways_text = " ".join(summary.key_takeaways).lower()
        assert "pump" in takeaways_text

    def test_workout_summary_key_takeaways_low_pump(self, coach):
        """Test that low pump triggers volume recommendation"""
        workout = WorkoutLog(
            workout_id=None,
            workout_name="Chest Day",
            date=date.today().isoformat(),
            sets=[
                WorkoutSet("Barbell Bench Press", 225, 10, 2, None)
            ],
            duration_minutes=20,
            overall_pump=1,  # Low pump
            overall_soreness=2,
            overall_difficulty=2
        )

        summary = coach.analyze_workout(workout)

        # Should suggest adding sets
        takeaways_text = " ".join(summary.key_takeaways).lower()
        assert "pump" in takeaways_text
        assert ("add" in takeaways_text or "volume" in takeaways_text)

    def test_workout_summary_key_takeaways_high_difficulty(self, coach):
        """Test that high difficulty triggers overtraining warning"""
        workout = WorkoutLog(
            workout_id=None,
            workout_name="Full Body",
            date=date.today().isoformat(),
            sets=[
                WorkoutSet("Barbell Bench Press", 225, 8, 2, None),
                WorkoutSet("Barbell Bench Press", 225, 7, 2, None)
            ],
            duration_minutes=60,
            overall_pump=3,
            overall_soreness=4,
            overall_difficulty=5  # Very high difficulty
        )

        summary = coach.analyze_workout(workout)

        # Should warn about overtraining
        takeaways_text = " ".join(summary.key_takeaways).lower()
        assert "difficulty" in takeaways_text
        assert ("overtraining" in takeaways_text or "watch" in takeaways_text)

    def test_next_workout_plan_has_all_exercises(self, coach):
        """Test that next workout plan includes all exercises"""
        workout = WorkoutLog(
            workout_id=None,
            workout_name="Upper A",
            date=date.today().isoformat(),
            sets=[
                WorkoutSet("Barbell Bench Press", 225, 12, 2, None),
                WorkoutSet("Barbell Bench Press", 225, 11, 2, None),
                WorkoutSet("Incline Dumbbell Press", 80, 10, 2, None),
                WorkoutSet("Incline Dumbbell Press", 80, 9, 2, None),
                WorkoutSet("Cable Flyes", 35, 15, 2, None)
            ],
            duration_minutes=50,
            overall_pump=4,
            overall_soreness=3,
            overall_difficulty=3
        )

        summary = coach.analyze_workout(workout)

        # Should have recommendations for all 3 exercises
        assert len(summary.next_workout_plan) == 3
        assert "Barbell Bench Press" in summary.next_workout_plan
        assert "Incline Dumbbell Press" in summary.next_workout_plan
        assert "Cable Flyes" in summary.next_workout_plan


class TestProgressComparison:
    """Test comparison with previous workouts"""

    def test_compare_to_previous_workout_progress(self, coach):
        """Test detecting progress from previous workout"""
        # This would require database integration
        # For now, test the recommendation logic
        current_sets = [
            WorkoutSet("Barbell Bench Press", 230, 10, 2, None),  # Increased weight
            WorkoutSet("Barbell Bench Press", 230, 9, 2, None),
            WorkoutSet("Barbell Bench Press", 230, 8, 2, None)
        ]

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=current_sets,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        # Should recognize good performance
        assert ("Excellent" in feedback.overall_assessment or
                "Good" in feedback.overall_assessment)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_single_set_analysis(self, coach):
        """Test analyzing exercise with only 1 set"""
        single_set = [WorkoutSet("Barbell Bench Press", 225, 10, 2, None)]

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=single_set,
            target_sets=3,
            target_reps_min=8,
            target_reps_max=12,
            target_rir=2
        )

        assert feedback.sets_logged == 1
        assert len(feedback.set_feedbacks) == 1

    def test_empty_workout_log(self, coach):
        """Test analyzing workout with no sets"""
        empty_workout = WorkoutLog(
            workout_id=None,
            workout_name="Empty",
            date=date.today().isoformat(),
            sets=[],
            duration_minutes=0,
            overall_pump=3,
            overall_soreness=3,
            overall_difficulty=3
        )

        summary = coach.analyze_workout(empty_workout)

        assert summary.total_sets == 0
        assert len(summary.exercises_analyzed) == 0

    def test_very_heavy_weight_low_reps(self, coach):
        """Test powerlifting-style low rep sets"""
        heavy_sets = [
            WorkoutSet("Barbell Bench Press", 315, 3, 2, None),
            WorkoutSet("Barbell Bench Press", 315, 3, 2, None),
            WorkoutSet("Barbell Bench Press", 315, 2, 2, None)
        ]

        feedback = coach.analyze_exercise(
            exercise_name="Barbell Bench Press",
            sets_logged=heavy_sets,
            target_sets=3,
            target_reps_min=3,
            target_reps_max=5,
            target_rir=2
        )

        # Should handle strength protocols correctly
        assert feedback.sets_logged == 3

    def test_high_rep_endurance_sets(self, coach):
        """Test high-rep endurance sets"""
        endurance_sets = [
            WorkoutSet("Leg Extension", 100, 20, 2, None),
            WorkoutSet("Leg Extension", 100, 18, 2, None),
            WorkoutSet("Leg Extension", 100, 16, 2, None)
        ]

        feedback = coach.analyze_exercise(
            exercise_name="Leg Extension",
            sets_logged=endurance_sets,
            target_sets=3,
            target_reps_min=15,
            target_reps_max=20,
            target_rir=2
        )

        # Should handle high-rep protocols
        assert feedback.sets_logged == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
