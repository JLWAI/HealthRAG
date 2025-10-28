"""
Tests for TDEE and macro calculations.

Tests all calculation functions against 5 user personas to ensure
accuracy across diverse profiles (male/female, different phases, activity levels).
"""

import pytest
from src.calculations import (
    calculate_bmr,
    calculate_tdee,
    apply_phase_adjustment,
    calculate_macros,
    calculate_nutrition_plan,
    ACTIVITY_MULTIPLIERS,
    PHASE_ADJUSTMENTS
)
from tests.fixtures import (
    BEGINNER_BEN,
    INTERMEDIATE_IAN,
    CUTTING_CLAIRE,
    RECOMP_RYAN,
    MINIMAL_MEGAN
)


class TestBMRCalculation:
    """Test BMR calculation using Mifflin-St Jeor formula"""

    def test_bmr_male(self):
        """Test BMR for male (Beginner Ben)"""
        personal_info = BEGINNER_BEN['personal_info']
        bmr = calculate_bmr(
            personal_info['weight_lbs'],
            personal_info['height_inches'],
            personal_info['age'],
            personal_info['sex']
        )

        # Check within expected range
        expected_min, expected_max = BEGINNER_BEN['expected']['bmr_range']
        assert expected_min <= bmr <= expected_max, \
            f"BMR {bmr} not in expected range {expected_min}-{expected_max}"

    def test_bmr_female(self):
        """Test BMR for female (Cutting Claire)"""
        personal_info = CUTTING_CLAIRE['personal_info']
        bmr = calculate_bmr(
            personal_info['weight_lbs'],
            personal_info['height_inches'],
            personal_info['age'],
            personal_info['sex']
        )

        # Check within expected range
        expected_min, expected_max = CUTTING_CLAIRE['expected']['bmr_range']
        assert expected_min <= bmr <= expected_max, \
            f"BMR {bmr} not in expected range {expected_min}-{expected_max}"

    def test_bmr_different_ages(self):
        """Test that BMR decreases with age"""
        # Same person, different ages
        bmr_young = calculate_bmr(185, 72, 25, 'male')
        bmr_older = calculate_bmr(185, 72, 50, 'male')

        assert bmr_young > bmr_older, "BMR should decrease with age"

    def test_bmr_male_vs_female(self):
        """Test that males have higher BMR than females (same stats)"""
        bmr_male = calculate_bmr(150, 66, 30, 'male')
        bmr_female = calculate_bmr(150, 66, 30, 'female')

        assert bmr_male > bmr_female, "Males should have higher BMR than females"


class TestTDEECalculation:
    """Test TDEE calculation with activity multipliers"""

    def test_tdee_sedentary(self):
        """Test TDEE for sedentary user (Beginner Ben)"""
        personal_info = BEGINNER_BEN['personal_info']
        bmr = calculate_bmr(
            personal_info['weight_lbs'],
            personal_info['height_inches'],
            personal_info['age'],
            personal_info['sex']
        )
        tdee = calculate_tdee(bmr, personal_info['activity_level'])

        # Check within expected range
        expected_min, expected_max = BEGINNER_BEN['expected']['tdee_maintenance']
        assert expected_min <= tdee <= expected_max, \
            f"TDEE {tdee} not in expected range {expected_min}-{expected_max}"

    def test_tdee_very_active(self):
        """Test TDEE for very active user (Cutting Claire)"""
        personal_info = CUTTING_CLAIRE['personal_info']
        bmr = calculate_bmr(
            personal_info['weight_lbs'],
            personal_info['height_inches'],
            personal_info['age'],
            personal_info['sex']
        )
        tdee = calculate_tdee(bmr, personal_info['activity_level'])

        # Check within expected range
        expected_min, expected_max = CUTTING_CLAIRE['expected']['tdee_maintenance']
        assert expected_min <= tdee <= expected_max, \
            f"TDEE {tdee} not in expected range {expected_min}-{expected_max}"

    def test_activity_multipliers(self):
        """Test that higher activity = higher TDEE"""
        bmr = 2000

        tdee_sedentary = calculate_tdee(bmr, 'sedentary')
        tdee_moderate = calculate_tdee(bmr, 'moderately_active')
        tdee_very = calculate_tdee(bmr, 'very_active')

        assert tdee_sedentary < tdee_moderate < tdee_very, \
            "TDEE should increase with activity level"


