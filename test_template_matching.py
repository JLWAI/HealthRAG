#!/usr/bin/env python3
"""Debug script to test template matching"""

import sys
sys.path.insert(0, 'src')

from mesocycle_templates import get_recommended_template, get_templates_by_days, ALL_TEMPLATES

print("=" * 80)
print("TEMPLATE MATCHING DEBUG")
print("=" * 80)

# Test parameters
days_per_week = 4
training_level = "intermediate"
goals = ["hypertrophy_focus"]

print(f"\nSearching for template:")
print(f"  Days per week: {days_per_week}")
print(f"  Training level: {training_level}")
print(f"  Goals: {goals}")

print(f"\nAll available templates ({len(ALL_TEMPLATES)}):")
for t in ALL_TEMPLATES:
    print(f"  - {t.name}:")
    print(f"      Days: {t.days_per_week}")
    print(f"      Level: {t.min_training_level}")
    print(f"      Best for: {t.best_for}")

# Test days filtering
print(f"\nTemplates matching {days_per_week} days/week:")
matching_days = get_templates_by_days(days_per_week)
print(f"  Found {len(matching_days)} templates")
for t in matching_days:
    print(f"  - {t.name}")

# Test full matching
print(f"\nTrying get_recommended_template with goals={goals}:")
template = get_recommended_template(days_per_week, training_level, goals)
if template:
    print(f"  ✅ Found: {template.name}")
else:
    print(f"  ❌ No template found!")

# Try with broader goals
print(f"\nTrying with broader goals:")
broader_goals = ["intermediate", "4_days_available", "balanced_development"]
template2 = get_recommended_template(days_per_week, training_level, broader_goals)
if template2:
    print(f"  ✅ Found: {template2.name}")
else:
    print(f"  ❌ No template found!")

# Check UPPER_LOWER_4X specifically
print(f"\nChecking UPPER_LOWER_4X template specifically:")
for t in ALL_TEMPLATES:
    if t.name == "upper_lower_4x":
        print(f"  Found template: {t.name}")
        print(f"  Days per week: {t.days_per_week}")
        print(f"  Min training level: {t.min_training_level}")
        print(f"  Best for: {t.best_for}")
        print(f"  Matches days? {t.days_per_week == days_per_week}")
        print(f"  Matches level? {t.min_training_level <= training_level}")

        # Check goal matching
        for goal in goals:
            print(f"  Has '{goal}' in best_for? {goal in t.best_for}")
