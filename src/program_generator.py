"""
Complete Program Generator for HealthRAG
Integrates all Phase 3 components into cohesive program generation
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json
from datetime import date, timedelta

from exercise_database import Exercise, MuscleGroup, ExerciseTier
from exercise_selection import ExerciseSelector, ExerciseRecommendation
from mesocycle_templates import (
    MesocycleTemplate, WorkoutDay, get_recommended_template,
    get_template_by_name, get_templates_by_days
)
from volume_prescription import (
    build_mesocycle_progression, MesocycleVolumeProgression,
    distribute_volume_across_workouts, calculate_volume_per_exercise
)
from progressive_overload import (
    build_exercise_progression, ExerciseProgram, WeeklyProgression,
    get_rep_scheme_for_exercise
)


@dataclass
class WorkoutExercise:
    """Single exercise in a workout"""
    exercise: Exercise
    sets: int
    reps_scheme: str  # "8-12 reps"
    rir: int
    load_lbs: Optional[float] = None  # User's working weight
    notes: str = ""


@dataclass
class Workout:
    """Complete workout session"""
    day_name: str  # "Upper A", "Push", etc.
    muscle_groups: List[MuscleGroup]
    exercises: List[WorkoutExercise]
    total_sets: int
    estimated_duration_min: int


@dataclass
class WeeklyPlan:
    """Week's training plan"""
    week_number: int
    is_deload: bool
    workouts: List[Workout]
    total_weekly_sets: int
    notes: str = ""


@dataclass
class CompleteMesocycle:
    """Complete 6-week training program"""
    template_name: str
    start_date: date
    weeks: List[WeeklyPlan]
    equipment_used: List[str]
    coverage_report: Dict
    created_at: str


class ProgramGenerator:
    """
    Generate complete training programs.

    Integrates:
    - Exercise selection (equipment-aware, tier-prioritized)
    - Volume prescription (MEV/MAV/MRV)
    - Progressive overload (RIR + load progression)
    - Mesocycle templates (training splits)
    """

    def __init__(
        self,
        available_equipment: List[str],
        training_level: str = "intermediate",
        days_per_week: int = 4
    ):
        self.equipment = available_equipment
        self.training_level = training_level
        self.days_per_week = days_per_week
        self.selector = ExerciseSelector(available_equipment, training_level)

    def generate_program(
        self,
        template_name: Optional[str] = None,
        weeks: int = 5,
        start_date: Optional[date] = None
    ) -> CompleteMesocycle:
        """
        Generate complete mesocycle program.

        Args:
            template_name: Template to use (or None for auto-recommendation)
            weeks: Accumulation weeks (before deload)
            start_date: Program start date

        Returns:
            Complete mesocycle with all workouts
        """
        # Get template
        if template_name:
            template = get_template_by_name(template_name)
        else:
            template = get_recommended_template(
                self.days_per_week,
                self.training_level,
                goals=["hypertrophy_focus"]
            )

        if not template:
            raise ValueError(f"No suitable template found for {self.days_per_week} days/week")

        # Generate weekly plans
        weekly_plans = []
        for week_num in range(1, weeks + 2):  # +1 for deload week
            is_deload = (week_num == weeks + 1)
            week_plan = self._generate_week(template, week_num, is_deload)
            weekly_plans.append(week_plan)

        # Get coverage report
        coverage = self.selector.get_coverage_report()

        return CompleteMesocycle(
            template_name=template.name,
            start_date=start_date or date.today(),
            weeks=weekly_plans,
            equipment_used=self.equipment,
            coverage_report=coverage,
            created_at=date.today().isoformat()
        )

    def _generate_week(
        self,
        template: MesocycleTemplate,
        week_num: int,
        is_deload: bool
    ) -> WeeklyPlan:
        """Generate single week's training plan"""
        workouts = []
        total_sets = 0

        for workout_day in template.workout_days:
            workout = self._generate_workout(
                workout_day,
                week_num,
                is_deload,
                template
            )
            workouts.append(workout)
            total_sets += workout.total_sets

        notes = "DELOAD WEEK: Easy sets, focus on recovery" if is_deload else f"Week {week_num} of accumulation"

        return WeeklyPlan(
            week_number=week_num,
            is_deload=is_deload,
            workouts=workouts,
            total_weekly_sets=total_sets,
            notes=notes
        )

    def _generate_workout(
        self,
        workout_day: WorkoutDay,
        week_num: int,
        is_deload: bool,
        template: MesocycleTemplate
    ) -> Workout:
        """Generate single workout session"""
        workout_exercises = []
        total_sets = 0

        for muscle in workout_day.priority_order:
            # Get volume progression for this muscle
            progression = build_mesocycle_progression(
                muscle,
                self.training_level,
                weeks=5
            )

            # Get weekly volume
            weekly_volume = progression.weekly_volumes[week_num - 1]

            # Distribute across workouts
            # Count how many times this muscle appears in ALL workout days this week
            muscle_frequency = sum(
                1 for day in template.workout_days
                if muscle in day.muscle_groups
            )

            # Ensure at least 1 workout per week (safety check)
            muscle_frequency = max(muscle_frequency, 1)

            # Sets for THIS workout
            workout_volume = weekly_volume // muscle_frequency

            if workout_volume == 0:
                continue  # Skip if no sets for this muscle

            # Select exercises (2 per muscle in most cases)
            # Get 3 options so user can see alternatives
            exercise_recs = self.selector.select_exercises_for_muscle(
                muscle,
                count=3 if not is_deload else 2
            )

            # Use top 2 (or 1 for deload) for actual workout
            exercise_recs_to_use = exercise_recs[:2 if not is_deload else 1]

            # Distribute sets across exercises
            sets_per_exercise = calculate_volume_per_exercise(
                workout_volume,
                len(exercise_recs_to_use)
            )

            # Build workout exercises
            for i, rec in enumerate(exercise_recs_to_use):
                sets = sets_per_exercise[i]
                if sets == 0:
                    continue

                rep_scheme = get_rep_scheme_for_exercise(rec.exercise)

                # RIR based on week
                if is_deload:
                    rir = 3
                elif week_num == 1:
                    rir = 3
                elif week_num <= 3:
                    rir = 2
                elif week_num == 4:
                    rir = 1
                else:
                    rir = 0

                workout_ex = WorkoutExercise(
                    exercise=rec.exercise,
                    sets=sets,
                    reps_scheme=rep_scheme.display,
                    rir=rir,
                    notes=rec.exercise.notes or ""
                )

                workout_exercises.append(workout_ex)
                total_sets += sets

        # Estimate duration (7-8 min per set including rest)
        estimated_duration = total_sets * 7.5

        return Workout(
            day_name=workout_day.name,
            muscle_groups=workout_day.muscle_groups,
            exercises=workout_exercises,
            total_sets=total_sets,
            estimated_duration_min=int(estimated_duration)
        )

    def save_program(self, program: CompleteMesocycle, filepath: str = "data/current_program.json"):
        """Save program to JSON file"""
        # Convert to dict
        program_dict = {
            "template_name": program.template_name,
            "start_date": program.start_date.isoformat(),
            "equipment_used": program.equipment_used,
            "coverage_report": program.coverage_report,
            "created_at": program.created_at,
            "weeks": []
        }

        for week in program.weeks:
            week_dict = {
                "week_number": week.week_number,
                "is_deload": week.is_deload,
                "notes": week.notes,
                "total_weekly_sets": week.total_weekly_sets,
                "workouts": []
            }

            for workout in week.workouts:
                workout_dict = {
                    "day_name": workout.day_name,
                    "muscle_groups": [m.value for m in workout.muscle_groups],
                    "total_sets": workout.total_sets,
                    "estimated_duration_min": workout.estimated_duration_min,
                    "exercises": []
                }

                for ex in workout.exercises:
                    ex_dict = {
                        "name": ex.exercise.display_name,
                        "tier": ex.exercise.tier.value,
                        "sets": ex.sets,
                        "reps": ex.reps_scheme,
                        "rir": ex.rir,
                        "load_lbs": ex.load_lbs,
                        "notes": ex.notes
                    }
                    workout_dict["exercises"].append(ex_dict)

                week_dict["workouts"].append(workout_dict)

            program_dict["weeks"].append(week_dict)

        # Save to file
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(program_dict, f, indent=2)

        return filepath