class TestPhaseAdjustments:
    """Test phase-specific calorie adjustments"""

    def test_cutting_deficit(self):
        """Test cutting phase creates deficit"""
        tdee_maintenance = 2500
        tdee_cut = apply_phase_adjustment(tdee_maintenance, 'cut')

        assert tdee_cut == tdee_maintenance + PHASE_ADJUSTMENTS['cut'], \
            f"Cut should be {PHASE_ADJUSTMENTS['cut']} cal deficit"

    def test_bulking_surplus(self):
        """Test bulking phase creates surplus"""
        tdee_maintenance = 2500
        tdee_bulk = apply_phase_adjustment(tdee_maintenance, 'bulk')

        assert tdee_bulk == tdee_maintenance + PHASE_ADJUSTMENTS['bulk'], \
            f"Bulk should be {PHASE_ADJUSTMENTS['bulk']} cal surplus"

    def test_recomp_maintenance(self):
        """Test recomp stays at maintenance"""
        tdee_maintenance = 2500
        tdee_recomp = apply_phase_adjustment(tdee_maintenance, 'recomp')

        assert tdee_recomp == tdee_maintenance, \
            "Recomp should stay at maintenance calories"

    def test_maintain_no_adjustment(self):
        """Test maintain phase has no adjustment"""
        tdee_maintenance = 2500
        tdee_maintain = apply_phase_adjustment(tdee_maintenance, 'maintain')

        assert tdee_maintain == tdee_maintenance, \
            "Maintain should have no calorie adjustment"


class TestMacroCalculations:
    """Test macro calculations (protein, fat, carbs)"""

    def test_macros_cutting_male(self):
        """Test macros for male cutting (Beginner Ben)"""
        personal_info = BEGINNER_BEN['personal_info']
        expected = BEGINNER_BEN['expected']

        # Get cutting calories
        bmr = calculate_bmr(
            personal_info['weight_lbs'],
            personal_info['height_inches'],
            personal_info['age'],
            personal_info['sex']
        )
        tdee_maintenance = calculate_tdee(bmr, personal_info['activity_level'])
        calories_cut = apply_phase_adjustment(tdee_maintenance, 'cut')

        # Calculate macros
        macros = calculate_macros(
            personal_info['weight_lbs'],
            calories_cut,
            'cut',
            personal_info['sex']
        )

        # Check protein in expected range (0.9-1.1g per lb)
        expected_protein_min, expected_protein_max = expected['protein_g_range']
        assert expected_protein_min <= macros['protein_g'] <= expected_protein_max, \
            f"Protein {macros['protein_g']}g not in expected range {expected_protein_min}-{expected_protein_max}g"

        # Check fat in expected range (0.3-0.4g per lb for males)
        expected_fat_min, expected_fat_max = expected['fat_g_range']
        assert expected_fat_min <= macros['fat_g'] <= expected_fat_max, \
            f"Fat {macros['fat_g']}g not in expected range {expected_fat_min}-{expected_fat_max}g"

        # Check macros sum to calories (within 10 cal tolerance)
        total_cal = (macros['protein_g'] * 4) + (macros['fat_g'] * 9) + (macros['carbs_g'] * 4)
        assert abs(total_cal - calories_cut) <= 10, \
            f"Macro calories {total_cal} should match target {calories_cut}"

    def test_macros_cutting_female(self):
        """Test macros for female cutting (Cutting Claire) - higher fat"""
        personal_info = CUTTING_CLAIRE['personal_info']
        expected = CUTTING_CLAIRE['expected']

        # Get cutting calories
        bmr = calculate_bmr(
            personal_info['weight_lbs'],
            personal_info['height_inches'],
            personal_info['age'],
            personal_info['sex']
        )
        tdee_maintenance = calculate_tdee(bmr, personal_info['activity_level'])
        calories_cut = apply_phase_adjustment(tdee_maintenance, 'cut')

        # Calculate macros
        macros = calculate_macros(
            personal_info['weight_lbs'],
            calories_cut,
            'cut',
            personal_info['sex']
        )

        # Females should have slightly higher fat (0.35-0.45g per lb)
        weight = personal_info['weight_lbs']
        expected_fat_min = weight * 0.35
        expected_fat_max = weight * 0.45

        assert expected_fat_min <= macros['fat_g'] <= expected_fat_max, \
            f"Female fat {macros['fat_g']}g should be in range {expected_fat_min:.0f}-{expected_fat_max:.0f}g"

    def test_macros_recomp_high_protein(self):
        """Test recomp has higher protein (1.1g per lb) than bulk"""
        personal_info = RECOMP_RYAN['personal_info']
        weight = personal_info['weight_lbs']

        # Recomp macros
        macros_recomp = calculate_macros(weight, 2700, 'recomp', 'male')

        # Bulk macros
        macros_bulk = calculate_macros(weight, 2700, 'bulk', 'male')

        # Recomp should have MORE protein than bulk
        assert macros_recomp['protein_g'] > macros_bulk['protein_g'], \
            "Recomp should have higher protein than bulk to support muscle growth at maintenance"


