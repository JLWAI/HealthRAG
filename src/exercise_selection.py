"""
Exercise Selection Engine for HealthRAG
Intelligent, equipment-aware exercise selection with tier prioritization

KEY ADVANTAGE OVER RP HYPERTROPHY APP:
- RP has no equipment awareness (can't filter by home gym vs commercial gym)
- RP's auto-fill is poor quality (random, repetitive exercises)
- HealthRAG prioritizes S/S+ tier exercises based on YOUR available equipment
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from exercise_database import (
    Exercise, ExerciseTier, MuscleGroup,
    get_exercises_by_muscle, get_exercises_by_equipment,
    get_substitutions, get_exercise_by_name,
    ALL_EXERCISES
)


@dataclass
class ExerciseRecommendation:
    """Recommended exercise with reasoning"""
    exercise: Exercise
    reason: str  # Why this exercise was selected
    alternatives: List[Exercise]  # If not available, use these
    location_note: Optional[str] = None  # "Available at home" or "Requires Planet Fitness"


# Movement patterns to detect variations (avoid selecting Cable + Dumbbell versions of same movement)
# More specific patterns listed first (e.g., "preacher curl" before "curl")
MOVEMENT_PATTERNS = [
    # Shoulders - specific
    "lateral raise",
    "front raise",
    "face pull",
    "reverse fly",
    "rear delt fly",
    "y-raise",
    "shoulder press",
    "overhead press",
    # Chest - specific
    "incline press",
    "decline press",
    "flat press",
    "chest press",
    "bench press",
    "cable fly",
    "dumbbell fly",
    "pec deck",
    "fly",
    "flye",
    # Back - specific
    "pulldown",
    "pull down",
    "pull-up",
    "chin-up",
    "seated row",
    "cable row",
    "barbell row",
    "dumbbell row",
    "t-bar row",
    "pullover",
    # Triceps - specific
    "pushdown",
    "push down",
    "overhead extension",
    "tricep extension",
    "skull crusher",
    "close-grip bench",
    "dip",
    "kickback",
    # Biceps - specific (allow different curl variations)
    "preacher curl",
    "spider curl",
    "incline curl",
    "hammer curl",
    "bayesian curl",
    "concentration curl",
    # Generic curl only matches if no specific curl type
    # Legs
    "squat",
    "leg press",
    "leg extension",
    "leg curl",
    "romanian deadlift",
    "hip thrust",
    "calf raise",
    "lunge",
    "split squat",
    # Other
    "shrug",
]


def get_movement_pattern(exercise_name: str) -> Optional[str]:
    """
    Extract the base movement pattern from an exercise name.
    E.g., "Cable Lateral Raise" and "Dumbbell Lateral Raise" -> "lateral raise"

    Uses longest-match-first to ensure specific patterns match before generic ones.
    """
    name_lower = exercise_name.lower()

    # Sort patterns by length (longest first) to match specific patterns before generic
    sorted_patterns = sorted(MOVEMENT_PATTERNS, key=len, reverse=True)

    for pattern in sorted_patterns:
        if pattern in name_lower:
            return pattern

    return None


class ExerciseSelector:
    """
    Smart exercise selection engine.

    Prioritizes:
    1. S+ tier exercises first
    2. S tier exercises second
    3. Equipment availability
    4. Training level appropriateness
    """

    def __init__(self, available_equipment: List[str], training_level: str = "intermediate"):
        """
        Args:
            available_equipment: List of equipment user has access to
            training_level: 'beginner', 'intermediate', 'advanced'
        """
        self.available_equipment = set(available_equipment)
        self.training_level = training_level

    def select_exercises_for_muscle(
        self,
        muscle: MuscleGroup,
        count: int = 2,
        tier_priority: List[ExerciseTier] = None
    ) -> List[ExerciseRecommendation]:
        """
        Select best exercises for a muscle group.

        Args:
            muscle: Target muscle group
            count: Number of exercises to select
            tier_priority: Order of tiers to check (default: [S+, S, A])

        Returns:
            List of exercise recommendations with alternatives
        """
        if tier_priority is None:
            tier_priority = [ExerciseTier.S_PLUS, ExerciseTier.S, ExerciseTier.A]

        recommendations = []
        selected_names = set()  # Track selected to avoid duplicates
        selected_patterns = set()  # Track movement patterns to avoid redundancy

        # Try each tier in priority order
        for tier in tier_priority:
            if len(recommendations) >= count:
                break

            # Get exercises of this tier for the muscle
            tier_exercises = get_exercises_by_muscle(muscle, tier_filter=[tier])

            # Filter by equipment and difficulty
            available_exercises = []
            for ex in tier_exercises:
                if ex.name in selected_names:
                    continue

                # Check for duplicate movement pattern (e.g., Cable + Dumbbell Lateral Raise)
                pattern = get_movement_pattern(ex.display_name)
                if pattern and pattern in selected_patterns:
                    continue  # Skip - already have this movement pattern

                if self._has_required_equipment(ex) and self._appropriate_difficulty(ex):
                    available_exercises.append(ex)

            # Add exercises from this tier
            for ex in available_exercises:
                if len(recommendations) >= count:
                    break

                # Double-check pattern isn't already selected (may have been added in inner loop)
                pattern = get_movement_pattern(ex.display_name)
                if pattern and pattern in selected_patterns:
                    continue

                # Find alternatives (same tier or one tier lower)
                alternatives = self._find_alternatives(ex, tier)

                # Determine location note
                location = self._get_location_note(ex)

                # Build recommendation
                reason = f"{tier.value} tier exercise"
                if tier == ExerciseTier.S_PLUS:
                    reason += " (best-of-the-best for {})".format(muscle.value)
                elif tier == ExerciseTier.S:
                    reason += " (excellent for {})".format(muscle.value)

                recommendations.append(ExerciseRecommendation(
                    exercise=ex,
                    reason=reason,
                    alternatives=alternatives,
                    location_note=location
                ))

                selected_names.add(ex.name)
                if pattern:
                    selected_patterns.add(pattern)

        # If still not enough, add from next tier down
        if len(recommendations) < count:
            remaining = count - len(recommendations)
            lower_tier = ExerciseTier.A if tier_priority[-1] == ExerciseTier.S else ExerciseTier.B

            lower_exercises = get_exercises_by_muscle(muscle, tier_filter=[lower_tier])
            for ex in lower_exercises:
                if len(recommendations) >= count:
                    break

                # Check for duplicate movement pattern
                pattern = get_movement_pattern(ex.display_name)
                if pattern and pattern in selected_patterns:
                    continue

                if ex.name not in selected_names and self._has_required_equipment(ex):
                    recommendations.append(ExerciseRecommendation(
                        exercise=ex,
                        reason=f"{lower_tier.value} tier alternative",
                        alternatives=[],
                        location_note=self._get_location_note(ex)
                    ))
                    selected_names.add(ex.name)
                    if pattern:
                        selected_patterns.add(pattern)

        return recommendations

    def build_workout_program(
        self,
        muscle_groups: List[MuscleGroup],
        exercises_per_muscle: int = 2
    ) -> Dict[MuscleGroup, List[ExerciseRecommendation]]:
        """
        Build a complete workout program with exercises for each muscle group.

        Args:
            muscle_groups: List of muscles to train
            exercises_per_muscle: How many exercises per muscle

        Returns:
            Dictionary mapping muscle groups to exercise recommendations
        """
        program = {}

        for muscle in muscle_groups:
            exercises = self.select_exercises_for_muscle(muscle, count=exercises_per_muscle)
            program[muscle] = exercises

        return program

    def get_coverage_report(self) -> Dict[str, any]:
        """
        Generate coverage report: how many S/S+ tier exercises are available.

        Returns:
            Dictionary with tier counts and coverage percentages
        """
        # All exercises in database
        all_s_plus = [ex for ex in ALL_EXERCISES if ex.tier == ExerciseTier.S_PLUS]
        all_s = [ex for ex in ALL_EXERCISES if ex.tier == ExerciseTier.S]

        # Available exercises with user's equipment
        available = get_exercises_by_equipment(list(self.available_equipment))
        available_s_plus = [ex for ex in available if ex.tier == ExerciseTier.S_PLUS]
        available_s = [ex for ex in available if ex.tier == ExerciseTier.S]

        return {
            "total_exercises": len(available),
            "s_plus_available": len(available_s_plus),
            "s_plus_total": len(all_s_plus),
            "s_plus_coverage": len(available_s_plus) / len(all_s_plus) * 100 if all_s_plus else 0,
            "s_available": len(available_s),
            "s_total": len(all_s),
            "s_coverage": len(available_s) / len(all_s) * 100 if all_s else 0,
            "missing_s_plus": [ex.display_name for ex in all_s_plus if ex not in available_s_plus],
            "missing_s": [ex.display_name for ex in all_s if ex not in available_s]
        }

    def _has_required_equipment(self, exercise: Exercise) -> bool:
        """Check if user has equipment to perform this exercise"""
        # Exercise can be done if user has ANY of the required equipment
        for equip in exercise.equipment_required:
            if equip in self.available_equipment:
                return True
        return False

    def _appropriate_difficulty(self, exercise: Exercise) -> bool:
        """Check if exercise difficulty matches user's training level"""
        difficulty_map = {
            "beginner": ["beginner"],
            "intermediate": ["beginner", "intermediate"],
            "advanced": ["beginner", "intermediate", "advanced"]
        }

        allowed_difficulties = difficulty_map.get(self.training_level, ["beginner", "intermediate"])
        return exercise.difficulty in allowed_difficulties

    def _find_alternatives(self, exercise: Exercise, tier: ExerciseTier) -> List[Exercise]:
        """Find alternative exercises (same tier or one tier lower)"""
        # Try same tier first
        same_tier_alts = get_substitutions(exercise, list(self.available_equipment), same_tier_only=True)

        # If not enough, add from tier below
        tier_below = ExerciseTier.S if tier == ExerciseTier.S_PLUS else ExerciseTier.A
        lower_tier_alts = get_substitutions(exercise, list(self.available_equipment), same_tier_only=False)
        lower_tier_alts = [ex for ex in lower_tier_alts if ex.tier == tier_below]

        # Combine (max 3 alternatives)
        alternatives = same_tier_alts[:2] + lower_tier_alts[:1]
        return alternatives[:3]

    def _get_location_note(self, exercise: Exercise) -> Optional[str]:
        """Determine where exercise can be performed"""
        # Home gym equipment
        home_equipment = {"dumbbells", "bench", "incline_bench", "pull_up_bar", "bodyweight", "resistance_bands"}

        # Check if exercise can be done at home
        can_do_home = any(eq in home_equipment for eq in exercise.equipment_required)

        # Check if requires gym-only equipment
        gym_only = {"smith_machine", "cables", "machines", "chest_press_machine", "leg_press_machine"}
        requires_gym = any(eq in gym_only for eq in exercise.equipment_required if eq in self.available_equipment)

        if can_do_home and not requires_gym:
            return "✅ Available at home"
        elif requires_gym and not can_do_home:
            return "🏋️ Requires gym (Planet Fitness)"
        else:
            return "📍 Available at both locations"


