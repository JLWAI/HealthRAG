"""
Intelligent Exercise Alternative System for HealthRAG

Provides location-aware exercise alternatives based on:
1. Jeff Nippard's tier rankings (S+, S, A)
2. Jason's home gym equipment vs Planet Fitness
3. Maintains exercise quality in substitutions

KEY FEATURE: Shows multiple equivalent options per exercise with location awareness
Example: Hack Squat (S+)
  - Planet Fitness: Hack squat machine
  - Home: Landmine hack squat variation (using Viking Press)
  - Home: High bar barbell back squat (S-tier equivalent)
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from exercise_database import (
    Exercise, ExerciseTier, MuscleGroup,
    get_exercise_by_name, get_exercises_by_muscle
)


class Location(Enum):
    """Where an exercise can be performed"""
    HOME = "home"
    PLANET_FITNESS = "pf"
    BOTH = "both"


@dataclass
class ExerciseAlternative:
    """Alternative exercise with location and quality info"""
    exercise: Exercise
    location: Location
    equipment_notes: str  # Specific equipment needed
    quality_note: str  # Why this is a good alternative

    def format(self) -> str:
        """Format alternative for display"""
        location_icon = {
            Location.HOME: "🏠",
            Location.PLANET_FITNESS: "🏋️",
            Location.BOTH: "📍"
        }
        icon = location_icon.get(self.location, "")

        location_text = {
            Location.HOME: "Home",
            Location.PLANET_FITNESS: "Planet Fitness",
            Location.BOTH: "Home or Planet Fitness"
        }
        loc_name = location_text.get(self.location, "")

        return f"{icon} **{self.exercise.display_name}** [{self.exercise.tier.value}] - {loc_name}\n   {self.quality_note}\n   Equipment: {self.equipment_notes}"


@dataclass
class ExerciseWithAlternatives:
    """Primary exercise with location-aware alternatives"""
    primary: Exercise
    primary_location: Location
    alternatives: List[ExerciseAlternative]

    def format(self) -> str:
        """Format exercise with alternatives for display"""
        location_icon = {
            Location.HOME: "🏠",
            Location.PLANET_FITNESS: "🏋️",
            Location.BOTH: "📍"
        }

        output = []
        output.append(f"\n### {self.primary.display_name} [{self.primary.tier.value}]")
        output.append(f"{location_icon.get(self.primary_location, '')} Primary location: {self.primary_location.value.upper()}")

        if self.primary.notes:
            output.append(f"💡 {self.primary.notes}")

        if self.alternatives:
            output.append(f"\n**Alternatives ({len(self.alternatives)} options):**")
            for alt in self.alternatives:
                output.append(f"\n{alt.format()}")

        return "\n".join(output)


# ============================================================================
# JASON'S HOME GYM EQUIPMENT
# ============================================================================

JASONS_HOME_GYM = {
    'barbell',
    'j_hooks',
    'squat_rack',
    'dumbbells',
    'bench',
    'incline_bench',
    'decline_bench',
    'smith_machine',
    'smith_squat_rack',
    'smith_bench_press',
    'cables',
    'functional_trainer',
    'leg_extension_machine',
    'leg_curl_machine',
    'pull_up_bar',
    'lat_pulldown_machine',
    'cable_row_machine',
    'chest_press_machine',
    'landmine',  # Viking Press Landmine Handle
    'lateral_raise_machine',  # Mikolo attachment
    'rowing_machine',
    'treadmill',
    'elliptical',
    'bodyweight'
}


PLANET_FITNESS_EQUIPMENT = {
    'dumbbells',
    'smith_machine',
    'cables',
    'functional_trainer',
    'leg_extension_machine',
    'leg_curl_machine',
    'leg_press_machine',
    'hack_squat_machine',
    'chest_press_machine',
    'pec_deck',
    'shoulder_press_machine',
    'lateral_raise_machine',
    'bicep_curl_machine',
    'tricep_extension_machine',
    'lat_pulldown_machine',
    'seated_row_machine',
    'rear_delt_machine',
    'lower_back_extension',
    'ab_crunch_machine',
    'treadmill',
    'elliptical',
    'rowing_machine',
    'kettlebells',
    'battle_ropes',
    'trx',
    'medicine_balls',
    'bosu_balls',
    'bodyweight'
}


def get_exercise_location(exercise: Exercise,
                          home_equipment: Set[str] = None,
                          pf_equipment: Set[str] = None) -> Location:
    """
    Determine where an exercise can be performed.

    Args:
        exercise: Exercise to check
        home_equipment: Equipment available at home (default: Jason's)
        pf_equipment: Equipment available at PF (default: standard PF)

    Returns:
        Location enum indicating where exercise can be done
    """
    if home_equipment is None:
        home_equipment = JASONS_HOME_GYM
    if pf_equipment is None:
        pf_equipment = PLANET_FITNESS_EQUIPMENT

    # Check if exercise can be done with available equipment
    can_do_home = any(eq in home_equipment for eq in exercise.equipment_required)
    can_do_pf = any(eq in pf_equipment for eq in exercise.equipment_required)

    if can_do_home and can_do_pf:
        return Location.BOTH
    elif can_do_home:
        return Location.HOME
    elif can_do_pf:
        return Location.PLANET_FITNESS
    else:
        return None  # Can't do this exercise


def find_alternatives_by_location(
    exercise: Exercise,
    target_muscle: MuscleGroup,
    home_equipment: Set[str] = None,
    pf_equipment: Set[str] = None,
    max_alternatives: int = 5
) -> List[ExerciseAlternative]:
    """
    Find alternative exercises with location awareness.

    Prioritizes:
    1. Same tier exercises
    2. One tier down
    3. Maintains quality while providing location options

    Args:
        exercise: Original exercise to find alternatives for
        target_muscle: Muscle group to target
        home_equipment: Equipment at home
        pf_equipment: Equipment at PF
        max_alternatives: Maximum number of alternatives to return

    Returns:
        List of alternatives with location info
    """
    if home_equipment is None:
        home_equipment = JASONS_HOME_GYM
    if pf_equipment is None:
        pf_equipment = PLANET_FITNESS_EQUIPMENT

    alternatives = []

    # Get all exercises for this muscle
    same_tier = get_exercises_by_muscle(target_muscle, tier_filter=[exercise.tier])
    one_tier_down = ExerciseTier.S if exercise.tier == ExerciseTier.S_PLUS else ExerciseTier.A
    lower_tier = get_exercises_by_muscle(target_muscle, tier_filter=[one_tier_down])

    # Combine candidates (prioritize same tier)
    candidates = [ex for ex in same_tier if ex.name != exercise.name] + lower_tier

    for candidate in candidates:
        if len(alternatives) >= max_alternatives:
            break

        # Determine location
        location = get_exercise_location(candidate, home_equipment, pf_equipment)
        if location is None:
            continue

        # Determine equipment needed
        equipment_notes = _get_equipment_notes(candidate, location, home_equipment, pf_equipment)

        # Quality note
        quality_note = _get_quality_note(candidate, exercise)

        alternatives.append(ExerciseAlternative(
            exercise=candidate,
            location=location,
            equipment_notes=equipment_notes,
            quality_note=quality_note
        ))

    return alternatives


def _get_equipment_notes(exercise: Exercise,
                        location: Location,
                        home_equipment: Set[str],
                        pf_equipment: Set[str]) -> str:
    """Generate equipment notes for an exercise"""
    if location == Location.HOME:
        available = [eq for eq in exercise.equipment_required if eq in home_equipment]
    elif location == Location.PLANET_FITNESS:
        available = [eq for eq in exercise.equipment_required if eq in pf_equipment]
    else:  # BOTH
        available = exercise.equipment_required

    # Clean up equipment names
    equipment_map = {
        'dumbbells': 'Dumbbells',
        'barbell': 'Barbell',
        'smith_machine': 'Smith Machine',
        'cables': 'Cable Station',
        'functional_trainer': 'Functional Trainer',
        'landmine': 'Landmine (Viking Press)',
        'lateral_raise_machine': 'Lateral Raise Attachment',
        'hack_squat_machine': 'Hack Squat Machine',
        'leg_press_machine': 'Leg Press',
        'bench': 'Bench',
        'incline_bench': 'Incline Bench',
        'squat_rack': 'Squat Rack',
        'bodyweight': 'Bodyweight'
    }

    clean_names = [equipment_map.get(eq, eq.replace('_', ' ').title()) for eq in available]
    return ", ".join(clean_names)


def _get_quality_note(candidate: Exercise, original: Exercise) -> str:
    """Generate quality note explaining why this is a good alternative"""
    if candidate.tier == original.tier:
        return f"Same tier ({candidate.tier.value}) - Equivalent quality"
    elif candidate.tier == ExerciseTier.S and original.tier == ExerciseTier.S_PLUS:
        return "Excellent alternative (S-tier) - Minimal quality drop"
    elif candidate.tier == ExerciseTier.A and original.tier == ExerciseTier.S:
        return "Very good alternative (A-tier) - Solid substitute"
    else:
        return f"Alternative ({candidate.tier.value} tier)"


# ============================================================================
# INTELLIGENT EXERCISE MAPPINGS
# ============================================================================

def build_exercise_with_alternatives(
    exercise_name: str,
    home_equipment: Set[str] = None,
    pf_equipment: Set[str] = None
) -> Optional[ExerciseWithAlternatives]:
    """
    Build complete exercise info with location-aware alternatives.

    Args:
        exercise_name: Internal name of exercise
        home_equipment: Equipment at home
        pf_equipment: Equipment at PF

    Returns:
        ExerciseWithAlternatives or None if exercise not found
    """
    if home_equipment is None:
        home_equipment = JASONS_HOME_GYM
    if pf_equipment is None:
        pf_equipment = PLANET_FITNESS_EQUIPMENT

    exercise = get_exercise_by_name(exercise_name)
    if not exercise:
        return None

    # Determine primary location
    primary_location = get_exercise_location(exercise, home_equipment, pf_equipment)
    if primary_location is None:
        primary_location = Location.PLANET_FITNESS  # Default if not available

    # Find alternatives
    target_muscle = exercise.primary_muscles[0]
    alternatives = find_alternatives_by_location(
        exercise,
        target_muscle,
        home_equipment,
        pf_equipment,
        max_alternatives=5
    )

    return ExerciseWithAlternatives(
        primary=exercise,
        primary_location=primary_location,
        alternatives=alternatives
    )


def get_s_tier_exercises_with_alternatives(
    muscle_group: MuscleGroup,
    home_equipment: Set[str] = None,
    pf_equipment: Set[str] = None
) -> List[ExerciseWithAlternatives]:
    """
    Get all S+ and S tier exercises for a muscle with alternatives.

    Args:
        muscle_group: Target muscle
        home_equipment: Equipment at home
        pf_equipment: Equipment at PF

    Returns:
        List of exercises with alternatives, sorted by tier
    """
    if home_equipment is None:
        home_equipment = JASONS_HOME_GYM
    if pf_equipment is None:
        pf_equipment = PLANET_FITNESS_EQUIPMENT

    # Get S+ and S tier exercises
    s_plus = get_exercises_by_muscle(muscle_group, tier_filter=[ExerciseTier.S_PLUS])
    s_tier = get_exercises_by_muscle(muscle_group, tier_filter=[ExerciseTier.S])

    results = []

    for exercise in s_plus + s_tier:
        exercise_with_alts = build_exercise_with_alternatives(
            exercise.name,
            home_equipment,
            pf_equipment
        )
        if exercise_with_alts:
            results.append(exercise_with_alts)

    return results


def generate_exercise_guide(
    home_equipment: Set[str] = None,
    pf_equipment: Set[str] = None
) -> str:
    """
    Generate complete exercise guide with all S+/S tier exercises and alternatives.

    Args:
        home_equipment: Equipment at home
        pf_equipment: Equipment at PF

    Returns:
        Formatted markdown guide
    """
    if home_equipment is None:
        home_equipment = JASONS_HOME_GYM
    if pf_equipment is None:
        pf_equipment = PLANET_FITNESS_EQUIPMENT

    output = []
    output.append("# Exercise Guide: S+ and S Tier Exercises with Location-Aware Alternatives")
    output.append("\n**Key:**")
    output.append("- 🏠 = Home gym")
    output.append("- 🏋️ = Planet Fitness")
    output.append("- 📍 = Available at both locations")
    output.append("\n" + "=" * 80)

    # Process each major muscle group
    muscle_groups = [
        MuscleGroup.CHEST,
        MuscleGroup.BACK,
        MuscleGroup.SHOULDERS,
        MuscleGroup.BICEPS,
        MuscleGroup.TRICEPS,
        MuscleGroup.QUADS,
        MuscleGroup.GLUTES,
        MuscleGroup.HAMSTRINGS
    ]

    for muscle in muscle_groups:
        output.append(f"\n## {muscle.value.upper()}")
        output.append("-" * 80)

        exercises = get_s_tier_exercises_with_alternatives(
            muscle,
            home_equipment,
            pf_equipment
        )

        if not exercises:
            output.append(f"\nNo S+/S tier exercises found for {muscle.value}")
            continue

        for ex_with_alts in exercises:
            output.append(ex_with_alts.format())

    return "\n".join(output)


if __name__ == "__main__":
    # Test the alternative system
    print("=== Exercise Alternatives Test ===\n")

    # Test 1: Hack Squat alternatives (user's example)
    print("TEST 1: Hack Squat Alternatives")
    print("=" * 80)
    hack_squat = build_exercise_with_alternatives("hack_squat")
    if hack_squat:
        print(hack_squat.format())

    print("\n" + "=" * 80)

    # Test 2: Cable lateral raise (S+)
    print("\nTEST 2: Cable Lateral Raise (S+) Alternatives")
    print("=" * 80)
    cable_lat = build_exercise_with_alternatives("cable_lateral_raise")
    if cable_lat:
        print(cable_lat.format())

    print("\n" + "=" * 80)

    # Test 3: All chest exercises with alternatives
    print("\nTEST 3: All S+/S Tier Chest Exercises")
    print("=" * 80)
    chest_exercises = get_s_tier_exercises_with_alternatives(MuscleGroup.CHEST)
    for ex in chest_exercises:
        print(ex.format())

    print("\n" + "=" * 80)

    # Test 4: Generate complete guide for quads
    print("\nTEST 4: Complete Quad Exercise Guide")
    print("=" * 80)
    from exercise_database import MuscleGroup
    quad_guide = get_s_tier_exercises_with_alternatives(MuscleGroup.QUADS)
    for ex in quad_guide:
        print(ex.format())
