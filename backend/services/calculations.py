"""
Nutrition & TDEE Calculations for HealthRAG

Provides evidence-based TDEE and macro calculations with coaching-style guidance.
All recommendations grounded in Renaissance Periodization and Jeff Nippard research.
"""

from typing import Dict, Tuple
from dataclasses import dataclass


# Activity level multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,           # Little to no exercise
    'lightly_active': 1.375,    # Light exercise 1-3 days/week
    'moderately_active': 1.55,  # Moderate exercise 3-5 days/week
    'very_active': 1.725,       # Hard exercise 6-7 days/week
    'extremely_active': 1.9     # Physical job + hard exercise daily
}

# Phase adjustments (calories to add/subtract from maintenance)
PHASE_ADJUSTMENTS = {
    'cut': -500,        # 500 cal deficit = ~1 lb/week loss
    'bulk': 400,        # 300-500 cal surplus = ~0.75 lb/week gain
    'maintain': 0,      # Maintenance calories
    'recomp': 0         # Maintenance calories (recomp at maintenance)
}


def calculate_bmr(weight_lbs: float, height_inches: int, age: int, sex: str) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.

    This is the most accurate formula for predicting resting metabolic rate.

    Args:
        weight_lbs: Body weight in pounds
        height_inches: Height in inches
        age: Age in years
        sex: 'male' or 'female'

    Returns:
        BMR in calories/day

    References:
        Mifflin-St Jeor equation (1990) - gold standard for BMR prediction
    """
    # Convert to metric
    weight_kg = weight_lbs * 0.453592
    height_cm = height_inches * 2.54

    # Mifflin-St Jeor formula
    if sex.lower() == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure.

    TDEE = BMR × activity multiplier

    Args:
        bmr: Basal Metabolic Rate in calories/day
        activity_level: One of ACTIVITY_MULTIPLIERS keys

    Returns:
        TDEE in calories/day (maintenance calories)

    References:
        Harris-Benedict equation for activity multipliers
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    tdee = bmr * multiplier
    return round(tdee, 0)


def apply_phase_adjustment(tdee: float, phase: str) -> float:
    """
    Apply phase-specific calorie adjustment to TDEE.

    - Cut: -500 cal (1 lb/week fat loss)
    - Bulk: +400 cal (0.75 lb/week muscle gain)
    - Maintain: 0 (maintain weight)
    - Recomp: 0 (maintain weight while building muscle/losing fat)

    Args:
        tdee: Maintenance TDEE in calories/day
        phase: One of 'cut', 'bulk', 'maintain', 'recomp'

    Returns:
        Phase-adjusted calories/day

    References:
        RP Diet 2.0 (deficit/surplus recommendations)
        Jeff Nippard Fundamentals (lean bulk guidelines)
    """
    adjustment = PHASE_ADJUSTMENTS.get(phase, 0)
    adjusted = tdee + adjustment
    return round(adjusted, 0)


def calculate_macros(
    weight_lbs: float,
    calories: float,
    phase: str,
    sex: str = 'male'
) -> Dict[str, float]:
    """
    Calculate macro breakdown (protein, fat, carbs).

    Protein: 0.8-1.2g per lb bodyweight (higher for cuts)
    Fat: 0.3-0.5g per lb bodyweight (females slightly higher)
    Carbs: Remainder of calories

    Args:
        weight_lbs: Body weight in pounds
        calories: Target daily calories
        phase: 'cut', 'bulk', 'maintain', or 'recomp'
        sex: 'male' or 'female'

    Returns:
        Dict with protein_g, fat_g, carbs_g, and percentages

    References:
        RP Diet 2.0 (macro recommendations by phase)
        Jeff Nippard Fundamentals (protein/fat ranges)
    """
    # Protein: Higher for cuts/recomp to preserve muscle
    if phase == 'cut':
        protein_g = weight_lbs * 1.0  # 1.0g/lb for cuts
    elif phase == 'recomp':
        protein_g = weight_lbs * 1.1  # 1.1g/lb for recomp (higher to support muscle growth)
    else:  # bulk or maintain
        protein_g = weight_lbs * 0.9  # 0.9g/lb for bulk/maintain

    protein_g = round(protein_g, 0)
    protein_cal = protein_g * 4  # 4 cal/g protein

    # Fat: Females need slightly more for hormone production
    if sex.lower() == 'female':
        fat_g = weight_lbs * 0.4  # 0.4g/lb for females
    else:  # male
        fat_g = weight_lbs * 0.35  # 0.35g/lb for males

    fat_g = round(fat_g, 0)
    fat_cal = fat_g * 9  # 9 cal/g fat

    # Carbs: Remainder of calories
    carbs_cal = calories - protein_cal - fat_cal
    carbs_g = round(carbs_cal / 4, 0)  # 4 cal/g carbs

    # Calculate percentages
    protein_pct = round((protein_cal / calories) * 100, 0)
    fat_pct = round((fat_cal / calories) * 100, 0)
    carbs_pct = round((carbs_cal / calories) * 100, 0)

    return {
        'protein_g': protein_g,
        'fat_g': fat_g,
        'carbs_g': carbs_g,
        'protein_pct': protein_pct,
        'fat_pct': fat_pct,
        'carbs_pct': carbs_pct,
        'protein_cal': protein_cal,
        'fat_cal': fat_cal,
        'carbs_cal': carbs_cal
    }


def generate_nutrition_guidance(
    personal_info: Dict,
    goals: Dict,
    bmr: float,
    tdee_maintenance: float,
    tdee_adjusted: float,
    macros: Dict[str, float]
) -> str:
    """
    Generate coaching-style nutrition guidance.

    NOT just numbers - provides context, expectations, and promises adaptation.

    Args:
        personal_info: Dict with weight_lbs, height_inches, age, sex, activity_level
        goals: Dict with phase, target_weight_lbs, timeline_weeks
        bmr: Calculated BMR
        tdee_maintenance: Maintenance TDEE
        tdee_adjusted: Phase-adjusted TDEE
        macros: Macro breakdown dict

    Returns:
        Coaching-style guidance string with context and citations
    """
    weight = personal_info['weight_lbs']
    height_inches = personal_info['height_inches']
    height_feet = height_inches // 12
    height_remaining_inches = height_inches % 12
    age = personal_info['age']
    sex = personal_info['sex']
    activity = personal_info['activity_level']
    phase = goals['phase']

    # Build coaching response
    response = f"""Based on your profile ({int(weight)} lbs, {height_feet}'{height_remaining_inches}\", {age}, {sex}, {activity.replace('_', ' ')}), here's your nutrition plan:

**Maintenance TDEE:** ~{int(tdee_maintenance):,} calories/day
(BMR: ~{int(bmr):,} cal × {activity.replace('_', ' ')} multiplier {ACTIVITY_MULTIPLIERS[activity]})
"""

    # Phase-specific guidance
    if phase == 'cut':
        deficit = abs(PHASE_ADJUSTMENTS['cut'])
        expected_rate = abs(deficit / 3500)  # 3500 cal = 1 lb fat

        response += f"""
**Cutting Target:** ~{int(tdee_adjusted):,} calories/day (-{deficit} cal deficit, ~{expected_rate:.1f} lb/week loss)

**Macro Breakdown:**
- Protein: {int(macros['protein_g'])}g ({int(macros['protein_cal'])} cal) - {int(macros['protein_pct'])}%
  → Renaissance Periodization recommends 1.0-1.2g/lb during cuts to preserve muscle
- Fat: {int(macros['fat_g'])}g ({int(macros['fat_cal'])} cal) - {int(macros['fat_pct'])}%
  → 0.3-0.4g/lb supports hormone production{'(females need slightly more)' if sex == 'female' else ''}
- Carbs: {int(macros['carbs_g'])}g ({int(macros['carbs_cal'])} cal) - {int(macros['carbs_pct'])}%
  → Remaining calories fuel your training

**What to Expect:**
You should lose ~{expected_rate:.1f} lb/week at this intake. We'll adjust based on your weekly weigh-ins.
- If progress too slow after 2 weeks, we'll reduce by 100-200 cal
- If too fast (>1.5 lb/week), we'll increase slightly to preserve muscle

**Source:** RP Diet 2.0 (Chapter 3), RP Diet Adjustments Manual (p. 12)
"""

    elif phase == 'bulk':
        surplus = PHASE_ADJUSTMENTS['bulk']
        expected_rate = surplus / 3500  # 3500 cal = 1 lb

        response += f"""
**Bulking Target:** ~{int(tdee_adjusted):,} calories/day (+{surplus} cal surplus, ~{expected_rate:.2f} lb/week gain)

**Macro Breakdown:**
- Protein: {int(macros['protein_g'])}g ({int(macros['protein_cal'])} cal) - {int(macros['protein_pct'])}%
  → 0.8-1.0g/lb is sufficient during bulk (more calories = less protein % needed)
- Fat: {int(macros['fat_g'])}g ({int(macros['fat_cal'])} cal) - {int(macros['fat_pct'])}%
  → Supports hormone production and energy
- Carbs: {int(macros['carbs_g'])}g ({int(macros['carbs_cal'])} cal) - {int(macros['carbs_pct'])}%
  → High carbs fuel intense training and muscle growth

**What to Expect:**
You should gain ~{expected_rate:.2f} lb/week (lean bulk = minimal fat gain). We'll adjust based on weekly weigh-ins and waist measurements.
- If gaining too slow (<0.5 lb/week for 2 weeks), we'll increase by 150-200 cal
- If gaining too fast (>1.0 lb/week), we'll reduce to minimize fat gain

**Source:** Jeff Nippard Fundamentals (Lean Bulk Guidelines), RP Hypertrophy Training Principles
"""

    elif phase == 'recomp':
        response += f"""
**Body Recomposition Target:** ~{int(tdee_adjusted):,} calories/day (maintenance)

**Why Maintenance Calories?**
Recomp requires eating at EXACTLY maintenance - no deficit (prioritizes fat loss over muscle gain) and no surplus (adds fat faster than muscle).

**Macro Breakdown:**
- Protein: {int(macros['protein_g'])}g ({int(macros['protein_cal'])} cal) - {int(macros['protein_pct'])}%
  → **HIGHER than bulk/cut:** 1.0-1.2g/lb (recomp needs max protein for muscle growth without surplus)
- Fat: {int(macros['fat_g'])}g ({int(macros['fat_cal'])} cal) - {int(macros['fat_pct'])}%
  → Supports hormone production
- Carbs: {int(macros['carbs_g'])}g ({int(macros['carbs_cal'])} cal) - {int(macros['carbs_pct'])}%
  → High carbs fuel the HIGH VOLUME training required for recomp

**What to Expect:**
Your scale weight should stay ±2 lbs of {int(weight)} lbs. Track progress via:
- Waist measurement (should DECREASE)
- Chest measurement (should INCREASE)
- Strength progression (PROOF of muscle gain)
- Progress photos (visual changes > scale)

Timeline: 6-12 months for noticeable recomp. Patience required!

**Strict Adherence Critical:**
- ±50 cal tolerance (not ±200 like bulk/cut)
- Track daily, weigh food initially
- Recomp is unforgiving - small errors stall progress

We'll adjust if:
- Weight increases >2 lbs over 2 weeks → -100-150 cal
- Weight decreases >2 lbs over 2 weeks → +100-150 cal
- Strength plateau >3 weeks → Increase training volume

**Source:** RP Diet 2.0 (Recomposition chapter), Jeff Nippard "Can You Build Muscle and Lose Fat?"
"""

    else:  # maintain
        response += f"""
**Maintenance Target:** ~{int(tdee_adjusted):,} calories/day

**Macro Breakdown:**
- Protein: {int(macros['protein_g'])}g ({int(macros['protein_cal'])} cal) - {int(macros['protein_pct'])}%
- Fat: {int(macros['fat_g'])}g ({int(macros['fat_cal'])} cal) - {int(macros['fat_pct'])}%
- Carbs: {int(macros['carbs_g'])}g ({int(macros['carbs_cal'])} cal) - {int(macros['carbs_pct'])}%

**What to Expect:**
Your weight should stay ±2-3 lbs of {int(weight)} lbs. Maintenance allows for flexibility:
- Enjoy cheat meals occasionally
- Travel without stress
- Focus on consistency over intensity

We'll adjust if weight drifts >5 lbs over 4 weeks.

**Source:** RP Diet 2.0 (Maintenance Nutrition)
"""

    response += "\nReady to start tracking your progress?"

    return response.strip()


def calculate_nutrition_plan(personal_info: Dict, goals: Dict) -> Dict:
    """
    Calculate complete nutrition plan with coaching guidance.

    One-stop function that calculates BMR, TDEE, macros, and generates guidance.

    Args:
        personal_info: Dict with weight_lbs, height_inches, age, sex, activity_level
        goals: Dict with phase (cut/bulk/maintain/recomp)

    Returns:
        Dict with:
            - bmr: Basal Metabolic Rate
            - tdee_maintenance: Maintenance TDEE
            - tdee_adjusted: Phase-adjusted TDEE
            - macros: Protein/fat/carbs breakdown
            - guidance: Coaching-style text guidance
    """
    # Extract required fields
    weight = personal_info['weight_lbs']
    height = personal_info['height_inches']
    age = personal_info['age']
    sex = personal_info['sex']
    activity = personal_info['activity_level']
    phase = goals.get('phase', 'maintain')

    # Calculate BMR and TDEE
    bmr = calculate_bmr(weight, height, age, sex)
    tdee_maintenance = calculate_tdee(bmr, activity)
    tdee_adjusted = apply_phase_adjustment(tdee_maintenance, phase)

    # Calculate macros
    macros = calculate_macros(weight, tdee_adjusted, phase, sex)

    # Generate coaching guidance
    guidance = generate_nutrition_guidance(
        personal_info, goals, bmr, tdee_maintenance, tdee_adjusted, macros
    )

    return {
        'bmr': bmr,
        'tdee_maintenance': tdee_maintenance,
        'tdee_adjusted': tdee_adjusted,
        'macros': macros,
        'guidance': guidance
    }


def get_expected_rate_text(phase: str) -> str:
    """
    Get expected progress rate text for dashboard display.

    Args:
        phase: User's current phase ('cut', 'bulk', 'maintain', 'recomp')

    Returns:
        Human-readable text like "~1.0 lb/week loss"
    """
    if phase == 'cut':
        return "~1.0 lb/week loss"
    elif phase == 'bulk':
        return "~0.75 lb/week gain"
    elif phase == 'recomp':
        return "Maintain weight (±2 lbs)"
    else:  # maintain
        return "Maintain current weight"


def get_phase_explanation(personal_info: Dict, goals: Dict) -> str:
    """
    Generate brief explanation of why these nutrition numbers.

    Args:
        personal_info: Dict with weight_lbs, height_inches, age, sex, activity_level
        goals: Dict with phase, target_weight_lbs, timeline_weeks

    Returns:
        Brief coaching explanation text
    """
    weight = personal_info['weight_lbs']
    sex = personal_info['sex']
    phase = goals['phase']

    if phase == 'cut':
        return (f"As a {int(weight)} lb {sex} cutting, you need high protein (1.0g/lb) to preserve "
                f"muscle during your deficit. We'll adjust based on weekly weigh-ins.")
    elif phase == 'bulk':
        return (f"With a lean bulk approach, you'll gain ~0.75 lb/week with minimal fat gain. "
                f"High carbs fuel intense training for muscle growth.")
    elif phase == 'recomp':
        return (f"Body recomposition requires eating at EXACTLY maintenance - no deficit, no surplus. "
                f"High protein (1.1g/lb) supports muscle growth despite no calorie surplus.")
    else:  # maintain
        return (f"Maintenance calories keep your weight stable at {int(weight)} lbs. "
                f"Enjoy more flexibility - focus on consistency over perfection.")
