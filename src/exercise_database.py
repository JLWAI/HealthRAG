"""
Exercise Database for HealthRAG
Based on Jeff Nippard's Exercise Tier List

Provides S/S+ tier exercises for optimal hypertrophy training,
with equipment requirements for smart exercise selection.
"""

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum


class ExerciseTier(Enum):
    """Jeff Nippard's exercise tier classification"""
    S_PLUS = "S+"  # Best of the best
    S = "S"        # Excellent
    A = "A"        # Very good
    B = "B"        # Good
    C = "C"        # Acceptable


class MuscleGroup(Enum):
    """Primary muscle groups"""
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    QUADS = "quads"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    ABS = "abs"


@dataclass
class Exercise:
    """Exercise definition with tier and equipment"""
    name: str
    display_name: str
    tier: ExerciseTier
    primary_muscles: List[MuscleGroup]
    secondary_muscles: List[MuscleGroup]
    equipment_required: List[str]
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    notes: Optional[str] = None


# ============================================================================
# S+ TIER EXERCISES (Best of the Best - Top 1-2 per muscle group)
# ============================================================================

S_PLUS_EXERCISES = [
    # GLUTES
    Exercise(
        name="walking_lunge",
        display_name="Walking Lunge (Dumbbell)",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.GLUTES],
        secondary_muscles=[MuscleGroup.QUADS, MuscleGroup.HAMSTRINGS],
        equipment_required=["dumbbells", "bodyweight"],
        difficulty="intermediate",
        notes="Can be done with just bodyweight or with dumbbells. Excellent for glute development."
    ),

    # QUADS
    Exercise(
        name="hack_squat",
        display_name="Hack Squat (Machine)",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["hack_squat_machine"],
        difficulty="intermediate",
        notes="Check if your Planet Fitness has this machine. If not, use Smith machine squat (S-tier)."
    ),

    # TRICEPS
    Exercise(
        name="overhead_cable_tricep_extension",
        display_name="Overhead Cable Tricep Extension",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.TRICEPS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="beginner",
        notes="Requires cable station. Planet Fitness has these."
    ),

    # BACK
    Exercise(
        name="chest_supported_row",
        display_name="Chest Supported Row (Machine or Incline Bench)",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["chest_supported_row_machine", "incline_bench", "dumbbells"],
        difficulty="beginner",
        notes="Planet Fitness has chest-supported row machine. Can also use incline bench + dumbbells."
    ),

    # BICEPS
    Exercise(
        name="face_away_beian_cable_curl",
        display_name="Face Away Bayesian Cable Curl",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.BICEPS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="intermediate",
        notes="Cable station required. Unique stretch-based bicep exercise."
    ),

    # SHOULDERS
    Exercise(
        name="cable_lateral_raise",
        display_name="Cable Lateral Raise",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="beginner",
        notes="Superior to dumbbell lateral raises for constant tension."
    ),
]


# ============================================================================
# S TIER EXERCISES (Excellent - Core of any program)
# ============================================================================

