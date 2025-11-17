"""
Progressive Overload System for HealthRAG
RIR (Reps in Reserve) progression and load increases

Based on RP's progressive overload methodology:
- Start with 3 RIR (3 reps left in tank)
- Decrease RIR each week (3 → 2 → 2 → 1 → 0)
- Increase load when RIR drops
- Deload resets progression

RIR = Reps in Reserve (how many more reps you could do)
- 3 RIR = could do 3 more reps (moderate intensity)
- 1 RIR = could do 1 more rep (hard set)
- 0 RIR = taken to failure (max effort)
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from exercise_database import Exercise, MuscleGroup


@dataclass
class RepScheme:
    """Rep range definition"""
    min_reps: int
    max_reps: int
    display: str  # e.g., "8-12 reps"

    def target_reps(self) -> int:
        """Get target reps (midpoint of range)"""
        return (self.min_reps + self.max_reps) // 2


# Standard rep ranges for hypertrophy
REP_SCHEMES = {
    "strength": RepScheme(min_reps=3, max_reps=6, display="3-6 reps"),
    "hypertrophy_low": RepScheme(min_reps=6, max_reps=8, display="6-8 reps"),
    "hypertrophy": RepScheme(min_reps=8, max_reps=12, display="8-12 reps"),
    "hypertrophy_high": RepScheme(min_reps=12, max_reps=15, display="12-15 reps"),
    "endurance": RepScheme(min_reps=15, max_reps=20, display="15-20 reps"),
}


def get_rep_scheme_for_exercise(exercise: Exercise) -> RepScheme:
    """
    Get appropriate rep scheme for an exercise.

    Logic:
    - Big compounds (squat, bench, deadlift): 6-8 reps
    - Most exercises: 8-12 reps (hypertrophy sweet spot)
    - Isolation (biceps, triceps, calves): 12-15 reps
    """
    # Big compound movements (lower reps, heavier weight)
    compound_exercises = [
        "barbell_back_squat", "barbell_bench_press", "deadlift",
        "overhead_press", "weighted_pull_up"
    ]

    if exercise.name in compound_exercises:
        return REP_SCHEMES["hypertrophy_low"]

    # Isolation exercises (higher reps, mind-muscle connection)
    isolation_exercises = [
        "cable_lateral_raise", "cable_crossover", "dumbbell_curl",
        "hammer_curl", "tricep_extension", "leg_extension", "leg_curl"
    ]

    if exercise.name in isolation_exercises:
        return REP_SCHEMES["hypertrophy_high"]

    # Default: standard hypertrophy range (8-12 reps)
    return REP_SCHEMES["hypertrophy"]


@dataclass
class WeeklyProgression:
    """Weekly progression prescription"""
    week: int
    sets: int
    reps_scheme: RepScheme
    rir: int  # Reps in Reserve
    load_change: str  # "+5 lbs", "+2.5%", "same"
    notes: str


def calculate_rir_progression(weeks: int = 5) -> List[int]:
    """
    Calculate RIR progression over mesocycle.

    Standard RP progression:
    Week 1: 3 RIR (moderate, building volume)
    Week 2: 2 RIR (moderate-hard)
    Week 3: 2 RIR (maintain intensity)
    Week 4: 1 RIR (hard sets)
    Week 5: 0 RIR (taken to failure, peak intensity)
    Week 6: 3 RIR (deload, easy)

    Args:
        weeks: Number of accumulation weeks (default 5)

    Returns:
        List of RIR values per week
    """
    if weeks == 4:
        return [3, 2, 1, 0, 3]  # 4-week + deload
    elif weeks == 5:
        return [3, 2, 2, 1, 0, 3]  # 5-week + deload
    elif weeks == 6:
        return [3, 2, 2, 1, 0, 0, 3]  # 6-week + deload
    else:
        # Default progression for any length
        rir_list = [3]  # Start at 3 RIR
        for week in range(1, weeks):
            if week < weeks // 2:
                rir_list.append(2)  # First half: 2 RIR
            elif week < weeks - 1:
                rir_list.append(1)  # Middle: 1 RIR
            else:
                rir_list.append(0)  # Last week: 0 RIR (failure)
        rir_list.append(3)  # Deload: 3 RIR
        return rir_list


def calculate_load_progression(
    weekly_rir: List[int],
    starting_load: float,
    exercise_type: str = "compound"  # 'compound' or 'isolation'
) -> List[Tuple[float, str]]:
    """
    Calculate load progression based on RIR changes.

    Logic:
    - When RIR drops, increase load to maintain intensity
    - Compounds: +5 lbs per increase
    - Isolation: +2.5 lbs per increase (smaller jumps)

    Args:
        weekly_rir: RIR values per week
        starting_load: Starting weight (lbs)
        exercise_type: 'compound' or 'isolation'

    Returns:
        List of (load, note) tuples

    Example:
    Week 1: 185 lbs @ 3 RIR
    Week 2: 190 lbs @ 2 RIR (RIR dropped, add weight)
    Week 3: 190 lbs @ 2 RIR (RIR same, maintain weight)
    Week 4: 195 lbs @ 1 RIR (RIR dropped, add weight)
    Week 5: 200 lbs @ 0 RIR (RIR dropped, add weight)
    Week 6: 175 lbs @ 3 RIR (deload = -10%)
    """
    load_increment = 5 if exercise_type == "compound" else 2.5

    loads = []
    current_load = starting_load
    previous_rir = None

    for week, rir in enumerate(weekly_rir, 1):
        # Deload week (last week)
        if week == len(weekly_rir):
            deload_load = starting_load * 0.9  # 10% reduction
            loads.append((deload_load, "Deload: -10% from starting weight"))
            continue

        # If RIR dropped from previous week, increase load
        if previous_rir is not None and rir < previous_rir:
            current_load += load_increment
            note = f"+{load_increment} lbs (RIR dropped from {previous_rir} → {rir})"
        else:
            note = "Maintain weight (RIR unchanged or first week)"

        loads.append((current_load, note))
        previous_rir = rir

    return loads


def build_exercise_progression(
    exercise: Exercise,
    weekly_sets: List[int],
    weeks: int = 5
) -> List[WeeklyProgression]:
    """
    Build complete weekly progression for an exercise.

    Args:
        exercise: Exercise to program
        weekly_sets: Sets per week for each week
        weeks: Number of accumulation weeks

    Returns:
        List of weekly progression prescriptions
    """
    rep_scheme = get_rep_scheme_for_exercise(exercise)
    rir_progression = calculate_rir_progression(weeks)

    # Determine if compound or isolation
    exercise_type = "compound" if (exercise.notes and "compound" in exercise.notes.lower()) else "isolation"

    # Example starting load (would come from user's training history in real app)
    starting_load = 185 if exercise_type == "compound" else 25

    load_progression = calculate_load_progression(rir_progression, starting_load, exercise_type)

    progressions = []
    for week in range(len(weekly_sets)):
        load, load_note = load_progression[week]
        rir = rir_progression[week]

        # Build weekly notes
        is_deload = (week == len(weekly_sets) - 1)
        if is_deload:
            notes = "DELOAD WEEK: Easy sets, focus on recovery"
        elif rir == 0:
            notes = "PEAK WEEK: Take sets to failure (0 RIR)"
        elif rir == 1:
            notes = "Hard sets, 1 rep shy of failure"
        elif rir == 2:
            notes = "Moderate intensity, 2 reps in reserve"
        else:
            notes = "Conservative, 3 reps in reserve"

        progressions.append(WeeklyProgression(
            week=week + 1,
            sets=weekly_sets[week],
            reps_scheme=rep_scheme,
            rir=rir,
            load_change=load_note,
            notes=notes
        ))

    return progressions


@dataclass
class ExerciseProgram:
    """Complete exercise program for a mesocycle"""
    exercise: Exercise
    progressions: List[WeeklyProgression]


def format_exercise_progression(program: ExerciseProgram) -> str:
    """Format exercise progression for display"""
    output = []

    output.append(f"## {program.exercise.display_name}")
    output.append(f"**Tier:** {program.exercise.tier.value}")
    output.append(f"**Target Muscle:** {program.exercise.primary_muscles[0].value.capitalize()}")

    output.append(f"\n**Weekly Progression:**")
    for prog in program.progressions:
        is_deload = "DELOAD" in prog.notes
        marker = "🔄" if is_deload else f"Week {prog.week}"
        output.append(f"\n**{marker}:** {prog.sets} sets × {prog.reps_scheme.display} @ {prog.rir} RIR")
        output.append(f"  Load: {prog.load_change}")
        output.append(f"  💡 {prog.notes}")

    return "\n".join(output)


def calculate_progression_rate(
    starting_load: float,
    ending_load: float,
    weeks: int
) -> Dict[str, float]:
    """
    Calculate progression metrics over mesocycle.

    Args:
        starting_load: Starting weight
        ending_load: Ending weight (peak week, before deload)
        weeks: Number of weeks

    Returns:
        Dictionary with progression stats
    """
    total_gain = ending_load - starting_load
    percentage_gain = (total_gain / starting_load) * 100
    weekly_average = total_gain / weeks

    return {
        "total_gain_lbs": total_gain,
        "percentage_gain": percentage_gain,
        "weekly_average_lbs": weekly_average,
        "starting_load": starting_load,
        "peak_load": ending_load
    }


if __name__ == "__main__":
    # Example usage and testing
    print("=== Progressive Overload System Test ===\n")

    # Test 1: RIR progression
    print("RIR PROGRESSION (5-week mesocycle + deload):")
    print("=" * 60)
    rir_progression = calculate_rir_progression(weeks=5)
    for week, rir in enumerate(rir_progression, 1):
        label = "DELOAD" if week == len(rir_progression) else f"Week {week}"
        intensity = ["Easy", "Moderate", "Moderate", "Hard", "Max Effort"][min(3-rir, 4)]
        print(f"{label:12} | {rir} RIR | {intensity}")
    print()

    # Test 2: Load progression
    print("\nLOAD PROGRESSION (Barbell Bench Press, 185 lbs starting):")
    print("=" * 60)
    loads = calculate_load_progression(rir_progression, starting_load=185, exercise_type="compound")
    for week, (load, note) in enumerate(loads, 1):
        label = "DELOAD" if week == len(loads) else f"Week {week}"
        print(f"{label:12} | {load:.1f} lbs | {note}")
    print()

    # Test 3: Complete exercise progression
    print("\nCOMPLETE EXERCISE PROGRESSION:")
    print("=" * 60)

    # Import exercise (create a sample one for testing)
    from exercise_database import Exercise, ExerciseTier, MuscleGroup

    bench_press = Exercise(
        name="barbell_bench_press",
        display_name="Barbell Bench Press",
        tier=ExerciseTier.S,
        primary_muscles=[MuscleGroup.CHEST],
        secondary_muscles=[MuscleGroup.TRICEPS, MuscleGroup.SHOULDERS],
        equipment_required=["barbell", "bench", "rack"],
        difficulty="intermediate",
        notes="King of chest exercises. Compound movement."
    )

    # Weekly sets progression (from volume prescription)
    weekly_sets = [4, 4, 5, 5, 5, 2]  # Including deload

    program = ExerciseProgram(
        exercise=bench_press,
        progressions=build_exercise_progression(bench_press, weekly_sets, weeks=5)
    )

    print(format_exercise_progression(program))

    # Test 4: Progression metrics
    print("\n\nPROGRESSION METRICS:")
    print("=" * 60)
    metrics = calculate_progression_rate(
        starting_load=185,
        ending_load=200,
        weeks=5
    )
    print(f"Starting load: {metrics['starting_load']} lbs")
    print(f"Peak load: {metrics['peak_load']} lbs")
    print(f"Total gain: {metrics['total_gain_lbs']} lbs ({metrics['percentage_gain']:.1f}%)")
    print(f"Average weekly gain: {metrics['weekly_average_lbs']:.1f} lbs/week")

    # Test 5: Isolation exercise example
    print("\n\n" + "=" * 60)
    print("ISOLATION EXERCISE PROGRESSION (Cable Lateral Raise):")
    print("=" * 60)

    cable_lateral = Exercise(
        name="cable_lateral_raise",
        display_name="Cable Lateral Raise",
        tier=ExerciseTier.S_PLUS,
        primary_muscles=[MuscleGroup.SHOULDERS],
        secondary_muscles=[],
        equipment_required=["cables"],
        difficulty="beginner",
        notes="Superior to dumbbell lateral raises for constant tension. Isolation exercise."
    )

    weekly_sets_isolation = [3, 3, 4, 4, 4, 2]

    isolation_program = ExerciseProgram(
        exercise=cable_lateral,
        progressions=build_exercise_progression(cable_lateral, weekly_sets_isolation, weeks=5)
    )

    print(format_exercise_progression(isolation_program))
