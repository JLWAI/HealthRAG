"""
Test fixtures for user personas used across HealthRAG testing.

These personas represent realistic users with different goals, experience levels,
equipment access, and schedules. Use these fixtures for consistent testing across
all development phases.

See SCENARIOS.md for detailed persona descriptions and use cases.
"""

# Equipment presets (from src/profile.py)
EQUIPMENT_PRESETS = {
    'minimal': ['bodyweight', 'resistance_bands', 'dumbbells'],
    'home_gym': ['bodyweight', 'dumbbells', 'bench', 'pull_up_bar', 'barbell', 'rack'],
    'commercial_gym': ['bodyweight', 'dumbbells', 'barbells', 'cables', 'machines',
                       'bench', 'squat_rack', 'pull_up_bar', 'dip_station', 'leg_press']
}


# PERSONA 1: "Beginner Ben" - The Newbie
BEGINNER_BEN = {
    'personal_info': {
        'weight_lbs': 210,
        'height_inches': 71,  # 5'11"
        'age': 26,
        'sex': 'male',
        'activity_level': 'sedentary'
    },
    'goals': {
        'phase': 'cut',
        'target_weight_lbs': 185,
        'timeline_weeks': 24,
        'primary_goal': 'fat_loss_and_learn_training'
    },
    'experience': {
        'training_level': 'beginner',
        'years_training': 0
    },
    'equipment': EQUIPMENT_PRESETS['home_gym'],
    'schedule': {
        'days_per_week': 3,
        'minutes_per_session': 45,
        'preferred_split': 'full_body'
    },
    # Expected calculations (for validation)
    'expected': {
        'bmr_range': (1930, 2000),  # Mifflin-St Jeor
        'tdee_maintenance': (2315, 2400),  # BMR × 1.2 (sedentary)
        'tdee_cutting': (1815, 1900),  # Maintenance - 500 cal
        'protein_g_range': (189, 231),  # 0.9-1.1g per lb
        'fat_g_range': (63, 84),  # 0.3-0.4g per lb
        'target_rate_lb_per_week': -1.0
    }
}


# PERSONA 2: "Intermediate Ian" - The Gym Regular
INTERMEDIATE_IAN = {
    'personal_info': {
        'weight_lbs': 185,
        'height_inches': 72,  # 6'0"
        'age': 32,
        'sex': 'male',
        'activity_level': 'moderately_active'
    },
    'goals': {
        'phase': 'bulk',
        'target_weight_lbs': 200,
        'timeline_weeks': 20,
        'primary_goal': 'hypertrophy'
    },
    'experience': {
        'training_level': 'intermediate',
        'years_training': 5
    },
    'equipment': EQUIPMENT_PRESETS['commercial_gym'],
    'schedule': {
        'days_per_week': 4,
        'minutes_per_session': 65,
        'preferred_split': 'upper_lower'
    },
    'expected': {
        'bmr_range': (1850, 1950),
        'tdee_maintenance': (2775, 2925),  # BMR × 1.5 (moderately active)
        'tdee_bulking': (3175, 3425),  # Maintenance + 400 cal
        'protein_g_range': (167, 204),  # 0.9-1.1g per lb
        'fat_g_range': (74, 93),  # 0.4-0.5g per lb
        'target_rate_lb_per_week': 0.75
    }
}


# PERSONA 3: "Cutting Claire" - The Female Lifter
CUTTING_CLAIRE = {
    'personal_info': {
        'weight_lbs': 145,
        'height_inches': 65,  # 5'5"
        'age': 28,
        'sex': 'female',
        'activity_level': 'very_active'
    },
    'goals': {
        'phase': 'cut',
        'target_weight_lbs': 135,
        'timeline_weeks': 16,
        'primary_goal': 'fat_loss_preserve_strength'
    },
    'experience': {
        'training_level': 'intermediate',
        'years_training': 3
    },
    'equipment': EQUIPMENT_PRESETS['commercial_gym'],
    'schedule': {
        'days_per_week': 5,
        'minutes_per_session': 60,
        'preferred_split': 'ppl'  # Push/Pull/Legs
    },
    'expected': {
        'bmr_range': (1350, 1450),
        'tdee_maintenance': (2295, 2465),  # BMR × 1.7 (very active)
        'tdee_cutting': (1795, 1965),  # Maintenance - 500 cal
        'protein_g_range': (131, 160),  # 0.9-1.1g per lb
        'fat_g_range': (51, 65),  # 0.35-0.45g per lb (female - higher fat)
        'target_rate_lb_per_week': -0.625
    }
}


# PERSONA 4: "Recomp Ryan" - The Lean Gainer
RECOMP_RYAN = {
    'personal_info': {
        'weight_lbs': 165,
        'height_inches': 70,  # 5'10"
        'age': 24,
        'sex': 'male',
        'activity_level': 'moderately_active'
    },
    'goals': {
        'phase': 'recomp',
        'target_weight_lbs': 165,  # Maintain weight
        'timeline_weeks': 12,
        'primary_goal': 'body_recomposition'
    },
    'experience': {
        'training_level': 'intermediate',
        'years_training': 2
    },
    'equipment': EQUIPMENT_PRESETS['home_gym'],
    'schedule': {
        'days_per_week': 4,
        'minutes_per_session': 75,
        'preferred_split': 'upper_lower'
    },
    'expected': {
        'bmr_range': (1750, 1850),
        'tdee_maintenance': (2625, 2775),  # BMR × 1.5 (moderately active)
        'tdee_recomp': (2625, 2775),  # Maintenance (no deficit/surplus)
        'protein_g_range': (149, 182),  # 0.9-1.1g per lb
        'fat_g_range': (66, 83),  # 0.4-0.5g per lb
        'target_rate_lb_per_week': 0.0  # Maintain weight
    }
}