S_TIER_EXERCISES = [
    # ========== CHEST ==========
    Exercise(
        name="barbell_bench_press",
        display_name="Barbell Bench Press",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        equipment_required=["barbell", "bench", "rack"],
        difficulty="intermediate",
        notes="King of chest exercises. Not available at Planet Fitness (no free barbells)."
    ),

    Exercise(
        name="incline_dumbbell_press",
        display_name="Incline Dumbbell Press",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        equipment_required=["dumbbells", "incline_bench"],
        difficulty="intermediate",
        notes="Excellent for upper chest. Available at home + Planet Fitness."
    ),

    Exercise(
        name="machine_chest_press",
        display_name="Machine Chest Press",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        equipment_required=["chest_press_machine"],
        difficulty="beginner",
        notes="Planet Fitness has these. Great for beginners."
    ),

    Exercise(
        name="cable_crossover",
        display_name="Cable Crossover (Mid/Low)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="intermediate",
        notes="Excellent for chest isolation and stretch."
    ),

    # ========== BACK ==========
    Exercise(
        name="wide_grip_lat_pulldown",
        display_name="Wide Grip Lat Pulldown",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["lat_pulldown_machine", "cables"],
        difficulty="beginner",
        notes="Essential for lat width. Planet Fitness has this."
    ),

    Exercise(
        name="neutral_grip_lat_pulldown",
        display_name="Neutral Grip Lat Pulldown",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["lat_pulldown_machine", "cables"],
        difficulty="beginner",
        notes="Better bicep involvement than wide grip."
    ),

    Exercise(
        name="cable_row",
        display_name="Seated Cable Row",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["cables", "cable_row_station"],
        difficulty="beginner",
        notes="Mid-back thickness. Planet Fitness has this."
    ),

    Exercise(
        name="wide_grip_cable_row",
        display_name="Wide Grip Cable Row",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["cables", "cable_row_station"],
        difficulty="intermediate",
        notes="Targets upper back more than standard cable row."
    ),

    Exercise(
        name="reverse_pec_deck",
        display_name="Reverse Pec Deck (Rear Delts)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BACK, MuscleGroup.SHOULDERS],
        secondary_muscles=[],
        equipment_required=["pec_deck_machine"],
        difficulty="beginner",
        notes="Best rear delt exercise. Planet Fitness has this."
    ),

    Exercise(
        name="half_kneeling_one_arm_lat_pulldown",
        display_name="Half-Kneeling Single-Arm Lat Pulldown",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["cables"],
        difficulty="intermediate",
        notes="Unilateral lat work with good stretch."
    ),

    # ========== SHOULDERS ==========
    Exercise(
        name="cable_y_raise",
        display_name="Cable Y-Raise",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="intermediate",
        notes="Targets upper/middle delts."
    ),

    Exercise(
        name="behind_back_cable_lateral_raise",
        display_name="Behind-the-Back Cable Lateral Raise",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="intermediate",
        notes="Unique shoulder exercise for side delts."
    ),

    Exercise(
        name="reverse_cable_crossover",
        display_name="Reverse Cable Crossover (Rear Delts)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[MuscleGroup.BACK],
        equipment_required=["cables"],
        difficulty="intermediate",
        notes="Rear delt isolation via cables."
    ),

    Exercise(
        name="machine_shoulder_press",
        display_name="Machine Shoulder Press",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[MuscleGroup.TRICEPS],
        equipment_required=["shoulder_press_machine"],
        difficulty="beginner",
        notes="Planet Fitness has this. Great for front delt mass."
    ),

    # ========== BICEPS ==========
    Exercise(
        name="preacher_curl",
        display_name="Preacher Curl (Barbell/Dumbbell)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BICEPS],
        secondary_muscles=[],
        equipment_required=["preacher_bench", "barbell", "dumbbells"],
        difficulty="beginner",
        notes="Planet Fitness has preacher curl station."
    ),

    Exercise(
        name="machine_preacher_curl",
        display_name="Machine Preacher Curl",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.BICEPS],
        secondary_muscles=[],
        equipment_required=["preacher_curl_machine"],
        difficulty="beginner",
        notes="Planet Fitness may have this machine."
    ),

    # ========== TRICEPS ==========
    Exercise(
        name="skull_crusher",
        display_name="Skull Crusher (Lying Tricep Extension)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.TRICEPS],
        secondary_muscles=[],
        equipment_required=["dumbbells", "barbell", "bench"],
        difficulty="intermediate",
        notes="Can do at home with dumbbells or at gym with barbell."
    ),

    # ========== QUADS ==========
    Exercise(
        name="barbell_back_squat",
        display_name="Barbell Back Squat (High Bar)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS],
        equipment_required=["barbell", "rack"],
        difficulty="advanced",
        notes="King of leg exercises. S-tier alternative to hack squat. NOT available at Planet Fitness (no free barbells)."
    ),

    Exercise(
        name="landmine_hack_squat",
        display_name="Landmine Hack Squat (Viking Press Attachment)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["landmine", "barbell"],
        difficulty="intermediate",
        notes="Home alternative to hack squat machine using Viking Press landmine attachment. Excellent quad builder."
    ),

    Exercise(
        name="smith_machine_squat",
        display_name="Smith Machine Squat",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["smith_machine"],
        difficulty="intermediate",
        notes="Planet Fitness has Smith machine. Excellent barbell squat alternative."
    ),

    Exercise(
        name="bulgarian_split_squat",
        display_name="Bulgarian Split Squat (Dumbbell)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["dumbbells", "bench", "step"],
        difficulty="intermediate",
        notes="Can do at home or gym. Unilateral quad builder."
    ),

    Exercise(
        name="pendulum_squat",
        display_name="Pendulum Squat (Machine)",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["pendulum_squat_machine"],
        difficulty="intermediate",
        notes="Rare specialty machine. Most gyms don't have this."
    ),

    # ========== GLUTES ==========
    Exercise(
        name="machine_hip_abduction",
        display_name="Machine Hip Abduction",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.GLUTES],
        secondary_muscles=[],
        equipment_required=["hip_abduction_machine"],
        difficulty="beginner",
        notes="Planet Fitness has this. Great for glute medius."
    ),

    Exercise(
        name="elevated_front_foot_lunge",
        display_name="Elevated Front Foot Lunge",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.GLUTES],
        secondary_muscles=[MuscleGroup.QUADS],
        equipment_required=["dumbbells", "step", "platform"],
        difficulty="intermediate",
        notes="Front foot on step/platform. Home or gym."
    ),

    Exercise(
        name="45_degree_back_extension",
        display_name="45-Degree Back Extension",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.GLUTES],
        secondary_muscles=[MuscleGroup.HAMSTRINGS, MuscleGroup.BACK],
        equipment_required=["back_extension_bench"],
        difficulty="beginner",
        notes="Planet Fitness has this."
    ),
]


