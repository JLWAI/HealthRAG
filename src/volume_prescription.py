"""
Volume Prescription System for HealthRAG
Based on Renaissance Periodization's MEV/MAV/MRV methodology

MEV = Minimum Effective Volume (lowest sets per week to grow)
MAV = Maximum Adaptive Volume (optimal sets for growth)
MRV = Maximum Recoverable Volume (max sets before overtraining)

Reference: RP Hypertrophy Training Guide, Dr. Mike Israetel
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

from exercise_database import MuscleGroup


@dataclass
class VolumeLandmarks:
    """Volume landmarks for a muscle group"""
    mev: int  # Minimum Effective Volume (sets/week)
    mav: int  # Maximum Adaptive Volume (sets/week)
    mrv: int  # Maximum Recoverable Volume (sets/week)
    mv: int   # Maintenance Volume (sets/week)


# ============================================================================
# RP VOLUME LANDMARKS (sets per week per muscle group)
# ============================================================================
# Based on RP's research and training recommendations

VOLUME_LANDMARKS = {
    MuscleGroup.CHEST: VolumeLandmarks(mev=10, mav=16, mrv=22, mv=6),
    MuscleGroup.BACK: VolumeLandmarks(mev=12, mav=18, mrv=25, mv=8),
    MuscleGroup.SHOULDERS: VolumeLandmarks(mev=12, mav=18, mrv=26, mv=8),
    MuscleGroup.BICEPS: VolumeLandmarks(mev=8, mav=14, mrv=20, mv=6),
    MuscleGroup.TRICEPS: VolumeLandmarks(mev=8, mav=12, mrv=18, mv=6),
    MuscleGroup.QUADS: VolumeLandmarks(mev=12, mav=18, mrv=24, mv=8),
    MuscleGroup.HAMSTRINGS: VolumeLandmarks(mev=8, mav=12, mrv=18, mv=6),
    MuscleGroup.GLUTES: VolumeLandmarks(mev=8, mav=14, mrv=20, mv=6),
    MuscleGroup.CALVES: VolumeLandmarks(mev=8, mav=12, mrv=16, mv=6),
    MuscleGroup.ABS: VolumeLandmarks(mev=0, mav=12, mrv=25, mv=0),  # Abs can be trained 0-25 sets
}


class TrainingPhase(Enum):
    """Training phase for volume adjustment"""
    MAINTENANCE = "maintenance"
    ACCUMULATION = "accumulation"
    INTENSIFICATION = "intensification"
    DELOAD = "deload"


def get_volume_landmarks(muscle: MuscleGroup) -> VolumeLandmarks:
    """Get volume landmarks for a muscle group"""
    return VOLUME_LANDMARKS.get(muscle, VolumeLandmarks(mev=8, mav=14, mrv=20, mv=6))


def calculate_starting_volume(
    muscle: MuscleGroup,
    training_level: str,
    phase: TrainingPhase = TrainingPhase.ACCUMULATION
) -> int:
    """
    Calculate starting weekly volume for a muscle group.

    Args:
        muscle: Target muscle group
        training_level: 'beginner', 'intermediate', 'advanced'
        phase: Training phase (maintenance/accumulation/intensification/deload)

    Returns:
        Starting sets per week

    Logic:
    - Beginners: Start at MEV (conservative)
    - Intermediate: Start between MEV and MAV (moderate)
    - Advanced: Start near MAV (aggressive)
    - Maintenance: Use MV (maintain muscle)
    - Deload: 50% of normal volume
    """
    landmarks = get_volume_landmarks(muscle)

    # Maintenance phase
    if phase == TrainingPhase.MAINTENANCE:
        return landmarks.mv

    # Deload phase (50% reduction)
    if phase == TrainingPhase.DELOAD:
        return landmarks.mav // 2

    # Growth phases (accumulation/intensification)
    if training_level == "beginner":
        # Start conservative (at MEV)
        return landmarks.mev

    elif training_level == "intermediate":
        # Start moderate (midpoint between MEV and MAV)
        return (landmarks.mev + landmarks.mav) // 2

    else:  # advanced
        # Start aggressive (near MAV, leave room for progression)
        return landmarks.mav - 2


def calculate_weekly_progression(
    starting_volume: int,
    landmarks: VolumeLandmarks,
    weeks: int = 5,
    progression_rate: int = 2
) -> List[int]:
    """
    Calculate weekly volume progression for a mesocycle.

    Args:
        starting_volume: Starting sets per week
        landmarks: Volume landmarks for the muscle
        weeks: Number of accumulation weeks (default 5)
        progression_rate: Sets to add per week (default 2)

    Returns:
        List of weekly volumes

    Example:
    Week 1: 12 sets
    Week 2: 14 sets (+2)
    Week 3: 16 sets (+2)
    Week 4: 18 sets (+2)
    Week 5: 20 sets (+2)
    Week 6: 10 sets (deload = 50% of starting volume)
    """
    weekly_volumes = []

    for week in range(weeks):
        volume = starting_volume + (week * progression_rate)

        # Cap at MRV (don't exceed maximum recoverable volume)
        volume = min(volume, landmarks.mrv)

        weekly_volumes.append(volume)

    # Add deload week (50% of starting volume)
    deload_volume = starting_volume // 2
    weekly_volumes.append(deload_volume)

    return weekly_volumes


def distribute_volume_across_workouts(
    weekly_volume: int,
    workouts_per_week: int
) -> List[int]:
    """
    Distribute weekly volume across workout sessions.

    Args:
        weekly_volume: Total sets per week
        workouts_per_week: How many times muscle is trained per week

    Returns:
        List of sets per workout

    Example:
    - 16 sets/week, 2 workouts → [8, 8]
    - 17 sets/week, 2 workouts → [9, 8] (uneven distribution)
    - 18 sets/week, 3 workouts → [6, 6, 6]
    """
    base_sets = weekly_volume // workouts_per_week
    remainder = weekly_volume % workouts_per_week

    distribution = [base_sets] * workouts_per_week

    # Distribute remainder across first N workouts
    for i in range(remainder):
        distribution[i] += 1

    return distribution


def calculate_volume_per_exercise(
    total_sets_for_muscle: int,
    num_exercises: int
) -> List[int]:
    """
    Distribute sets across exercises for a muscle group.

    Args:
        total_sets_for_muscle: Total sets for the muscle in this workout
        num_exercises: Number of exercises for this muscle

    Returns:
        List of sets per exercise

    Logic:
    - First exercise gets most sets (primary compound)
    - Remaining exercises get equal distribution

    Example:
    - 8 sets, 2 exercises → [5, 3] (primary compound + accessory)
    - 6 sets, 3 exercises → [3, 2, 1] (weighted toward first exercise)
    """
    if num_exercises == 1:
        return [total_sets_for_muscle]

    # Primary exercise gets 60% of sets (rounded)
    primary_sets = int(total_sets_for_muscle * 0.6)
    remaining_sets = total_sets_for_muscle - primary_sets

    # Distribute remaining sets evenly
    base_sets = remaining_sets // (num_exercises - 1)
    remainder = remaining_sets % (num_exercises - 1)

    distribution = [primary_sets]
    for i in range(num_exercises - 1):
        sets = base_sets + (1 if i < remainder else 0)
        distribution.append(sets)

    return distribution


@dataclass
class MesocycleVolumeProgression:
    """Complete volume progression for a muscle group"""
    muscle: MuscleGroup
    landmarks: VolumeLandmarks
    starting_volume: int
    weekly_volumes: List[int]  # Including deload week
    peak_volume: int
    deload_volume: int


def build_mesocycle_progression(
    muscle: MuscleGroup,
    training_level: str,
    weeks: int = 5,
    progression_rate: int = 2
) -> MesocycleVolumeProgression:
    """
    Build complete mesocycle volume progression for a muscle.

    Args:
        muscle: Target muscle group
        training_level: 'beginner', 'intermediate', 'advanced'
        weeks: Accumulation weeks (before deload)
        progression_rate: Sets added per week

    Returns:
        Complete progression plan
    """
    landmarks = get_volume_landmarks(muscle)
    starting_volume = calculate_starting_volume(muscle, training_level)
    weekly_volumes = calculate_weekly_progression(
        starting_volume, landmarks, weeks, progression_rate
    )

    return MesocycleVolumeProgression(
        muscle=muscle,
        landmarks=landmarks,
        starting_volume=starting_volume,
        weekly_volumes=weekly_volumes,
        peak_volume=weekly_volumes[-2],  # Second to last (before deload)
        deload_volume=weekly_volumes[-1]
    )


def format_volume_progression(progression: MesocycleVolumeProgression) -> str:
    """Format volume progression for display"""
    output = []

    output.append(f"## {progression.muscle.value.upper()} Volume Progression")
    output.append(f"\n**Volume Landmarks:**")
    output.append(f"  MEV: {progression.landmarks.mev} sets/week (minimum to grow)")
    output.append(f"  MAV: {progression.landmarks.mav} sets/week (optimal growth)")
    output.append(f"  MRV: {progression.landmarks.mrv} sets/week (maximum before overtraining)")
    output.append(f"  MV: {progression.landmarks.mv} sets/week (maintenance)")

    output.append(f"\n**Weekly Progression:**")
    for week, volume in enumerate(progression.weekly_volumes[:-1], 1):
        percentage = (volume / progression.landmarks.mav) * 100
        output.append(f"  Week {week}: {volume} sets ({percentage:.0f}% of MAV)")

    # Deload
    deload_week = len(progression.weekly_volumes)
    output.append(f"  Week {deload_week} (DELOAD): {progression.deload_volume} sets (50% reduction)")

    output.append(f"\n**Peak Volume:** {progression.peak_volume} sets (Week {len(progression.weekly_volumes) - 1})")

    return "\n".join(output)


if __name__ == "__main__":
    # Example usage and testing
    print("=== Volume Prescription System Test ===\n")

    # Test 1: Volume landmarks
    print("VOLUME LANDMARKS (sets per week):")
    print("=" * 60)
    for muscle in [MuscleGroup.CHEST, MuscleGroup.BACK, MuscleGroup.QUADS]:
        landmarks = get_volume_landmarks(muscle)
        print(f"{muscle.value.upper():12} | MEV: {landmarks.mev:2} | MAV: {landmarks.mav:2} | MRV: {landmarks.mrv:2}")
    print()

    # Test 2: Starting volumes by training level
    print("STARTING VOLUMES (Chest, Accumulation Phase):")
    print("=" * 60)
    for level in ["beginner", "intermediate", "advanced"]:
        volume = calculate_starting_volume(MuscleGroup.CHEST, level)
        landmarks = get_volume_landmarks(MuscleGroup.CHEST)
        percentage = (volume / landmarks.mav) * 100
        print(f"{level.capitalize():12} | {volume} sets/week ({percentage:.0f}% of MAV)")
    print()

    # Test 3: 6-week mesocycle progression
    print("CHEST MESOCYCLE (Intermediate, 6 weeks):")
    print("=" * 60)
    progression = build_mesocycle_progression(
        MuscleGroup.CHEST,
        training_level="intermediate",
        weeks=5,
        progression_rate=2
    )
    print(format_volume_progression(progression))
    print()

    # Test 4: Volume distribution
    print("\nVOLUME DISTRIBUTION TEST:")
    print("=" * 60)
    print("16 sets/week, trained 2x per week:")
    distribution = distribute_volume_across_workouts(16, 2)
    print(f"  Workout A: {distribution[0]} sets")
    print(f"  Workout B: {distribution[1]} sets")

    print("\n18 sets/week, trained 3x per week (PPL):")
    distribution = distribute_volume_across_workouts(18, 3)
    for i, sets in enumerate(distribution, 1):
        print(f"  Workout {i}: {sets} sets")

    # Test 5: Sets per exercise
    print("\n\nSETS PER EXERCISE TEST:")
    print("=" * 60)
    print("8 sets for chest, 2 exercises (e.g., Bench Press + Cable Crossover):")
    exercise_sets = calculate_volume_per_exercise(8, 2)
    print(f"  Exercise 1 (Primary): {exercise_sets[0]} sets")
    print(f"  Exercise 2 (Accessory): {exercise_sets[1]} sets")

    print("\n6 sets for back, 3 exercises:")
    exercise_sets = calculate_volume_per_exercise(6, 3)
    for i, sets in enumerate(exercise_sets, 1):
        print(f"  Exercise {i}: {sets} sets")

    # Test 6: Complete back progression
    print("\n\n" + "=" * 60)
    print("BACK MESOCYCLE (Advanced, 5 weeks + deload):")
    print("=" * 60)
    progression = build_mesocycle_progression(
        MuscleGroup.BACK,
        training_level="advanced",
        weeks=5,
        progression_rate=2
    )
    print(format_volume_progression(progression))