def format_workout(workout: Workout) -> str:
    """Format workout for display"""
    output = []

    output.append(f"# {workout.day_name}")
    output.append(f"**Muscles:** {', '.join([m.value.capitalize() for m in workout.muscle_groups])}")
    output.append(f"**Total Sets:** {workout.total_sets} | **Duration:** ~{workout.estimated_duration_min} min")

    output.append("\n## Exercises:")
    for i, ex in enumerate(workout.exercises, 1):
        output.append(f"\n{i}. **{ex.exercise.display_name}** [{ex.exercise.tier.value}]")
        output.append(f"   {ex.sets} sets × {ex.reps_scheme} @ {ex.rir} RIR")
        if ex.notes:
            output.append(f"   💡 {ex.notes[:100]}")  # Truncate long notes

    return "\n".join(output)


def format_week(week: WeeklyPlan) -> str:
    """Format weekly plan for display"""
    output = []

    marker = "🔄 DELOAD" if week.is_deload else f"Week {week.week_number}"
    output.append(f"# {marker}")
    output.append(f"**Total Weekly Sets:** {week.total_weekly_sets}")
    output.append(f"**Notes:** {week.notes}")

    for workout in week.workouts:
        output.append(f"\n---\n")
        output.append(format_workout(workout))

    return "\n".join(output)


if __name__ == "__main__":
    # Example usage
    print("=== Program Generator Test ===\n")

    # Test: Generate program for home + PF equipment
    equipment = [
        "dumbbells", "bench", "incline_bench", "pull_up_bar", "bodyweight",
        "smith_machine", "cables", "leg_press_machine", "chest_press_machine",
        "lat_pulldown_machine", "hip_abduction_machine"
    ]

    generator = ProgramGenerator(
        available_equipment=equipment,
        training_level="intermediate",
        days_per_week=4
    )

    # Generate 6-week program
    program = generator.generate_program(
        template_name="upper_lower_4x",
        weeks=5
    )

    print(f"Template: {program.template_name}")
    print(f"Coverage: {program.coverage_report['s_plus_available']}/{program.coverage_report['s_plus_total']} S+ tier")
    print(f"          {program.coverage_report['s_available']}/{program.coverage_report['s_total']} S tier")
    print()

    # Display Week 1
    print("=" * 60)
    print(format_week(program.weeks[0]))

    # Display Deload week
    print("\n\n" + "=" * 60)
    print(format_week(program.weeks[-1]))

    # Save program
    filepath = generator.save_program(program, "data/test_program.json")
    print(f"\n\nProgram saved to: {filepath}")