def format_exercise_recommendation(rec: ExerciseRecommendation) -> str:
    """Format recommendation for display"""
    output = []

    # Main exercise
    output.append(f"**{rec.exercise.display_name}** [{rec.exercise.tier.value}]")
    output.append(f"  {rec.reason}")

    if rec.location_note:
        output.append(f"  {rec.location_note}")

    if rec.exercise.notes:
        output.append(f"  💡 {rec.exercise.notes}")

    # Alternatives
    if rec.alternatives:
        output.append(f"  **Alternatives:**")
        for alt in rec.alternatives:
            output.append(f"    - {alt.display_name} [{alt.tier.value}]")

    return "\n".join(output)


def format_workout_program(program: Dict[MuscleGroup, List[ExerciseRecommendation]]) -> str:
    """Format complete workout program for display"""
    output = []

    for muscle, exercises in program.items():
        output.append(f"\n## {muscle.value.upper()}")
        for i, rec in enumerate(exercises, 1):
            output.append(f"\n{i}. {format_exercise_recommendation(rec)}")

    return "\n".join(output)


if __name__ == "__main__":
    # Example usage and testing
    print("=== Exercise Selection Engine Test ===\n")

    # Test 1: Home gym only
    print("TEST 1: Home Gym Only (dumbbells, bench, pull-up bar)")
    print("=" * 60)
    home_equipment = ["dumbbells", "bench", "incline_bench", "pull_up_bar", "bodyweight"]
    selector = ExerciseSelector(home_equipment, training_level="intermediate")

    # Coverage report
    coverage = selector.get_coverage_report()
    print(f"\nCoverage Report:")
    print(f"  Total exercises available: {coverage['total_exercises']}")
    print(f"  S+ tier: {coverage['s_plus_available']}/{coverage['s_plus_total']} ({coverage['s_plus_coverage']:.0f}%)")
    print(f"  S tier: {coverage['s_available']}/{coverage['s_total']} ({coverage['s_coverage']:.0f}%)")

    # Select chest exercises
    print(f"\nChest Exercises (top 2):")
    chest_recs = selector.select_exercises_for_muscle(MuscleGroup.CHEST, count=2)
    for rec in chest_recs:
        print(f"\n{format_exercise_recommendation(rec)}")

    print("\n" + "=" * 60)

    # Test 2: Planet Fitness
    print("\nTEST 2: Planet Fitness Equipment")
    print("=" * 60)
    pf_equipment = [
        "smith_machine", "cables", "dumbbells", "leg_press_machine",
        "leg_extension_machine", "leg_curl_machine", "chest_press_machine",
        "lat_pulldown_machine", "shoulder_press_machine", "pec_deck_machine",
        "hip_abduction_machine", "back_extension_bench", "chest_supported_row_machine"
    ]
    pf_selector = ExerciseSelector(pf_equipment, training_level="intermediate")

    coverage = pf_selector.get_coverage_report()
    print(f"\nCoverage Report:")
    print(f"  Total exercises available: {coverage['total_exercises']}")
    print(f"  S+ tier: {coverage['s_plus_available']}/{coverage['s_plus_total']} ({coverage['s_plus_coverage']:.0f}%)")
    print(f"  S tier: {coverage['s_available']}/{coverage['s_total']} ({coverage['s_coverage']:.0f}%)")

    # Select back exercises
    print(f"\nBack Exercises (top 3):")
    back_recs = pf_selector.select_exercises_for_muscle(MuscleGroup.BACK, count=3)
    for rec in back_recs:
        print(f"\n{format_exercise_recommendation(rec)}")

    print("\n" + "=" * 60)

    # Test 3: Combined (Home + PF)
    print("\nTEST 3: Combined Equipment (Home + Planet Fitness)")
    print("=" * 60)
    combined_equipment = list(set(home_equipment + pf_equipment))
    combined_selector = ExerciseSelector(combined_equipment, training_level="intermediate")

    coverage = combined_selector.get_coverage_report()
    print(f"\nCoverage Report:")
    print(f"  Total exercises available: {coverage['total_exercises']}")
    print(f"  S+ tier: {coverage['s_plus_available']}/{coverage['s_plus_total']} ({coverage['s_plus_coverage']:.0f}%)")
    print(f"  S tier: {coverage['s_available']}/{coverage['s_total']} ({coverage['s_coverage']:.0f}%)")
    print(f"\nMissing S+ tier exercises: {', '.join(coverage['missing_s_plus']) if coverage['missing_s_plus'] else 'None!'}")

    # Build a sample upper body program
    print(f"\nSample Upper Body Program:")
    upper_muscles = [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS]
    program = combined_selector.build_workout_program(upper_muscles, exercises_per_muscle=2)

    print(format_workout_program(program))