# ============================================================================
# A TIER EXERCISES (Very Good - Solid alternatives)
# ============================================================================

A_TIER_EXERCISES = [
    # CHEST
    Exercise(
        name="dumbbell_bench_press",
        display_name="Flat Dumbbell Bench Press",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        equipment_required=["dumbbells", "bench"],
        difficulty="intermediate",
        notes="Available at home + gym."
    ),

    Exercise(
        name="push_up",
        display_name="Push-Up",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        equipment_required=["bodyweight"],
        difficulty="beginner",
        notes="Can do anywhere. Progress with weight vest or deficit."
    ),

    # BACK
    Exercise(
        name="pull_up",
        display_name="Pull-Up",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["pull_up_bar"],
        difficulty="intermediate",
        notes="Home gym has pull-up bar. Planet Fitness has assisted pull-up machine."
    ),

    Exercise(
        name="dumbbell_row",
        display_name="Single-Arm Dumbbell Row",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["dumbbells", "bench"],
        difficulty="beginner",
        notes="Classic back builder. Home or gym."
    ),

    Exercise(
        name="landmine_t_bar_row",
        display_name="Landmine T-Bar Row (Viking Press Attachment)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.BACK],
        secondary_muscles=[MuscleGroup.BICEPS],
        equipment_required=["landmine", "barbell"],
        difficulty="intermediate",
        notes="Excellent back thickness builder using Viking Press landmine attachment. Home gym friendly."
    ),

    # SHOULDERS
    Exercise(
        name="dumbbell_lateral_raise",
        display_name="Dumbbell Lateral Raise",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[],
        equipment_required=["dumbbells"],
        difficulty="beginner",
        notes="Home or gym. Cable lateral raise (S+) is better but this works."
    ),

    Exercise(
        name="dumbbell_shoulder_press",
        display_name="Seated Dumbbell Shoulder Press",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[MuscleGroup.TRICEPS],
        equipment_required=["dumbbells", "bench"],
        difficulty="intermediate",
        notes="Home or gym."
    ),

    Exercise(
        name="landmine_press",
        display_name="Landmine Shoulder Press (Viking Press)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[MuscleGroup.TRICEPS],
        equipment_required=["landmine", "barbell"],
        difficulty="intermediate",
        notes="Unique shoulder press variation using Viking Press landmine attachment. Great for shoulder-friendly pressing."
    ),

    # BICEPS
    Exercise(
        name="dumbbell_curl",
        display_name="Dumbbell Curl (Standing/Seated)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.BICEPS],
        secondary_muscles=[],
        equipment_required=["dumbbells"],
        difficulty="beginner",
        notes="Classic bicep exercise. Home or gym."
    ),

    Exercise(
        name="hammer_curl",
        display_name="Hammer Curl",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.BICEPS],
        secondary_muscles=[],
        equipment_required=["dumbbells"],
        difficulty="beginner",
        notes="Targets brachialis more. Home or gym."
    ),

    # TRICEPS
    Exercise(
        name="dumbbell_overhead_extension",
        display_name="Dumbbell Overhead Tricep Extension",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.TRICEPS],
        secondary_muscles=[],
        equipment_required=["dumbbells"],
        difficulty="beginner",
        notes="Home or gym alternative to cable overhead extension."
    ),

    Exercise(
        name="close_grip_bench_press",
        display_name="Close-Grip Bench Press",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.TRICEPS],
        secondary_muscles=[MuscleGroup.CHEST, MuscleGroup.SHOULDERS],
        equipment_required=["barbell", "bench", "rack"],
        difficulty="intermediate",
        notes="Compound tricep movement. Not available at Planet Fitness."
    ),

    # LEGS
    Exercise(
        name="leg_press",
        display_name="Leg Press (Machine)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["leg_press_machine"],
        difficulty="beginner",
        notes="Planet Fitness has leg press."
    ),

    Exercise(
        name="leg_extension",
        display_name="Leg Extension (Machine)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[],
        equipment_required=["leg_extension_machine"],
        difficulty="beginner",
        notes="Quad isolation. Planet Fitness has this."
    ),

    Exercise(
        name="leg_curl",
        display_name="Leg Curl (Machine)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.HAMSTRINGS],
        secondary_muscles=[],
        equipment_required=["leg_curl_machine"],
        difficulty="beginner",
        notes="Hamstring isolation. Planet Fitness has this."
    ),

    Exercise(
        name="goblet_squat",
        display_name="Goblet Squat (Dumbbell)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.QUADS],
        secondary_muscles=[MuscleGroup.GLUTES],
        equipment_required=["dumbbells"],
        difficulty="beginner",
        notes="Beginner-friendly squat. Home or gym."
    ),

    # ABS
    Exercise(
        name="cable_crunch",
        display_name="Cable Crunch (Kneeling)",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.ABS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="beginner",
        notes="Weighted ab work. Planet Fitness has cables."
    ),

    Exercise(
        name="ab_wheel_rollout",
        display_name="Ab Wheel Rollout",
        tier=ExerciseTier.A,
        primary_muscles=[MuscleGroup.ABS],
        secondary_muscles=[],
        equipment_required=["ab_wheel"],
        difficulty="advanced",
        notes="Extremely effective core exercise."
    ),
]


