"""
Program Export for HealthRAG
Export training programs to Google Sheets-compatible formats (Excel, CSV)

Features:
- Complete week-by-week breakdown
- Exercise alternatives with tier explanations
- Rep ranges and RIR progression
- Hypertrophy benefits for each exercise
"""

import json
from datetime import date
from typing import Dict, List
import pandas as pd
from io import BytesIO


def export_program_to_excel(program_json_path: str) -> BytesIO:
    """
    Export training program to Excel format for Google Sheets.

    Args:
        program_json_path: Path to program JSON file

    Returns:
        BytesIO object with Excel file data
    """
    # Load program
    with open(program_json_path, 'r') as f:
        program = json.load(f)

    # Create Excel writer
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Sheet 1: Program Overview
    overview_data = {
        'Program': [program['template_name'].replace('_', ' ').title()],
        'Start Date': [program['start_date']],
        'Duration': [f"{len(program['weeks'])} weeks (5 weeks + deload)"],
        'S+ Tier Exercises': [f"{program['coverage_report']['s_plus_available']}/{program['coverage_report']['s_plus_total']}"],
        'S Tier Exercises': [f"{program['coverage_report']['s_available']}/{program['coverage_report']['s_total']}"],
        'Equipment': [', '.join(program['equipment_used'][:5]) + ('...' if len(program['equipment_used']) > 5 else '')]
    }
    df_overview = pd.DataFrame(overview_data)
    df_overview.to_excel(writer, sheet_name='Overview', index=False)

    # Sheet 2-7: Each week's workouts
    for week in program['weeks']:
        week_num = week['week_number']
        is_deload = week['is_deload']
        sheet_name = f"Week {week_num}" if not is_deload else "Deload"

        # Build workout table
        rows = []
        rows.append(['', '', '', '', '', ''])  # Blank row
        rows.append([f"Week {week_num}: {week['notes']}", '', '', '', '', ''])
        rows.append([f"Total Weekly Sets: {week['total_weekly_sets']}", '', '', '', '', ''])
        rows.append(['', '', '', '', '', ''])  # Blank row

        for workout in week['workouts']:
            # Workout header
            rows.append([f"🏋️ {workout['day_name']}", '', '', '', '', ''])
            rows.append(['', f"Duration: ~{workout['estimated_duration_min']} min", '', '', '', ''])
            rows.append(['', f"Muscle Groups: {', '.join([m.capitalize() for m in workout['muscle_groups']])}",  '', '', '', ''])
            rows.append(['', '', '', '', '', ''])  # Blank row

            # Exercise table header
            rows.append(['Exercise', 'Tier', 'Sets', 'Reps', 'RIR', 'Notes'])

            # Exercises
            for ex in workout['exercises']:
                rows.append([
                    ex['name'],
                    ex['tier'],
                    ex['sets'],
                    ex['reps'],
                    ex['rir'],
                    (ex['notes'][:50] + '...') if ex['notes'] and len(ex['notes']) > 50 else (ex['notes'] or '')
                ])

            rows.append(['', '', '', '', '', ''])  # Blank row between workouts

        df_week = pd.DataFrame(rows)
        df_week.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    # Sheet: Exercise Alternatives & Explanations
    # This would require re-running the exercise selector to get alternatives
    # For now, include a summary

    alt_rows = []
    alt_rows.append(['Exercise Name', 'Tier', 'Why This Exercise?'])
    alt_rows.append(['', '', ''])

    # Add unique exercises from all weeks
    unique_exercises = {}
    for week in program['weeks']:
        for workout in week['workouts']:
            for ex in workout['exercises']:
                if ex['name'] not in unique_exercises:
                    unique_exercises[ex['name']] = {
                        'tier': ex['tier'],
                        'notes': ex['notes']
                    }

    # Add tier explanations
    tier_explanations = {
        'S+': 'Best-of-the-best exercise for hypertrophy. Highest stimulus-to-fatigue ratio.',
        'S': 'Excellent exercise with strong research support. Great for muscle growth.',
        'A': 'Solid exercise option. Good hypertrophy potential.',
        'B': 'Acceptable exercise. Can be used when S/A tier options unavailable.'
    }

    for ex_name, ex_data in sorted(unique_exercises.items()):
        tier = ex_data['tier']
        explanation = tier_explanations.get(tier, 'Good exercise for hypertrophy')
        alt_rows.append([
            ex_name,
            tier,
            explanation
        ])

    df_alt = pd.DataFrame(alt_rows)
    df_alt.to_excel(writer, sheet_name='Exercise Guide', index=False, header=False)

    # Sheet: RIR Progression Explained
    rir_rows = []
    rir_rows.append(['Week', 'RIR', 'Description', 'Intensity'])
    rir_rows.append([1, 3, 'Conservative - 3 reps left in tank', 'Moderate'])
    rir_rows.append([2, 2, 'Moderate - 2 reps left in tank', 'Moderate-Hard'])
    rir_rows.append([3, 2, 'Maintain - 2 reps left in tank', 'Moderate-Hard'])
    rir_rows.append([4, 1, 'Hard - 1 rep left in tank', 'Hard'])
    rir_rows.append([5, 0, 'Failure - No reps left (max effort)', 'Maximum'])
    rir_rows.append([6, 3, 'Deload - Easy recovery', 'Recovery'])
    rir_rows.append(['', '', '', ''])
    rir_rows.append(['RIR = Reps in Reserve', '', '', ''])
    rir_rows.append(['How many more reps you could do before failure', '', '', ''])
    rir_rows.append(['', '', '', ''])
    rir_rows.append(['Progressive Overload Strategy:', '', '', ''])
    rir_rows.append(['As RIR decreases, increase weight to maintain intensity', '', '', ''])

    df_rir = pd.DataFrame(rir_rows)
    df_rir.to_excel(writer, sheet_name='RIR Guide', index=False, header=False)

    # Save and return
    writer.close()
    output.seek(0)
    return output


def export_program_to_csv(program_json_path: str) -> str:
    """
    Export training program to simple CSV format.

    Args:
        program_json_path: Path to program JSON file

    Returns:
        CSV string
    """
    # Load program
    with open(program_json_path, 'r') as f:
        program = json.load(f)

    rows = []

    # Header
    rows.append(['Program', program['template_name']])
    rows.append(['Start Date', program['start_date']])
    rows.append([''])

    # Each week
    for week in program['weeks']:
        rows.append([f"WEEK {week['week_number']}", week['notes']])
        rows.append([''])

        for workout in week['workouts']:
            rows.append([workout['day_name'], '', '', '', ''])
            rows.append(['Exercise', 'Tier', 'Sets', 'Reps', 'RIR'])

            for ex in workout['exercises']:
                rows.append([
                    ex['name'],
                    ex['tier'],
                    ex['sets'],
                    ex['reps'],
                    ex['rir']
                ])

            rows.append([''])

    # Convert to CSV string
    import csv
    from io import StringIO
    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    return output.getvalue()


if __name__ == "__main__":
    # Test export
    import sys

    if len(sys.argv) > 1:
        program_path = sys.argv[1]
    else:
        program_path = "data/current_program.json"

    print(f"Exporting program from {program_path}...")

    # Test Excel export
    excel_data = export_program_to_excel(program_path)
    with open("data/program_export.xlsx", "wb") as f:
        f.write(excel_data.getvalue())
    print("✅ Excel export saved to data/program_export.xlsx")

    # Test CSV export
    csv_data = export_program_to_csv(program_path)
    with open("data/program_export.csv", "w") as f:
        f.write(csv_data)
    print("✅ CSV export saved to data/program_export.csv")