# PERSONA 5: "Minimal Megan" - The Time-Crunched Professional
MINIMAL_MEGAN = {
    'personal_info': {
        'weight_lbs': 128,
        'height_inches': 64,  # 5'4"
        'age': 35,
        'sex': 'female',
        'activity_level': 'lightly_active'
    },
    'goals': {
        'phase': 'maintain',
        'target_weight_lbs': 128,
        'timeline_weeks': 52,  # Ongoing
        'primary_goal': 'general_fitness'
    },
    'experience': {
        'training_level': 'beginner',
        'years_training': 1
    },
    'equipment': EQUIPMENT_PRESETS['minimal'],
    'schedule': {
        'days_per_week': 2,
        'minutes_per_session': 35,
        'preferred_split': 'full_body'
    },
    'expected': {
        'bmr_range': (1200, 1300),
        'tdee_maintenance': (1640, 1760),  # BMR × 1.375 (lightly active)
        'tdee_maintain': (1640, 1760),  # Maintenance (same as above)
        'protein_g_range': (115, 141),  # 0.9-1.1g per lb
        'fat_g_range': (45, 58),  # 0.35-0.45g per lb (female)
        'target_rate_lb_per_week': 0.0  # Maintain weight
    }
}


# All personas collection for iteration
ALL_PERSONAS = {
    'beginner_ben': BEGINNER_BEN,
    'intermediate_ian': INTERMEDIATE_IAN,
    'cutting_claire': CUTTING_CLAIRE,
    'recomp_ryan': RECOMP_RYAN,
    'minimal_megan': MINIMAL_MEGAN
}


# Edge case personas for testing validation and error handling

# Edge Case 1: Unrealistic goal timeline
UNREALISTIC_GOAL = {
    'personal_info': {
        'weight_lbs': 220,
        'height_inches': 70,
        'age': 30,
        'sex': 'male',
        'activity_level': 'sedentary'
    },
    'goals': {
        'phase': 'cut',
        'target_weight_lbs': 170,  # 50 lbs loss
        'timeline_weeks': 8,  # 6.25 lb/week - UNREALISTIC!
        'primary_goal': 'rapid_fat_loss'
    },
    'expected_validation': {
        'error_type': 'unrealistic_timeline',
        'max_safe_rate_lb_per_week': 2.2,  # 1% bodyweight
        'recommended_timeline_weeks': 33  # 50 lbs at 1.5 lb/week
    }
}


# Edge Case 2: Conflicting goals
CONFLICTING_GOALS = {
    'personal_info': {
        'weight_lbs': 165,
        'height_inches': 70,
        'age': 24,
        'sex': 'male',
        'activity_level': 'moderately_active'
    },
    'goals': {
        'phase': 'bulk',  # Wants to bulk...
        'target_weight_lbs': 155,  # ...but target is LOWER weight
        'timeline_weeks': 12,
        'primary_goal': 'build_muscle'
    },
    'expected_validation': {
        'error_type': 'conflicting_phase_and_target',
        'conflict': 'bulk_phase_with_weight_loss_goal'
    }
}


# Edge Case 3: Extreme body stats (very underweight)
EXTREME_UNDERWEIGHT = {
    'personal_info': {
        'weight_lbs': 160,
        'height_inches': 80,  # 6'8"
        'age': 25,
        'sex': 'male',
        'activity_level': 'sedentary'
    },
    'goals': {
        'phase': 'bulk',
        'target_weight_lbs': 185,
        'timeline_weeks': 50,
        'primary_goal': 'gain_weight_healthily'
    },
    'expected_validation': {
        'bmi': 17.2,  # Underweight
        'warning': 'medical_consultation_recommended',
        'healthy_weight_range': (185, 250)  # For 6'8"
    }
}


# Edge Case 4: Elderly user
ELDERLY_USER = {
    'personal_info': {
        'weight_lbs': 170,
        'height_inches': 70,
        'age': 68,
        'sex': 'male',
        'activity_level': 'lightly_active'
    },
    'goals': {
        'phase': 'maintain',
        'target_weight_lbs': 170,
        'timeline_weeks': 52,
        'primary_goal': 'general_fitness_and_mobility'
    },
    'expected_validation': {
        'age_category': 'senior',
        'recommendations': [
            'medical_clearance_required',
            'lower_intensity_8_15_reps',
            'longer_recovery_3_days_per_week_max',
            'emphasis_on_mobility_and_balance',
            'higher_protein_needs_1_0_1_2g_per_lb'
        ]
    }
}


# Edge case collection
EDGE_CASE_PERSONAS = {
    'unrealistic_goal': UNREALISTIC_GOAL,
    'conflicting_goals': CONFLICTING_GOALS,
    'extreme_underweight': EXTREME_UNDERWEIGHT,
    'elderly_user': ELDERLY_USER
}