# ============================================================================
# EQUIPMENT DATABASE
# ============================================================================

EQUIPMENT_MAPPING = {
    # Home Gym Equipment (from TIER_LIST_COVERAGE_ANALYSIS)
    "dumbbells": "Dumbbells (5-75 lbs)",
    "bench": "Adjustable Bench",
    "incline_bench": "Incline Bench",
    "pull_up_bar": "Pull-Up Bar",
    "resistance_bands": "Resistance Bands",
    "bodyweight": "Bodyweight Only",
    "step": "Step/Platform",
    "ab_wheel": "Ab Wheel",

    # Planet Fitness Equipment
    "smith_machine": "Smith Machine",
    "cables": "Cable Station",
    "cable_row_station": "Cable Row Station",
    "leg_press_machine": "Leg Press Machine",
    "leg_extension_machine": "Leg Extension Machine",
    "leg_curl_machine": "Leg Curl Machine",
    "chest_press_machine": "Chest Press Machine",
    "lat_pulldown_machine": "Lat Pulldown Machine",
    "shoulder_press_machine": "Shoulder Press Machine",
    "pec_deck_machine": "Pec Deck Machine",
    "preacher_curl_machine": "Preacher Curl Machine",
    "hip_abduction_machine": "Hip Abduction Machine",
    "back_extension_bench": "45° Back Extension Bench",
    "chest_supported_row_machine": "Chest Supported Row Machine",
    "preacher_bench": "Preacher Bench",
    "assisted_pull_up_machine": "Assisted Pull-Up Machine",

    # Specialty Equipment (rare, may not be available)
    "barbell": "Barbell",
    "rack": "Squat/Power Rack",
    "hack_squat_machine": "Hack Squat Machine",
    "pendulum_squat_machine": "Pendulum Squat Machine",
}


