"""
Mesocycle Templates for HealthRAG
Training split definitions (Upper/Lower, PPL, Full Body, etc.)

Based on RP Hypertrophy App's template system but with better organization
and equipment awareness.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from exercise_database import MuscleGroup


class TrainingSplit(Enum):
    """Training split types"""
    FULL_BODY = "full_body"
    UPPER_LOWER = "upper_lower"
    PPL = "push_pull_legs"
    BRO_SPLIT = "bro_split"
    UPPER_LOWER_PPL_HYBRID = "upper_lower_ppl"


@dataclass
class WorkoutDay:
    """Single workout day definition"""
    name: str  # "Upper A", "Push", "Leg Day", etc.
    muscle_groups: List[MuscleGroup]
    priority_order: List[MuscleGroup]  # Which muscles to train first
    notes: Optional[str] = None


@dataclass
class MesocycleTemplate:
    """Complete mesocycle template"""
    name: str
    display_name: str
    split_type: TrainingSplit
    days_per_week: int
    workout_days: List[WorkoutDay]
    description: str
    best_for: List[str]  # e.g., ["beginners", "time_constrained"]
    min_training_level: str  # "beginner", "intermediate", "advanced"


# ============================================================================
# FULL BODY TEMPLATES (3x per week)
# ============================================================================

FULL_BODY_3X = MesocycleTemplate(
    name="full_body_3x",
    display_name="Full Body 3x per Week",
    split_type=TrainingSplit.FULL_BODY,
    days_per_week=3,
    workout_days=[
        WorkoutDay(
            name="Full Body A",
            muscle_groups=[
                MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.QUADS,
                MuscleGroup.SHOULDERS, MuscleGroup.BICEPS, MuscleGroup.TRICEPS
            ],
            priority_order=[
                MuscleGroup.QUADS,    # Legs first (most demanding)
                MuscleGroup.CHEST,    # Push
                MuscleGroup.BACK,     # Pull
                MuscleGroup.SHOULDERS,
                MuscleGroup.BICEPS,
                MuscleGroup.TRICEPS
            ],
            notes="Start with compound leg exercise, then upper body compounds, finish with arms"
        ),
        WorkoutDay(
            name="Full Body B",
            muscle_groups=[
                MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS, MuscleGroup.BACK,
                MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS, MuscleGroup.BICEPS
            ],
            priority_order=[
                MuscleGroup.GLUTES,      # Leg focus (posterior chain)
                MuscleGroup.HAMSTRINGS,
                MuscleGroup.BACK,
                MuscleGroup.CHEST,
                MuscleGroup.SHOULDERS,
                MuscleGroup.TRICEPS,
                MuscleGroup.BICEPS
            ],
            notes="Posterior chain emphasis, then chest/back, finish with arms"
        ),
        WorkoutDay(
            name="Full Body C",
            muscle_groups=[
                MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.CHEST,
                MuscleGroup.BACK, MuscleGroup.SHOULDERS, MuscleGroup.BICEPS, MuscleGroup.TRICEPS
            ],
            priority_order=[
                MuscleGroup.QUADS,
                MuscleGroup.GLUTES,
                MuscleGroup.BACK,
                MuscleGroup.CHEST,
                MuscleGroup.SHOULDERS,
                MuscleGroup.TRICEPS,
                MuscleGroup.BICEPS
            ],
            notes="Balanced full body, alternating push/pull"
        )
    ],
    description="Hit every muscle group 3x per week. Efficient for beginners or time-constrained schedules.",
    best_for=["beginners", "time_constrained", "3_days_available"],
    min_training_level="beginner"
)


# ============================================================================
# UPPER/LOWER TEMPLATES (4x per week)
# ============================================================================

UPPER_LOWER_4X = MesocycleTemplate(
    name="upper_lower_4x",
    display_name="Upper/Lower 4x per Week",
    split_type=TrainingSplit.UPPER_LOWER,
    days_per_week=4,
    workout_days=[
        WorkoutDay(
            name="Upper A (Chest/Back Focus)",
            muscle_groups=[MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS,
                          MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS,
                          MuscleGroup.TRICEPS, MuscleGroup.BICEPS],
            notes="Heavy compound chest & back work"
        ),
        WorkoutDay(
            name="Lower A (Quad Focus)",
            muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            priority_order=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            notes="Squat pattern emphasis"
        ),
        WorkoutDay(
            name="Upper B (Shoulder/Arm Focus)",
            muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.BACK, MuscleGroup.CHEST,
                          MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.SHOULDERS, MuscleGroup.BACK, MuscleGroup.CHEST,
                          MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            notes="Shoulder and arm emphasis, lighter chest/back volume"
        ),
        WorkoutDay(
            name="Lower B (Glute/Hamstring Focus)",
            muscle_groups=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS, MuscleGroup.QUADS,
                          MuscleGroup.CALVES],
            priority_order=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS, MuscleGroup.QUADS,
                          MuscleGroup.CALVES],
            notes="Hip hinge/posterior chain emphasis"
        )
    ],
    description="Classic upper/lower split. Each muscle group trained 2x per week.",
    best_for=["intermediate", "4_days_available", "balanced_development", "hypertrophy", "hypertrophy_focus"],
    min_training_level="intermediate"
)


# ============================================================================
# PUSH/PULL/LEGS TEMPLATES (6x per week)
# ============================================================================

PPL_6X = MesocycleTemplate(
    name="ppl_6x",
    display_name="Push/Pull/Legs 6x per Week",
    split_type=TrainingSplit.PPL,
    days_per_week=6,
    workout_days=[
        WorkoutDay(
            name="Push A (Chest Focus)",
            muscle_groups=[MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.CHEST, MuscleGroup.SHOULDERS, MuscleGroup.TRICEPS],
            notes="Heavy pressing day"
        ),
        WorkoutDay(
            name="Pull A (Back Width)",
            muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS],
            priority_order=[MuscleGroup.BACK, MuscleGroup.BICEPS],
            notes="Vertical pulling emphasis (lat pulldowns, pull-ups)"
        ),
        WorkoutDay(
            name="Legs A (Quad Focus)",
            muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            priority_order=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            notes="Squat pattern, quad emphasis"
        ),
        WorkoutDay(
            name="Push B (Shoulder Focus)",
            muscle_groups=[MuscleGroup.SHOULDERS, MuscleGroup.CHEST, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.SHOULDERS, MuscleGroup.CHEST, MuscleGroup.TRICEPS],
            notes="Overhead pressing and lateral raises"
        ),
        WorkoutDay(
            name="Pull B (Back Thickness)",
            muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS],
            priority_order=[MuscleGroup.BACK, MuscleGroup.BICEPS],
            notes="Horizontal pulling emphasis (rows)"
        ),
        WorkoutDay(
            name="Legs B (Glute/Hamstring Focus)",
            muscle_groups=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS, MuscleGroup.QUADS,
                          MuscleGroup.CALVES],
            priority_order=[MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS, MuscleGroup.QUADS,
                          MuscleGroup.CALVES],
            notes="Hip hinge/lunge pattern, posterior chain"
        )
    ],
    description="Each muscle group trained 2x per week with high frequency. Popular for hypertrophy.",
    best_for=["advanced", "6_days_available", "hypertrophy_focus"],
    min_training_level="intermediate"
)


# ============================================================================
# BRO SPLIT TEMPLATE (5x per week)
# ============================================================================

BRO_SPLIT_5X = MesocycleTemplate(
    name="bro_split_5x",
    display_name="Bro Split 5x per Week",
    split_type=TrainingSplit.BRO_SPLIT,
    days_per_week=5,
    workout_days=[
        WorkoutDay(
            name="Chest Day",
            muscle_groups=[MuscleGroup.CHEST, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.CHEST, MuscleGroup.TRICEPS],
            notes="High volume chest with tricep assistance work"
        ),
        WorkoutDay(
            name="Back Day",
            muscle_groups=[MuscleGroup.BACK, MuscleGroup.BICEPS],
            priority_order=[MuscleGroup.BACK, MuscleGroup.BICEPS],
            notes="High volume back with bicep assistance work"
        ),
        WorkoutDay(
            name="Shoulder Day",
            muscle_groups=[MuscleGroup.SHOULDERS],
            priority_order=[MuscleGroup.SHOULDERS],
            notes="Dedicated shoulder volume (front, side, rear delts)"
        ),
        WorkoutDay(
            name="Leg Day",
            muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            priority_order=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            notes="High volume legs - all muscle groups"
        ),
        WorkoutDay(
            name="Arm Day",
            muscle_groups=[MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            notes="Dedicated arm volume"
        )
    ],
    description="Classic bodybuilding split. Each muscle group hit 1x per week with high volume.",
    best_for=["advanced", "5_days_available", "high_volume_tolerance"],
    min_training_level="intermediate"
)


# ============================================================================
# SPECIALIZATION TEMPLATES
# ============================================================================

ARM_SPECIALIZATION = MesocycleTemplate(
    name="arm_specialization_4x",
    display_name="Arm Specialization (Upper/Lower + Arms)",
    split_type=TrainingSplit.UPPER_LOWER,
    days_per_week=4,
    workout_days=[
        WorkoutDay(
            name="Upper (Chest/Back)",
            muscle_groups=[MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS],
            priority_order=[MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.SHOULDERS],
            notes="Minimal arm work - arms trained separately"
        ),
        WorkoutDay(
            name="Lower",
            muscle_groups=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES],
            priority_order=[MuscleGroup.QUADS, MuscleGroup.GLUTES, MuscleGroup.HAMSTRINGS,
                          MuscleGroup.CALVES]
        ),
        WorkoutDay(
            name="Arms A (Volume)",
            muscle_groups=[MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            notes="High volume arm work"
        ),
        WorkoutDay(
            name="Arms B (Strength)",
            muscle_groups=[MuscleGroup.BICEPS, MuscleGroup.TRICEPS],
            priority_order=[MuscleGroup.TRICEPS, MuscleGroup.BICEPS],
            notes="Heavier arm work"
        )
    ],
    description="Specialization template for arm growth. Arms trained 2x per week with high volume.",
    best_for=["intermediate", "arm_growth", "4_days_available"],
    min_training_level="intermediate"
)


# ============================================================================
# TEMPLATE DATABASE
# ============================================================================

ALL_TEMPLATES = [
    FULL_BODY_3X,
    UPPER_LOWER_4X,
    PPL_6X,
    BRO_SPLIT_5X,
    ARM_SPECIALIZATION
]


def get_templates_by_days(days_per_week: int) -> List[MesocycleTemplate]:
    """Get templates matching available training days"""
    return [t for t in ALL_TEMPLATES if t.days_per_week == days_per_week]


def get_template_by_name(name: str) -> Optional[MesocycleTemplate]:
    """Get template by internal name"""
    for template in ALL_TEMPLATES:
        if template.name == name:
            return template
    return None


def get_recommended_template(
    days_per_week: int,
    training_level: str,
    goals: List[str]
) -> Optional[MesocycleTemplate]:
    """
    Recommend template based on user constraints.

    Args:
        days_per_week: How many days user can train
        training_level: 'beginner', 'intermediate', 'advanced'
        goals: List like ["hypertrophy", "time_efficient"]

    Returns:
        Recommended template or None
    """
    # Filter by days available
    matching_days = get_templates_by_days(days_per_week)

    # Filter by training level
    level_order = {"beginner": 0, "intermediate": 1, "advanced": 2}
    user_level = level_order.get(training_level, 1)

    appropriate = []
    for template in matching_days:
        template_level = level_order.get(template.min_training_level, 0)
        if template_level <= user_level:
            appropriate.append(template)

    if not appropriate:
        return None

    # Score templates by goal alignment
    def score_template(template: MesocycleTemplate) -> int:
        score = 0
        for goal in goals:
            if goal in template.best_for:
                score += 1
        return score

    appropriate.sort(key=score_template, reverse=True)

    return appropriate[0] if appropriate else None


def format_template(template: MesocycleTemplate, show_workouts: bool = True) -> str:
    """Format template for display"""
    output = []

    output.append(f"# {template.display_name}")
    output.append(f"**{template.days_per_week} days per week**")
    output.append(f"\n{template.description}")
    output.append(f"\n**Best for:** {', '.join(template.best_for)}")
    output.append(f"**Minimum level:** {template.min_training_level.capitalize()}")

    if show_workouts:
        output.append(f"\n## Workout Structure:")
        for i, day in enumerate(template.workout_days, 1):
            output.append(f"\n**Day {i}: {day.name}**")
            output.append(f"  Muscles: {', '.join([m.value.capitalize() for m in day.muscle_groups])}")
            if day.notes:
                output.append(f"  💡 {day.notes}")

    return "\n".join(output)


if __name__ == "__main__":
    # Example usage and testing
    print("=== Mesocycle Templates Test ===\n")

    # Test 1: List all templates
    print("AVAILABLE TEMPLATES:")
    print("=" * 60)
    for template in ALL_TEMPLATES:
        print(f"{template.display_name} ({template.days_per_week} days/week)")
        print(f"  Best for: {', '.join(template.best_for)}")
        print()

    # Test 2: Get templates for 4 days/week
    print("\nTEMPLATES FOR 4 DAYS PER WEEK:")
    print("=" * 60)
    four_day_templates = get_templates_by_days(4)
    for template in four_day_templates:
        print(format_template(template, show_workouts=False))
        print()

    # Test 3: Recommend template
    print("\nRECOMMENDED TEMPLATE:")
    print("=" * 60)
    print("User: Intermediate, 6 days available, hypertrophy focus\n")
    recommended = get_recommended_template(
        days_per_week=6,
        training_level="intermediate",
        goals=["hypertrophy_focus", "advanced"]
    )
    if recommended:
        print(format_template(recommended, show_workouts=True))

    # Test 4: Full template details
    print("\n\n" + "=" * 60)
    print("FULL BODY 3X DETAILS:")
    print("=" * 60)
    print(format_template(FULL_BODY_3X, show_workouts=True))
