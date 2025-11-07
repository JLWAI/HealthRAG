"""
Monthly Progress Reports

Generate comprehensive monthly progress reports combining:
- Weight and body composition changes
- TDEE and metabolic adaptations
- Nutrition adherence
- Workout volume and performance
- Body measurements
- Coaching recommendations

Designed to provide actionable insights for the next training/diet block.
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from adaptive_tdee import WeightTracker, calculate_trend_weight
from tdee_analytics import TDEEHistoricalTracker, TDEESnapshot
from body_measurements import BodyMeasurementTracker, MeasurementComparison
from food_logger import FoodLogger
from workout_database import WorkoutDatabase


@dataclass
class MonthlyProgressReport:
    """Comprehensive monthly progress report"""
    month_start: str  # ISO format YYYY-MM-DD
    month_end: str
    phase: str  # cut, bulk, maintain, recomp

    # Weight changes
    start_weight_lbs: Optional[float]
    end_weight_lbs: Optional[float]
    weight_change_lbs: Optional[float]
    trend_weight_change_lbs: Optional[float]

    # Body measurements
    measurement_changes: Optional[MeasurementComparison]

    # Nutrition
    avg_daily_calories: Optional[float]
    avg_daily_protein_g: Optional[float]
    nutrition_compliance_pct: Optional[float]  # % of days logged
    days_logged: int

    # TDEE changes
    start_tdee: Optional[int]
    end_tdee: Optional[int]
    tdee_change: Optional[int]
    metabolic_adaptation_pct: Optional[float]

    # Workout performance
    workouts_completed: int
    total_volume_kg: Optional[float]
    volume_change_pct: Optional[float]

    # Achievements
    achievements: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]

    # Overall rating
    overall_rating: str  # "Excellent", "Good", "Fair", "Needs Attention"
    summary: str


def generate_monthly_progress_report(
    month: int,
    year: int,
    weight_tracker: WeightTracker,
    tdee_tracker: TDEEHistoricalTracker,
    measurement_tracker: BodyMeasurementTracker,
    food_logger: FoodLogger,
    workout_db: WorkoutDatabase,
    phase: str
) -> MonthlyProgressReport:
    """
    Generate comprehensive monthly progress report.

    Args:
        month: Month number (1-12)
        year: Year
        weight_tracker: WeightTracker instance
        tdee_tracker: TDEEHistoricalTracker instance
        measurement_tracker: BodyMeasurementTracker instance
        food_logger: FoodLogger instance
        workout_db: WorkoutDatabase instance
        phase: Current phase (cut, bulk, maintain, recomp)

    Returns:
        MonthlyProgressReport with complete analysis
    """
    # Calculate date range
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    start_str = month_start.isoformat()
    end_str = month_end.isoformat()

    # Initialize report data
    achievements = []
    areas_for_improvement = []
    recommendations = []

    # === WEIGHT ANALYSIS ===
    weight_entries = weight_tracker.get_weights(start_date=start_str, end_date=end_str)
    weight_entries.reverse()  # Chronological order

    start_weight = weight_entries[0].weight_lbs if weight_entries else None
    end_weight = weight_entries[-1].weight_lbs if weight_entries else None
    weight_change = (end_weight - start_weight) if (start_weight and end_weight) else None

    # Calculate trend weight change (more reliable)
    trend_weight_change = None
    if len(weight_entries) >= 7:
        weights = [e.weight_lbs for e in weight_entries]
        trend_weights = calculate_trend_weight(weights, alpha=0.3)
        trend_weight_change = trend_weights[-1] - trend_weights[0]

    # Evaluate weight progress
    if trend_weight_change:
        if phase in ['cut', 'recomp']:
            if trend_weight_change < -4:
                achievements.append(f"Lost {abs(trend_weight_change):.1f} lbs this month!")
            elif trend_weight_change < -2:
                achievements.append(f"Lost {abs(trend_weight_change):.1f} lbs - steady progress")
            elif trend_weight_change > 0:
                areas_for_improvement.append("Weight went up during cut - review calorie intake")
        elif phase == 'bulk':
            if 2 < trend_weight_change < 5:
                achievements.append(f"Gained {trend_weight_change:.1f} lbs - ideal lean bulk pace")
            elif trend_weight_change > 5:
                areas_for_improvement.append(f"Gained {trend_weight_change:.1f} lbs - may be too fast")
            elif trend_weight_change < 1:
                areas_for_improvement.append("Weight gain slower than expected - increase calories?")

    # === BODY MEASUREMENTS ===
    measurements = measurement_tracker.get_measurements(start_date=start_str, end_date=end_str)
    measurement_comparison = None

    if len(measurements) >= 2:
        measurements.sort(key=lambda m: m.date)
        measurement_comparison = measurement_tracker.compare_measurements(
            measurements[-1].date,
            measurements[0].date
        )

        # Evaluate measurement changes
        if measurement_comparison:
            if phase in ['cut', 'recomp']:
                waist_change = measurement_comparison.changes.get('waist_inches', 0)
                if waist_change < -1:
                    achievements.append(f"Waist down {abs(waist_change):.1f} inches - fat loss confirmed!")

                arms_change = measurement_comparison.changes.get('bicep_left_inches', 0)
                if arms_change > 0:
                    achievements.append(f"Arms grew {arms_change:.1f} inches while cutting - muscle retention!")

    # === NUTRITION ANALYSIS ===
    days_logged = 0
    avg_calories = None
    avg_protein = None

    try:
        # Count days with food logs
        current_date = month_start
        total_calories = 0
        total_protein = 0
        logged_days = 0

        while current_date <= month_end:
            day_summary = food_logger.get_daily_summary(current_date.isoformat())
            if day_summary.entries_logged > 0:
                logged_days += 1
                total_calories += day_summary.total_calories
                total_protein += day_summary.total_protein
            current_date += timedelta(days=1)

        days_logged = logged_days
        if logged_days > 0:
            avg_calories = total_calories / logged_days
            avg_protein = total_protein / logged_days

        # Calculate compliance
        total_days = (month_end - month_start).days + 1
        compliance_pct = (days_logged / total_days) * 100

        # Evaluate nutrition adherence
        if compliance_pct >= 90:
            achievements.append(f"Excellent food tracking - {compliance_pct:.0f}% of days logged!")
        elif compliance_pct >= 70:
            achievements.append(f"Good tracking consistency - {compliance_pct:.0f}% of days")
        elif compliance_pct < 50:
            areas_for_improvement.append(f"Low tracking consistency - only {compliance_pct:.0f}% of days logged")
            recommendations.append("Track food daily for better results and adaptive TDEE accuracy")

    except Exception as e:
        pass  # Food logger may not have data

    # === TDEE ANALYSIS ===
    tdee_snapshots = tdee_tracker.get_snapshots(start_date=start_str, end_date=end_str)
    tdee_snapshots.reverse()  # Chronological order

    start_tdee = tdee_snapshots[0].adaptive_tdee if tdee_snapshots else None
    end_tdee = tdee_snapshots[-1].adaptive_tdee if tdee_snapshots else None
    tdee_change = (end_tdee - start_tdee) if (start_tdee and end_tdee) else None

    # Metabolic adaptation detection
    metabolic_adaptation_pct = None
    if tdee_change:
        metabolic_adaptation_pct = (tdee_change / start_tdee) * 100

        if phase in ['cut', 'recomp']:
            if tdee_change < -200:
                areas_for_improvement.append(f"TDEE dropped {abs(tdee_change)} cal - significant metabolic adaptation")
                recommendations.append("Consider diet break or reverse diet to restore metabolism")
            elif tdee_change < -100:
                achievements.append("Minor metabolic adaptation detected - normal for dieting")

    # === WORKOUT ANALYSIS ===
    workouts_completed = 0
    total_volume = None
    volume_change_pct = None

    try:
        sessions = workout_db.get_sessions_in_date_range(start_str, end_str)
        workouts_completed = len(sessions)

        if workouts_completed > 0:
            # Calculate total volume (tonnage)
            total_volume = 0
            for session in sessions:
                sets = workout_db.get_sets_by_session(session.session_id)
                for s in sets:
                    if s.weight_kg and s.reps:
                        total_volume += s.weight_kg * s.reps

            # Evaluate workout consistency
            expected_workouts = 16  # ~4x/week for 4 weeks
            if workouts_completed >= expected_workouts:
                achievements.append(f"Completed {workouts_completed} workouts - excellent consistency!")
            elif workouts_completed >= 12:
                achievements.append(f"{workouts_completed} workouts completed - good consistency")
            elif workouts_completed < 8:
                areas_for_improvement.append(f"Only {workouts_completed} workouts - aim for 12-16/month")
                recommendations.append("Increase training frequency to 3-4x per week")

    except Exception as e:
        pass  # Workout database may not have data

    # === RECOMMENDATIONS ===
    # Phase-specific recommendations
    if phase in ['cut', 'recomp']:
        if trend_weight_change and abs(trend_weight_change) < 2:
            recommendations.append("Weight loss slower than expected - consider reducing calories by 100-150")
        if avg_protein and avg_protein < 0.8:
            recommendations.append("Increase protein to 1.0-1.2g/lb to preserve muscle during cut")

    elif phase == 'bulk':
        if trend_weight_change and trend_weight_change < 1.5:
            recommendations.append("Bulk progressing slowly - consider adding 150-200 calories")
        if workouts_completed and workouts_completed < 12:
            recommendations.append("Increase training volume to maximize muscle growth potential")

    # === OVERALL RATING ===
    rating_score = 0

    # Weight progress (40% of score)
    if trend_weight_change:
        if phase in ['cut', 'recomp'] and trend_weight_change < -2:
            rating_score += 40
        elif phase in ['cut', 'recomp'] and trend_weight_change < 0:
            rating_score += 25
        elif phase == 'bulk' and 2 < trend_weight_change < 5:
            rating_score += 40
        elif phase == 'bulk' and trend_weight_change > 0:
            rating_score += 25

    # Nutrition adherence (30% of score)
    if days_logged:
        compliance = (days_logged / ((month_end - month_start).days + 1))
        rating_score += int(compliance * 30)

    # Workout consistency (30% of score)
    if workouts_completed:
        workout_score = min(workouts_completed / 16, 1.0) * 30
        rating_score += int(workout_score)

    # Determine overall rating
    if rating_score >= 80:
        overall_rating = "Excellent"
        summary = "Outstanding month! You're crushing your goals with consistent effort."
    elif rating_score >= 60:
        overall_rating = "Good"
        summary = "Solid progress this month. Stay consistent and results will compound."
    elif rating_score >= 40:
        overall_rating = "Fair"
        summary = "Some progress, but there's room for improvement in consistency."
    else:
        overall_rating = "Needs Attention"
        summary = "This month needs more focus. Review your plan and recommit to consistency."

    return MonthlyProgressReport(
        month_start=start_str,
        month_end=end_str,
        phase=phase,
        start_weight_lbs=start_weight,
        end_weight_lbs=end_weight,
        weight_change_lbs=weight_change,
        trend_weight_change_lbs=trend_weight_change,
        measurement_changes=measurement_comparison,
        avg_daily_calories=avg_calories,
        avg_daily_protein_g=avg_protein,
        nutrition_compliance_pct=(days_logged / ((month_end - month_start).days + 1)) * 100 if days_logged else 0,
        days_logged=days_logged,
        start_tdee=start_tdee,
        end_tdee=end_tdee,
        tdee_change=tdee_change,
        metabolic_adaptation_pct=metabolic_adaptation_pct,
        workouts_completed=workouts_completed,
        total_volume_kg=total_volume,
        volume_change_pct=volume_change_pct,
        achievements=achievements,
        areas_for_improvement=areas_for_improvement,
        recommendations=recommendations,
        overall_rating=overall_rating,
        summary=summary
    )


def create_monthly_report_visualization(report: MonthlyProgressReport) -> go.Figure:
    """
    Create visual summary of monthly progress report.

    Args:
        report: MonthlyProgressReport object

    Returns:
        Plotly Figure with multi-panel visualization
    """
    # Create subplots: 2 rows, 2 columns
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Weight Progress',
            'Nutrition Adherence',
            'Workout Consistency',
            'TDEE Changes'
        ),
        specs=[
            [{'type': 'indicator'}, {'type': 'indicator'}],
            [{'type': 'bar'}, {'type': 'indicator'}]
        ]
    )

    # Weight change indicator
    weight_delta = report.trend_weight_change_lbs if report.trend_weight_change_lbs else 0
    weight_color = "green" if (report.phase in ['cut', 'recomp'] and weight_delta < 0) or (report.phase == 'bulk' and weight_delta > 0) else "red"

    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=report.end_weight_lbs if report.end_weight_lbs else 0,
        delta={'reference': report.start_weight_lbs if report.start_weight_lbs else 0, 'relative': False},
        title={'text': f"Weight Change ({report.phase})"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ), row=1, col=1)

    # Nutrition compliance indicator
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=report.nutrition_compliance_pct if report.nutrition_compliance_pct else 0,
        title={'text': "Tracking Consistency"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "lightblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 80], 'color': "lightyellow"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ), row=1, col=2)

    # Workout count bar
    fig.add_trace(go.Bar(
        x=['Completed', 'Target'],
        y=[report.workouts_completed, 16],
        marker_color=['lightblue', 'lightgray'],
        text=[report.workouts_completed, 16],
        textposition='auto'
    ), row=2, col=1)

    # TDEE change indicator
    tdee_delta = report.tdee_change if report.tdee_change else 0
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=report.end_tdee if report.end_tdee else 0,
        delta={'reference': report.start_tdee if report.start_tdee else 0, 'relative': False},
        title={'text': "TDEE Change (cal/day)"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ), row=2, col=2)

    fig.update_layout(
        title_text=f"Monthly Progress Summary: {report.month_start} to {report.month_end}",
        height=700,
        showlegend=False
    )

    return fig