# Combined exercise lists
ALL_EXERCISES = S_PLUS_EXERCISES + S_TIER_EXERCISES + A_TIER_EXERCISES


def get_exercises_by_tier(tier: ExerciseTier) -> List[Exercise]:
    """Get all exercises of a specific tier"""
    return [ex for ex in ALL_EXERCISES if ex.tier == tier]


def get_exercises_by_muscle(muscle: MuscleGroup, tier_filter: Optional[List[ExerciseTier]] = None) -> List[Exercise]:
    """
    Get exercises for a muscle group, optionally filtered by tier.

    Args:
        muscle: Target muscle group
        tier_filter: List of tiers to include (e.g., [ExerciseTier.S_PLUS, ExerciseTier.S])

    Returns:
        List of exercises matching criteria
    """
    exercises = [ex for ex in ALL_EXERCISES if muscle in ex.primary_muscles]

    if tier_filter:
        exercises = [ex for ex in exercises if ex.tier in tier_filter]

    # Sort by tier (S+ first, then S, then A)
    tier_order = {ExerciseTier.S_PLUS: 0, ExerciseTier.S: 1, ExerciseTier.A: 2, ExerciseTier.B: 3}
    exercises.sort(key=lambda ex: tier_order.get(ex.tier, 99))

    return exercises


def get_exercises_by_equipment(available_equipment: List[str], muscle: Optional[MuscleGroup] = None) -> List[Exercise]:
    """
    Get exercises that can be performed with available equipment.

    Args:
        available_equipment: List of equipment user has access to
        muscle: Optional muscle group filter

    Returns:
        List of exercises that can be performed
    """
    available_set = set(available_equipment)

    def has_equipment(exercise: Exercise) -> bool:
        """Check if user has at least one required equipment option"""
        # If exercise requires multiple equipment types (all must be present)
        # OR if it has alternative options (any one will do)
        # We'll use OR logic: if user has ANY of the required equipment, they can do it

        for equip in exercise.equipment_required:
            if equip in available_set:
                return True
        return False

    exercises = [ex for ex in ALL_EXERCISES if has_equipment(ex)]

    if muscle:
        exercises = [ex for ex in exercises if muscle in ex.primary_muscles]

    # Sort by tier
    tier_order = {ExerciseTier.S_PLUS: 0, ExerciseTier.S: 1, ExerciseTier.A: 2}
    exercises.sort(key=lambda ex: tier_order.get(ex.tier, 99))

    return exercises


def get_exercise_by_name(name: str) -> Optional[Exercise]:
    """Get exercise by internal name or display name"""
    # First try exact match on internal name
    for ex in ALL_EXERCISES:
        if ex.name == name:
            return ex

    # Then try exact match on display name
    for ex in ALL_EXERCISES:
        if ex.display_name == name:
            return ex

    # Finally try case-insensitive match on display name
    name_lower = name.lower()
    for ex in ALL_EXERCISES:
        if ex.display_name.lower() == name_lower:
            return ex

    return None


