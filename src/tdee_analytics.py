"""
Advanced TDEE Analytics and Visualization

Provides comprehensive analytics, visualizations, and insights for the
Adaptive TDEE system. Includes:
- Historical TDEE tracking
- Trend charts (Plotly)
- Progress comparisons
- Predictive goal date calculations
- Water weight spike detection
- Monthly progress reports
- Export functionality

Based on Renaissance Periodization principles and MacroFactor methodology.
"""

import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
import json
import csv


@dataclass
class TDEESnapshot:
    """Historical TDEE snapshot"""
    snapshot_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD

    # TDEE calculations
    formula_tdee: int  # Mifflin-St Jeor estimate
    adaptive_tdee: Optional[int]  # Back-calculated from data
    tdee_delta: Optional[int]  # Difference (adaptive - formula)

    # Supporting data
    average_intake_14d: Optional[float]
    weight_lbs: Optional[float]
    trend_weight_lbs: Optional[float]
    weight_change_14d: Optional[float]

    # Goal tracking
    goal_rate_lbs_week: float
    actual_rate_lbs_week: Optional[float]
    percent_deviation: Optional[float]

    # Macro recommendations
    recommended_calories: int
    calorie_adjustment: int
    recommended_protein_g: float
    recommended_carbs_g: float
    recommended_fat_g: float

    # Metadata
    phase: str  # cut, bulk, maintain, recomp
    confidence_score: Optional[float] = None
    created_at: Optional[str] = None


@dataclass
class WaterWeightAlert:
    """Water weight spike detection"""
    date: str
    weight_lbs: float
    trend_weight_lbs: float
    deviation_lbs: float
    is_spike: bool  # True if sudden increase
    is_drop: bool  # True if sudden decrease
    likely_causes: List[str]
    recommendation: str


@dataclass
class GoalPrediction:
    """Predictive goal date calculation"""
    current_weight_lbs: float
    goal_weight_lbs: float
    weight_to_go: float

    current_rate_lbs_week: float
    predicted_weeks: float
    predicted_date: str  # ISO format

    # Confidence metrics
    data_quality_days: int
    confidence: str  # "High", "Medium", "Low"

    # Alternative scenarios
    best_case_weeks: float  # If rate improves 20%
    worst_case_weeks: float  # If rate slows 20%


