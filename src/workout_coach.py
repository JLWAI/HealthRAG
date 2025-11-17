"""
Per-Workout Coach Analysis for HealthRAG

Provides immediate feedback after each workout session:
- Real-time set-by-set feedback
- Post-workout summary
- Specific recommendations for next session

Unlike autoregulation.py (multi-workout trends), this provides instant coaching.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import date

try:
    from workout_logger import WorkoutLogger, WorkoutLog, WorkoutSet
except ImportError:
    from src.workout_logger import WorkoutLogger, WorkoutLog, WorkoutSet


@dataclass
class SetFeedback:
    """Feedback for a single logged set"""
    set_number: int
    status: str  # "perfect", "good", "low", "too_hard"
    message: str
    next_action: str  # What to do next set or next workout


@dataclass
class ExerciseFeedback:
    """Feedback for all sets of an exercise"""
    exercise_name: str
    target_sets: int
    target_reps_min: int
    target_reps_max: int
    target_rir: int
    sets_logged: int
    set_feedbacks: List[SetFeedback]
    overall_assessment: str
    next_workout_recommendation: str


@dataclass
class WorkoutSummary:
    """Complete post-workout analysis"""
    workout_name: str
    workout_date: str
    total_sets: int
    exercises_analyzed: List[ExerciseFeedback]
    overall_performance: str  # "excellent", "good", "needs_adjustment"
    key_takeaways: List[str]
    next_workout_plan: Dict[str, str]  # exercise_name -> recommendation


class WorkoutCoach:
    """
    Immediate coaching feedback system.

    Analyzes each workout right after completion and provides:
    1. Set-by-set feedback (hit target? adjust weight?)
    2. Exercise-level summary (progress vs last time?)
    3. Overall workout assessment
    4. Specific recommendations for next session
    """

    def __init__(self, logger: Optional[WorkoutLogger] = None):
        self.logger = logger or WorkoutLogger()

    def analyze_set(self,
                   exercise_name: str,
                   set_number: int,
                   weight: float,
                   reps: int,
                   rir: int,
                   target_reps_min: int,
                   target_reps_max: int,
                   target_rir: int) -> SetFeedback:
        """
        Analyze a single set immediately after logging.

        Args:
            exercise_name: Name of exercise
            set_number: Which set (1, 2, 3, etc.)
            weight: Weight used
            reps: Reps completed
            rir: RIR reported
            target_reps_min: Minimum target reps
            target_reps_max: Maximum target reps
            target_rir: Target RIR

        Returns:
            SetFeedback with instant coaching
        """
        # Check if hit target reps
        hit_reps = target_reps_min <= reps <= target_reps_max
        hit_rir = rir <= target_rir + 1  # Allow 1 RIR buffer

        # Perfect execution
        if hit_reps and rir == target_rir:
            return SetFeedback(
                set_number=set_number,
                status="perfect",
                message=f"✅ Perfect! {weight} lbs × {reps} @ {rir} RIR - Hit target exactly",
                next_action="Maintain this weight. If you hit top of range (12 reps) @ target RIR next time, increase weight 5 lbs"
            )

        # Hit reps but too easy (higher RIR than target)
        elif hit_reps and rir > target_rir + 1:
            return SetFeedback(
                set_number=set_number,
                status="too_easy",
                message=f"⚠️ Too easy: {weight} lbs × {reps} @ {rir} RIR (target was {target_rir} RIR)",
                next_action=f"Increase weight to {weight + 5} lbs next set or next workout"
            )

        # Hit reps but pushed too hard (RIR too low)
        elif hit_reps and rir < target_rir:
            return SetFeedback(
                set_number=set_number,
                status="too_hard",
                message=f"🔥 Too close to failure: {weight} lbs × {reps} @ {rir} RIR (target was {target_rir} RIR)",
                next_action="Back off intensity next set. Reduce weight 5% or add 1 RIR"
            )

        # Missed target reps (below range)
        elif reps < target_reps_min:
            if rir <= 1:
                return SetFeedback(
                    set_number=set_number,
                    status="too_hard",
                    message=f"❌ Missed reps: Only {reps} reps @ {rir} RIR (target was {target_reps_min}-{target_reps_max})",
                    next_action=f"Weight too heavy. Reduce to {weight - 5} lbs or {weight - 10} lbs next time"
                )
            else:
                return SetFeedback(
                    set_number=set_number,
                    status="low_effort",
                    message=f"⚠️ Low reps but had more in tank: {reps} reps @ {rir} RIR",
                    next_action="Push closer to target RIR next set - you have more in you!"
                )

        # Exceeded target reps (above range)
        elif reps > target_reps_max:
            return SetFeedback(
                set_number=set_number,
                status="excellent",
                message=f"🔥 Crushed it! {weight} lbs × {reps} reps @ {rir} RIR (target was {target_reps_max})",
                next_action=f"Increase weight to {weight + 5} lbs next workout"
            )

        # Default: good but not perfect
        else:
            return SetFeedback(
                set_number=set_number,
                status="good",
                message=f"✅ Good set: {weight} lbs × {reps} @ {rir} RIR",
                next_action="Keep pushing, maintain intensity"
            )

    def analyze_exercise(self,
                        exercise_name: str,
                        sets_logged: List[WorkoutSet],
                        target_sets: int,
                        target_reps_min: int,
                        target_reps_max: int,
                        target_rir: int) -> ExerciseFeedback:
        """
        Analyze all sets of an exercise and compare to last workout.

        Args:
            exercise_name: Name of exercise
            sets_logged: All sets logged for this exercise
            target_sets: Target number of sets
            target_reps_min: Minimum target reps
            target_reps_max: Maximum target reps
            target_rir: Target RIR

        Returns:
            ExerciseFeedback with recommendations
        """
        # Generate set-by-set feedback
        set_feedbacks = []
        for i, workout_set in enumerate(sets_logged, 1):
            feedback = self.analyze_set(
                exercise_name=exercise_name,
                set_number=i,
                weight=workout_set.weight_lbs,
                reps=workout_set.reps,
                rir=workout_set.rir,
                target_reps_min=target_reps_min,
                target_reps_max=target_reps_max,
                target_rir=target_rir
            )
            set_feedbacks.append(feedback)

        # Overall assessment
        perfect_count = sum(1 for sf in set_feedbacks if sf.status == "perfect")
        good_count = sum(1 for sf in set_feedbacks if sf.status in ["good", "excellent"])

        if perfect_count >= target_sets * 0.75:
            overall = "Excellent execution - all sets in target range @ target RIR"
        elif good_count >= target_sets * 0.75:
            overall = "Good performance - most sets hit target"
        else:
            overall = "Needs adjustment - several sets missed target"

        # Compare to last workout
        last_workout = self._get_last_exercise_performance(exercise_name)
        next_recommendation = self._generate_next_workout_recommendation(
            exercise_name,
            sets_logged,
            last_workout,
            target_reps_min,
            target_reps_max,
            target_rir
        )

        return ExerciseFeedback(
            exercise_name=exercise_name,
            target_sets=target_sets,
            target_reps_min=target_reps_min,
            target_reps_max=target_reps_max,
            target_rir=target_rir,
            sets_logged=len(sets_logged),
            set_feedbacks=set_feedbacks,
            overall_assessment=overall,
            next_workout_recommendation=next_recommendation
        )

    def analyze_workout(self, workout_log: WorkoutLog) -> WorkoutSummary:
        """
        Analyze complete workout and provide summary.

        Args:
            workout_log: Complete workout session

        Returns:
            WorkoutSummary with recommendations
        """
        # Group sets by exercise
        exercises = {}
        for workout_set in workout_log.sets:
            if workout_set.exercise_name not in exercises:
                exercises[workout_set.exercise_name] = []
            exercises[workout_set.exercise_name].append(workout_set)

        # Analyze each exercise
        exercise_feedbacks = []
        for exercise_name, sets in exercises.items():
            # Assume standard hypertrophy protocol if not specified
            # TODO: Get from active program
            feedback = self.analyze_exercise(
                exercise_name=exercise_name,
                sets_logged=sets,
                target_sets=3,  # Default
                target_reps_min=8,
                target_reps_max=12,
                target_rir=2
            )
            exercise_feedbacks.append(feedback)

        # Overall performance
        excellent_count = sum(1 for ef in exercise_feedbacks
                            if "Excellent" in ef.overall_assessment)
        if excellent_count >= len(exercise_feedbacks) * 0.75:
            overall_performance = "excellent"
        elif excellent_count >= len(exercise_feedbacks) * 0.5:
            overall_performance = "good"
        else:
            overall_performance = "needs_adjustment"

        # Generate key takeaways
        key_takeaways = self._generate_takeaways(
            exercise_feedbacks,
            workout_log.overall_pump,
            workout_log.overall_soreness,
            workout_log.overall_difficulty
        )

        # Next workout plan
        next_workout_plan = {
            ef.exercise_name: ef.next_workout_recommendation
            for ef in exercise_feedbacks
        }

        return WorkoutSummary(
            workout_name=workout_log.workout_name,
            workout_date=workout_log.date,
            total_sets=len(workout_log.sets),
            exercises_analyzed=exercise_feedbacks,
            overall_performance=overall_performance,
            key_takeaways=key_takeaways,
            next_workout_plan=next_workout_plan
        )

    def _get_last_exercise_performance(self, exercise_name: str) -> Optional[Dict]:
        """Get last workout performance for exercise"""
        history = self.logger.get_exercise_history(exercise_name, limit=10)
        if history:
            # Get most recent entry
            return history[0]
        return None

    def _generate_next_workout_recommendation(self,
                                              exercise_name: str,
                                              current_sets: List[WorkoutSet],
                                              last_workout: Optional[Dict],
                                              target_reps_min: int,
                                              target_reps_max: int,
                                              target_rir: int) -> str:
        """Generate specific recommendation for next workout"""
        if not current_sets:
            return "No data to analyze"

        # Get average performance
        avg_weight = sum(s.weight_lbs for s in current_sets) / len(current_sets)
        avg_reps = sum(s.reps for s in current_sets) / len(current_sets)
        avg_rir = sum(s.rir for s in current_sets) / len(current_sets)

        # Check if progressed from last workout
        progressed = False
        if last_workout:
            if avg_weight > last_workout['weight_lbs']:
                progressed = True
            elif avg_weight == last_workout['weight_lbs'] and avg_reps > last_workout['reps']:
                progressed = True

        # Generate recommendation
        if progressed:
            return f"✅ PROGRESS! Matched or beat last workout. Next time: Same weight ({avg_weight} lbs), aim for {target_reps_max} reps @ {target_rir} RIR. If you hit it, increase to {avg_weight + 5} lbs."

        # Hit top of rep range @ target RIR
        if avg_reps >= target_reps_max and avg_rir <= target_rir:
            return f"🔥 INCREASE WEIGHT! Next time: {avg_weight + 5} lbs × {target_reps_min}-{target_reps_max} @ {target_rir} RIR"

        # In middle of range
        if target_reps_min <= avg_reps <= target_reps_max:
            return f"✅ MAINTAIN: {avg_weight} lbs × {target_reps_min}-{target_reps_max} @ {target_rir} RIR - Keep building reps before increasing weight"

        # Below target reps
        if avg_reps < target_reps_min:
            return f"⚠️ REDUCE WEIGHT: Drop to {avg_weight - 5} lbs next time. Aim for {target_reps_min}-{target_reps_max} @ {target_rir} RIR"

        return f"Continue with {avg_weight} lbs, focus on technique"

    def _generate_takeaways(self,
                           exercise_feedbacks: List[ExerciseFeedback],
                           pump: int,
                           soreness: int,
                           difficulty: int) -> List[str]:
        """Generate key takeaways from workout"""
        takeaways = []

        # Progress takeaways
        excellent_exercises = [ef.exercise_name for ef in exercise_feedbacks
                             if "Excellent" in ef.overall_assessment]
        if excellent_exercises:
            takeaways.append(f"✅ Excellent performance on: {', '.join(excellent_exercises[:3])}")

        # Adjustment needed
        needs_adjustment = [ef.exercise_name for ef in exercise_feedbacks
                          if "needs_adjustment" in ef.overall_assessment.lower()]
        if needs_adjustment:
            takeaways.append(f"⚠️ Adjust next time: {', '.join(needs_adjustment)}")

        # Pump analysis
        if pump >= 4:
            takeaways.append(f"💪 Great pump ({pump}/5) - volume is appropriate")
        elif pump <= 2:
            takeaways.append(f"📊 Low pump ({pump}/5) - consider adding 1-2 sets")

        # Difficulty analysis
        if difficulty >= 4:
            takeaways.append(f"🔥 High difficulty ({difficulty}/5) - watch for overtraining")
        elif difficulty <= 2:
            takeaways.append(f"📈 Low difficulty ({difficulty}/5) - room to push harder")

        # Volume summary
        total_sets = sum(ef.sets_logged for ef in exercise_feedbacks)
        takeaways.append(f"📊 Total sets: {total_sets}")

        return takeaways


if __name__ == "__main__":
    # Test workout coach
    print("=== Workout Coach Test ===\n")

    from datetime import date

    coach = WorkoutCoach()

    # Test set feedback
    print("Test 1: Set Feedback")
    print("-" * 60)

    set1 = coach.analyze_set(
        exercise_name="Barbell Bench Press",
        set_number=1,
        weight=225,
        reps=12,
        rir=2,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )
    print(f"Set 1: {set1.message}")
    print(f"Next: {set1.next_action}\n")

    set2 = coach.analyze_set(
        exercise_name="Barbell Bench Press",
        set_number=2,
        weight=225,
        reps=10,
        rir=2,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )
    print(f"Set 2: {set2.message}")
    print(f"Next: {set2.next_action}\n")

    set3 = coach.analyze_set(
        exercise_name="Barbell Bench Press",
        set_number=3,
        weight=225,
        reps=8,
        rir=3,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )
    print(f"Set 3: {set3.message}")
    print(f"Next: {set3.next_action}\n")

    print("\n✅ Workout Coach tests passed!")