def get_substitutions(exercise: Exercise, available_equipment: List[str], same_tier_only: bool = True) -> List[Exercise]:
    """
    Find substitute exercises for the same muscle group.

    Args:
        exercise: Original exercise to substitute
        available_equipment: Equipment user has
        same_tier_only: If True, only return exercises of same tier

    Returns:
        List of substitute exercises
    """
    # Get exercises for same primary muscle
    substitutes = get_exercises_by_equipment(
        available_equipment,
        muscle=exercise.primary_muscles[0]
    )

    # Remove the original exercise
    substitutes = [ex for ex in substitutes if ex.name != exercise.name]

    # Filter by tier if requested
    if same_tier_only:
        substitutes = [ex for ex in substitutes if ex.tier == exercise.tier]

    return substitutes


if __name__ == "__main__":
    # Example usage and testing
    print("=== Exercise Database Test ===\n")

    # Test 1: S+ tier exercises
    print("S+ TIER EXERCISES:")
    s_plus = get_exercises_by_tier(ExerciseTier.S_PLUS)
    for ex in s_plus:
        print(f"  - {ex.display_name} ({ex.primary_muscles[0].value})")
    print(f"Total S+ tier: {len(s_plus)}\n")

    # Test 2: Get chest exercises (S+ and S tier)
    print("CHEST EXERCISES (S+/S tier):")
    chest_exercises = get_exercises_by_muscle(
        MuscleGroup.CHEST,
        tier_filter=[ExerciseTier.S_PLUS, ExerciseTier.S]
    )
    for ex in chest_exercises:
        print(f"  [{ex.tier.value}] {ex.display_name}")
    print()

    # Test 3: Equipment-based selection (Home gym)
    print("HOME GYM EXERCISES (dumbbells, bench, pull-up bar):")
    home_equipment = ["dumbbells", "bench", "incline_bench", "pull_up_bar", "bodyweight"]
    home_exercises = get_exercises_by_equipment(home_equipment)
    print(f"  Total exercises: {len(home_exercises)}")
    print(f"  S+ tier: {len([ex for ex in home_exercises if ex.tier == ExerciseTier.S_PLUS])}")
    print(f"  S tier: {len([ex for ex in home_exercises if ex.tier == ExerciseTier.S])}")
    print(f"  A tier: {len([ex for ex in home_exercises if ex.tier == ExerciseTier.A])}")
    print()

    # Test 4: Planet Fitness exercises
    print("PLANET FITNESS EXERCISES:")
    pf_equipment = [
        "smith_machine", "cables", "dumbbells", "leg_press_machine",
        "leg_extension_machine", "leg_curl_machine", "chest_press_machine",
        "lat_pulldown_machine", "shoulder_press_machine", "pec_deck_machine",
        "hip_abduction_machine", "back_extension_bench", "chest_supported_row_machine"
    ]
    pf_exercises = get_exercises_by_equipment(pf_equipment)
    print(f"  Total exercises: {len(pf_exercises)}")
    print(f"  S+ tier: {len([ex for ex in pf_exercises if ex.tier == ExerciseTier.S_PLUS])}")
    print(f"  S tier: {len([ex for ex in pf_exercises if ex.tier == ExerciseTier.S])}")
    print()

    # Test 5: Combined coverage (Home + PF)
    print("COMBINED (Home + Planet Fitness):")
    combined_equipment = list(set(home_equipment + pf_equipment))
    combined_exercises = get_exercises_by_equipment(combined_equipment)
    print(f"  Total exercises: {len(combined_exercises)}")
    print(f"  S+ tier: {len([ex for ex in combined_exercises if ex.tier == ExerciseTier.S_PLUS])}")
    print(f"  S tier: {len([ex for ex in combined_exercises if ex.tier == ExerciseTier.S])}")
    print()

    # Test 6: Find substitutions
    print("SUBSTITUTIONS TEST:")
    barbell_bench = get_exercise_by_name("barbell_bench_press")
    if barbell_bench:
        subs = get_substitutions(barbell_bench, home_equipment, same_tier_only=False)
        print(f"  Substitutes for {barbell_bench.display_name} (home gym):")
        for sub in subs[:3]:
            print(f"    [{sub.tier.value}] {sub.display_name}")