class TestNutritionPlan:
    """Test complete nutrition plan generation"""

    def test_beginner_ben_cutting(self):
        """Test complete nutrition plan for Beginner Ben (cutting)"""
        personal_info = BEGINNER_BEN['personal_info']
        goals = BEGINNER_BEN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)

        # Check all components present
        assert 'bmr' in plan
        assert 'tdee_maintenance' in plan
        assert 'tdee_adjusted' in plan
        assert 'macros' in plan
        assert 'guidance' in plan

        # Check TDEE in expected range
        expected_tdee_min, expected_tdee_max = BEGINNER_BEN['expected']['tdee_cutting']
        assert expected_tdee_min <= plan['tdee_adjusted'] <= expected_tdee_max

        # Check guidance is coaching-style (contains coaching keywords)
        guidance = plan['guidance']
        assert 'Based on your profile' in guidance, "Should be personalized"
        assert 'What to Expect:' in guidance, "Should set expectations"
        assert 'Source:' in guidance, "Should cite RP sources"
        assert 'RP Diet' in guidance or 'Renaissance Periodization' in guidance, \
            "Should cite RP Diet 2.0"

    def test_intermediate_ian_bulking(self):
        """Test complete nutrition plan for Intermediate Ian (bulking)"""
        personal_info = INTERMEDIATE_IAN['personal_info']
        goals = INTERMEDIATE_IAN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)

        # Check TDEE in expected range
        expected_tdee_min, expected_tdee_max = INTERMEDIATE_IAN['expected']['tdee_bulking']
        assert expected_tdee_min <= plan['tdee_adjusted'] <= expected_tdee_max

        # Check bulking guidance
        guidance = plan['guidance']
        assert 'surplus' in guidance.lower(), "Should mention surplus for bulk"
        assert 'gain' in guidance.lower(), "Should mention weight gain"

    def test_recomp_ryan_maintenance(self):
        """Test complete nutrition plan for Recomp Ryan (recomp)"""
        personal_info = RECOMP_RYAN['personal_info']
        goals = RECOMP_RYAN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)

        # Check TDEE is maintenance (no adjustment)
        expected_tdee_min, expected_tdee_max = RECOMP_RYAN['expected']['tdee_recomp']
        assert expected_tdee_min <= plan['tdee_adjusted'] <= expected_tdee_max

        # Recomp should get maintenance calories
        assert plan['tdee_maintenance'] == plan['tdee_adjusted'], \
            "Recomp should be at maintenance calories (no +/-)"

        # Check recomp-specific guidance
        guidance = plan['guidance']
        assert 'recomp' in guidance.lower(), "Should mention recomposition"
        assert 'waist' in guidance.lower(), "Should mention waist measurement"
        assert 'maintenance' in guidance.lower(), "Should mention maintenance calories"

    def test_minimal_megan_maintenance(self):
        """Test complete nutrition plan for Minimal Megan (maintenance)"""
        personal_info = MINIMAL_MEGAN['personal_info']
        goals = MINIMAL_MEGAN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)

        # Check TDEE in expected range
        expected_tdee_min, expected_tdee_max = MINIMAL_MEGAN['expected']['tdee_maintain']
        assert expected_tdee_min <= plan['tdee_adjusted'] <= expected_tdee_max