class TDEEHistoricalTracker:
    """
    Historical TDEE tracking database.

    Stores snapshots of adaptive TDEE calculations to enable:
    - Trend analysis over time
    - Progress comparisons
    - Monthly reports
    - Data export
    """

    def __init__(self, db_path: str = "data/tdee_history.db"):
        """
        Initialize historical TDEE tracker.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # TDEE snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tdee_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,

                -- TDEE calculations
                formula_tdee INTEGER NOT NULL,
                adaptive_tdee INTEGER,
                tdee_delta INTEGER,

                -- Supporting data
                average_intake_14d REAL,
                weight_lbs REAL,
                trend_weight_lbs REAL,
                weight_change_14d REAL,

                -- Goal tracking
                goal_rate_lbs_week REAL NOT NULL,
                actual_rate_lbs_week REAL,
                percent_deviation REAL,

                -- Macro recommendations
                recommended_calories INTEGER NOT NULL,
                calorie_adjustment INTEGER NOT NULL,
                recommended_protein_g REAL NOT NULL,
                recommended_carbs_g REAL NOT NULL,
                recommended_fat_g REAL NOT NULL,

                -- Metadata
                phase TEXT NOT NULL,
                confidence_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for date lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshots_date
            ON tdee_snapshots(date DESC)
        """)

        conn.commit()
        conn.close()

    def save_snapshot(self, snapshot: TDEESnapshot) -> int:
        """
        Save TDEE snapshot (replaces existing entry for same date).

        Args:
            snapshot: TDEESnapshot object

        Returns:
            snapshot_id of saved entry
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            data = asdict(snapshot)
            data.pop('snapshot_id', None)
            data.pop('created_at', None)

            columns = list(data.keys())
            placeholders = ['?' for _ in columns]
            values = [data[col] for col in columns]

            query = f"""
                INSERT OR REPLACE INTO tdee_snapshots ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """

            cursor.execute(query, values)
            snapshot_id = cursor.lastrowid
            conn.commit()

            return snapshot_id

        finally:
            conn.close()

    def get_snapshots(self, start_date: Optional[str] = None,
                     end_date: Optional[str] = None,
                     limit: Optional[int] = None) -> List[TDEESnapshot]:
        """
        Retrieve TDEE snapshots ordered by date (newest first).

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Optional limit on number of entries

        Returns:
            List of TDEESnapshot objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM tdee_snapshots WHERE 1=1"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            TDEESnapshot(
                snapshot_id=row['id'],
                date=row['date'],
                formula_tdee=row['formula_tdee'],
                adaptive_tdee=row['adaptive_tdee'],
                tdee_delta=row['tdee_delta'],
                average_intake_14d=row['average_intake_14d'],
                weight_lbs=row['weight_lbs'],
                trend_weight_lbs=row['trend_weight_lbs'],
                weight_change_14d=row['weight_change_14d'],
                goal_rate_lbs_week=row['goal_rate_lbs_week'],
                actual_rate_lbs_week=row['actual_rate_lbs_week'],
                percent_deviation=row['percent_deviation'],
                recommended_calories=row['recommended_calories'],
                calorie_adjustment=row['calorie_adjustment'],
                recommended_protein_g=row['recommended_protein_g'],
                recommended_carbs_g=row['recommended_carbs_g'],
                recommended_fat_g=row['recommended_fat_g'],
                phase=row['phase'],
                confidence_score=row['confidence_score'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def get_latest_snapshot(self) -> Optional[TDEESnapshot]:
        """Get most recent TDEE snapshot"""
        snapshots = self.get_snapshots(limit=1)
        return snapshots[0] if snapshots else None


def create_tdee_trend_chart(snapshots: List[TDEESnapshot]) -> go.Figure:
    """
    Create interactive Plotly chart showing TDEE trends over time.

    Args:
        snapshots: List of TDEESnapshot objects (chronological order)

    Returns:
        Plotly Figure object
    """
    if not snapshots:
        # Empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No TDEE data available yet. Log weight and food for 14 days to start tracking.",
            showarrow=False,
            font=dict(size=14)
        )
        return fig

    # Extract data
    dates = [s.date for s in snapshots]
    formula_tdees = [s.formula_tdee for s in snapshots]
    adaptive_tdees = [s.adaptive_tdee if s.adaptive_tdee else None for s in snapshots]
    avg_intakes = [s.average_intake_14d if s.average_intake_14d else None for s in snapshots]

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Formula TDEE (dashed line)
    fig.add_trace(go.Scatter(
        x=dates,
        y=formula_tdees,
        name='Formula TDEE',
        line=dict(color='gray', width=2, dash='dash'),
        mode='lines',
        hovertemplate='<b>Formula TDEE</b><br>%{y} cal<extra></extra>'
    ))

    # Adaptive TDEE (solid line)
    fig.add_trace(go.Scatter(
        x=dates,
        y=adaptive_tdees,
        name='Adaptive TDEE',
        line=dict(color='blue', width=3),
        mode='lines+markers',
        hovertemplate='<b>Adaptive TDEE</b><br>%{y} cal<extra></extra>'
    ))

    # Average intake (area fill)
    fig.add_trace(go.Scatter(
        x=dates,
        y=avg_intakes,
        name='Avg Intake (14d)',
        fill='tozeroy',
        fillcolor='rgba(255, 165, 0, 0.2)',
        line=dict(color='orange', width=2),
        mode='lines',
        hovertemplate='<b>Average Intake</b><br>%{y:.0f} cal<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        title='TDEE Trend Over Time',
        xaxis_title='Date',
        yaxis_title='Calories per Day',
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500
    )

    return fig


def create_weight_progress_chart(
    weight_entries: List[Tuple[str, float, float]]  # (date, actual_weight, trend_weight)
) -> go.Figure:
    """
    Create weight progress chart with actual vs. trend weight.

    Args:
        weight_entries: List of (date, actual_weight, trend_weight) tuples

    Returns:
        Plotly Figure object
    """
    if not weight_entries:
        fig = go.Figure()
        fig.add_annotation(
            text="No weight data available. Start logging your daily weight!",
            showarrow=False,
            font=dict(size=14)
        )
        return fig

    dates = [e[0] for e in weight_entries]
    actual_weights = [e[1] for e in weight_entries]
    trend_weights = [e[2] for e in weight_entries]

    fig = go.Figure()

    # Actual weight (scatter with small markers)
    fig.add_trace(go.Scatter(
        x=dates,
        y=actual_weights,
        name='Daily Weight',
        mode='markers',
        marker=dict(color='lightblue', size=6),
        hovertemplate='<b>Daily Weight</b><br>%{y:.1f} lbs<extra></extra>'
    ))

    # Trend weight (smooth line)
    fig.add_trace(go.Scatter(
        x=dates,
        y=trend_weights,
        name='Trend Weight (EWMA)',
        line=dict(color='blue', width=3),
        mode='lines',
        hovertemplate='<b>Trend Weight</b><br>%{y:.1f} lbs<extra></extra>'
    ))

    fig.update_layout(
        title='Weight Progress: Daily vs. Trend',
        xaxis_title='Date',
        yaxis_title='Weight (lbs)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )

    return fig


def detect_water_weight_spikes(
    weight_entries: List[Tuple[str, float, float]],  # (date, actual, trend)
    threshold_lbs: float = 2.0
) -> List[WaterWeightAlert]:
    """
    Detect sudden water weight spikes/drops.

    A spike is detected when actual weight deviates significantly from trend weight,
    indicating temporary water retention rather than true fat/muscle change.

    Args:
        weight_entries: List of (date, actual_weight, trend_weight) tuples
        threshold_lbs: Deviation threshold (default 2.0 lbs)

    Returns:
        List of WaterWeightAlert objects for significant deviations
    """
    alerts = []

    for date, actual, trend in weight_entries:
        deviation = actual - trend

        if abs(deviation) >= threshold_lbs:
            is_spike = deviation > 0
            is_drop = deviation < 0

            # Determine likely causes
            causes = []
            if is_spike:
                causes = [
                    "High sodium intake (restaurant meal, processed food)",
                    "High carbohydrate intake (glycogen + water storage)",
                    "Insufficient water intake (paradoxically causes retention)",
                    "Hormonal fluctuations (menstrual cycle for women)",
                    "New exercise program (inflammation + glycogen)",
                    "Lack of sleep or high stress (cortisol)"
                ]
                recommendation = (
                    f"Don't panic! This is likely water weight (+{abs(deviation):.1f} lbs).\n\n"
                    "What to do:\n"
                    "- Drink plenty of water (helps flush excess sodium)\n"
                    "- Keep protein and veggies consistent\n"
                    "- Continue tracking - it should normalize in 2-3 days\n"
                    "- Don't reduce calories based on this spike"
                )
            else:
                causes = [
                    "Low sodium intake (less water retention)",
                    "Low carbohydrate intake (glycogen depletion)",
                    "Increased water intake",
                    "Better sleep (reduced cortisol)",
                    "Natural fluctuation after previous spike"
                ]
                recommendation = (
                    f"You're down {abs(deviation):.1f} lbs from trend, likely water weight.\n\n"
                    "What to do:\n"
                    "- Don't assume this is all fat loss\n"
                    "- Keep tracking to see if trend weight follows\n"
                    "- Don't increase calories based on this drop"
                )

            alerts.append(WaterWeightAlert(
                date=date,
                weight_lbs=actual,
                trend_weight_lbs=trend,
                deviation_lbs=deviation,
                is_spike=is_spike,
                is_drop=is_drop,
                likely_causes=causes,
                recommendation=recommendation
            ))

    return alerts


def predict_goal_date(
    current_weight_lbs: float,
    goal_weight_lbs: float,
    current_rate_lbs_week: float,
    data_days: int
) -> GoalPrediction:
    """
    Predict when user will reach their goal weight.

    Args:
        current_weight_lbs: Current weight (trend weight preferred)
        goal_weight_lbs: Target weight
        current_rate_lbs_week: Current rate of change (negative for loss)
        data_days: Days of data used to calculate rate (for confidence)

    Returns:
        GoalPrediction with estimated date and scenarios
    """
    weight_to_go = abs(goal_weight_lbs - current_weight_lbs)

    # Handle zero or near-zero rate
    if abs(current_rate_lbs_week) < 0.1:
        # Minimal progress - use a default slow rate
        if goal_weight_lbs < current_weight_lbs:
            current_rate_lbs_week = -0.5  # Slow cut
        else:
            current_rate_lbs_week = 0.5  # Slow bulk

    # Calculate predicted weeks
    predicted_weeks = weight_to_go / abs(current_rate_lbs_week)

    # Calculate prediction date
    predicted_date = (date.today() + timedelta(weeks=predicted_weeks)).isoformat()

    # Confidence based on data quality
    if data_days >= 28:
        confidence = "High"
    elif data_days >= 14:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Alternative scenarios (±20% rate change)
    best_case_rate = abs(current_rate_lbs_week) * 1.2
    worst_case_rate = abs(current_rate_lbs_week) * 0.8

    best_case_weeks = weight_to_go / best_case_rate
    worst_case_weeks = weight_to_go / worst_case_rate

    return GoalPrediction(
        current_weight_lbs=current_weight_lbs,
        goal_weight_lbs=goal_weight_lbs,
        weight_to_go=weight_to_go,
        current_rate_lbs_week=current_rate_lbs_week,
        predicted_weeks=predicted_weeks,
        predicted_date=predicted_date,
        data_quality_days=data_days,
        confidence=confidence,
        best_case_weeks=best_case_weeks,
        worst_case_weeks=worst_case_weeks
    )


def export_tdee_data_csv(snapshots: List[TDEESnapshot], output_path: str):
    """
    Export TDEE snapshots to CSV file.

    Args:
        snapshots: List of TDEESnapshot objects
        output_path: Path to output CSV file
    """
    if not snapshots:
        raise ValueError("No snapshots to export")

    # Convert to list of dicts
    data = [asdict(s) for s in snapshots]

    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def export_tdee_data_json(snapshots: List[TDEESnapshot], output_path: str):
    """
    Export TDEE snapshots to JSON file.

    Args:
        snapshots: List of TDEESnapshot objects
        output_path: Path to output JSON file
    """
    if not snapshots:
        raise ValueError("No snapshots to export")

    # Convert to list of dicts
    data = [asdict(s) for s in snapshots]

    # Write JSON
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


def generate_weekly_comparison(
    this_week_snapshot: TDEESnapshot,
    last_week_snapshot: TDEESnapshot
) -> Dict:
    """
    Generate week-over-week comparison.

    Args:
        this_week_snapshot: Most recent TDEE snapshot
        last_week_snapshot: Snapshot from 7 days ago

    Returns:
        Dictionary with comparison metrics
    """
    comparison = {
        'weight_change_lbs': None,
        'tdee_change_cal': None,
        'intake_change_cal': None,
        'rate_change_lbs_week': None,
        'progress_summary': '',
        'recommendations': []
    }

    # Weight change
    if this_week_snapshot.trend_weight_lbs and last_week_snapshot.trend_weight_lbs:
        weight_change = this_week_snapshot.trend_weight_lbs - last_week_snapshot.trend_weight_lbs
        comparison['weight_change_lbs'] = round(weight_change, 2)

    # TDEE change
    if this_week_snapshot.adaptive_tdee and last_week_snapshot.adaptive_tdee:
        tdee_change = this_week_snapshot.adaptive_tdee - last_week_snapshot.adaptive_tdee
        comparison['tdee_change_cal'] = tdee_change

    # Intake change
    if this_week_snapshot.average_intake_14d and last_week_snapshot.average_intake_14d:
        intake_change = this_week_snapshot.average_intake_14d - last_week_snapshot.average_intake_14d
        comparison['intake_change_cal'] = round(intake_change)

    # Rate change
    if this_week_snapshot.actual_rate_lbs_week is not None and last_week_snapshot.actual_rate_lbs_week is not None:
        rate_change = this_week_snapshot.actual_rate_lbs_week - last_week_snapshot.actual_rate_lbs_week
        comparison['rate_change_lbs_week'] = round(rate_change, 2)

    # Generate summary
    if comparison['weight_change_lbs'] is not None:
        if this_week_snapshot.phase in ['cut', 'recomp']:
            if comparison['weight_change_lbs'] < -1:
                comparison['progress_summary'] = f"Excellent progress! Down {abs(comparison['weight_change_lbs']):.1f} lbs this week."
            elif comparison['weight_change_lbs'] < 0:
                comparison['progress_summary'] = f"Good progress. Down {abs(comparison['weight_change_lbs']):.1f} lbs this week."
            elif comparison['weight_change_lbs'] > 0:
                comparison['progress_summary'] = f"Weight up {comparison['weight_change_lbs']:.1f} lbs. May need adjustment."
        elif this_week_snapshot.phase == 'bulk':
            if 0 < comparison['weight_change_lbs'] < 1:
                comparison['progress_summary'] = f"Great lean bulk! Up {comparison['weight_change_lbs']:.1f} lbs this week."
            elif comparison['weight_change_lbs'] > 1:
                comparison['progress_summary'] = f"Gaining a bit fast. Up {comparison['weight_change_lbs']:.1f} lbs - consider slowing."

    return comparison