class TestEdgeCases:
    """Test edge cases and validation"""

    def test_very_tall_person(self):
        """Test calculations for very tall person (6'8")"""
        bmr = calculate_bmr(200, 80, 25, 'male')  # 6'8", 200 lbs
        assert bmr > 2000, "Very tall person should have high BMR"

    def test_very_short_person(self):
        """Test calculations for very short person (4'10")"""
        bmr = calculate_bmr(100, 58, 25, 'female')  # 4'10", 100 lbs
        assert bmr < 1400, "Very short person should have lower BMR"

    def test_macros_sum_to_calories(self):
        """Test that macros always sum to target calories"""
        test_cases = [
            (180, 2500, 'cut', 'male'),
            (150, 2000, 'bulk', 'female'),
            (165, 2700, 'recomp', 'male'),
            (128, 1800, 'maintain', 'female')
        ]

        for weight, calories, phase, sex in test_cases:
            macros = calculate_macros(weight, calories, phase, sex)

            # Calculate total calories from macros
            total_cal = (
                (macros['protein_g'] * 4) +
                (macros['fat_g'] * 9) +
                (macros['carbs_g'] * 4)
            )

            # Allow 10 cal tolerance for rounding
            assert abs(total_cal - calories) <= 10, \
                f"Macros should sum to target calories (phase={phase}, sex={sex})"


class TestCoachingGuidance:
    """Test that guidance follows coaching principles"""

    def test_guidance_is_personalized(self):
        """Test that guidance includes user-specific details"""
        personal_info = BEGINNER_BEN['personal_info']
        goals = BEGINNER_BEN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)
        guidance = plan['guidance']

        # Should include user's stats
        assert str(int(personal_info['weight_lbs'])) in guidance, "Should mention weight"
        assert str(personal_info['age']) in guidance, "Should mention age"

    def test_guidance_sets_expectations(self):
        """Test that guidance sets expectations"""
        personal_info = BEGINNER_BEN['personal_info']
        goals = BEGINNER_BEN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)
        guidance = plan['guidance']

        # Should set expectations
        assert 'expect' in guidance.lower() or 'should' in guidance.lower(), \
            "Should set expectations"

    def test_guidance_promises_adaptation(self):
        """Test that guidance promises to adapt"""
        personal_info = BEGINNER_BEN['personal_info']
        goals = BEGINNER_BEN['goals']

        plan = calculate_nutrition_plan(personal_info, goals)
        guidance = plan['guidance']

        # Should promise adaptation
        assert 'adjust' in guidance.lower() or 'we\'ll' in guidance.lower(), \
            "Should promise to adapt based on progress"

    def test_guidance_cites_sources(self):
        """Test that guidance cites RP sources"""
        all_personas = [
            (BEGINNER_BEN, 'cut'),
            (INTERMEDIATE_IAN, 'bulk'),
            (RECOMP_RYAN, 'recomp'),
            (MINIMAL_MEGAN, 'maintain')
        ]

        for persona, phase in all_personas:
            personal_info = persona['personal_info']
            goals = persona['goals']

            plan = calculate_nutrition_plan(personal_info, goals)
            guidance = plan['guidance']

            # Should cite RP or Jeff Nippard
            assert ('RP Diet' in guidance or
                    'Renaissance Periodization' in guidance or
                    'Jeff Nippard' in guidance), \
                f"Should cite RP/Nippard sources for {phase} phase"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
