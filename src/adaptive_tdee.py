"""
Adaptive TDEE System for HealthRAG

Implements MacroFactor-style adaptive TDEE calculation using:
1. EWMA (Exponentially Weighted Moving Average) for trend weight
2. Back-calculation TDEE from actual intake + weight change
3. Weekly macro adjustment recommendations

This module provides the foundation for intelligent, data-driven
nutrition coaching that adapts to individual responses.
"""

import sqlite3
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


def calculate_trend_weight(weights: List[float], alpha: float = 0.3) -> List[Optional[float]]:
    """
    Calculate trend weight using Exponentially Weighted Moving Average (EWMA).

    MacroFactor uses alpha ≈ 0.25-0.35 for optimal smoothing:
    - Lower alpha = smoother (less reactive to daily fluctuations)
    - Higher alpha = faster adaptation to real changes

    Algorithm:
        trend[0] = weights[0]
        trend[i] = (alpha × weights[i]) + ((1 - alpha) × trend[i-1])

    Args:
        weights: List of daily weights in chronological order
        alpha: Smoothing factor (0 < alpha < 1). Default 0.3 (MacroFactor-style)

    Returns:
        List of trend weights aligned with input. Returns None for positions
        where insufficient data exists (empty list, single point needs at least 1 value).

    Examples:
        >>> calculate_trend_weight([210.0, 209.5, 209.0])
        [210.0, 209.85, 209.595]

        >>> calculate_trend_weight([208.0, 209.0, 208.0, 207.0])  # Fluctuations
        [208.0, 208.3, 208.21, 207.847]

        >>> calculate_trend_weight([])
        []

        >>> calculate_trend_weight([210.0])
        [210.0]
    """
    # Guard: empty list
    if not weights:
        return []

    # Guard: single weight point (no trend calculation needed)
    if len(weights) == 1:
        return [weights[0]]

    # Guard: validate alpha range
    if not (0 < alpha < 1):
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")

    # Guard: check for None/invalid weights
    if any(w is None or not isinstance(w, (int, float)) for w in weights):
        raise ValueError("All weights must be valid numbers (int or float)")

    # Initialize trend with first weight
    trend = [weights[0]]

    # Calculate EWMA for subsequent weights
    for i in range(1, len(weights)):
        new_trend = (alpha * weights[i]) + ((1 - alpha) * trend[i - 1])
        trend.append(new_trend)

    return trend


def calculate_simple_moving_average(weights: List[float], window: int = 7) -> List[Optional[float]]:
    """
    Calculate simple moving average (SMA) for comparison with EWMA.

    Args:
        weights: List of daily weights in chronological order
        window: Number of days for averaging (default 7)

    Returns:
        List of averages. Returns None for positions with insufficient data.

    Examples:
        >>> calculate_simple_moving_average([210, 209, 208, 207, 206, 205, 204], window=7)
        [None, None, None, None, None, None, 207.0]
    """
    if not weights or len(weights) < window:
        return [None] * len(weights)

    result = [None] * (window - 1)

    for i in range(window - 1, len(weights)):
        window_weights = weights[i - window + 1 : i + 1]
        avg = sum(window_weights) / len(window_weights)
        result.append(avg)

    return result


@dataclass
class WeightEntry:
    """Single daily weight measurement"""
    entry_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD
    weight_lbs: float
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class WeightTrend:
    """Weight trend analysis"""
    date: str
    actual_weight: float
    trend_weight: float
    moving_average_7d: Optional[float]
    delta_from_goal: Optional[float]  # If user has goal weight
    rate_of_change_weekly: Optional[float]  # lbs/week


class WeightTracker:
    """
    Weight tracking system with SQLite backend.

    Features:
    - Daily weight logging
    - EWMA trend calculation
    - 7-day moving averages
    - Progress tracking vs. goal weight
    - Rate of change calculations

    Designed to integrate with adaptive TDEE calculation.
    """

    def __init__(self, db_path: str = "data/weights.db"):
        """
        Initialize weight tracker.

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

        # Weight entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                weight_lbs REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for date lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_weight_entries_date
            ON weight_entries(date DESC)
        """)

        conn.commit()
        conn.close()

    def log_weight(self, weight_lbs: float, log_date: Optional[str] = None,
                   notes: Optional[str] = None) -> int:
        """
        Log daily weight (replaces existing entry for same date).

        Args:
            weight_lbs: Weight in pounds
            log_date: Date in YYYY-MM-DD format (default: today)
            notes: Optional notes

        Returns:
            entry_id of logged weight

        Raises:
            ValueError: If weight is invalid
        """
        if weight_lbs <= 0 or weight_lbs > 1000:
            raise ValueError(f"Invalid weight: {weight_lbs} lbs")

        if log_date is None:
            log_date = date.today().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Use INSERT OR REPLACE to handle duplicate dates
            cursor.execute("""
                INSERT OR REPLACE INTO weight_entries (date, weight_lbs, notes)
                VALUES (?, ?, ?)
            """, (log_date, weight_lbs, notes))

            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id

        finally:
            conn.close()

    def get_weights(self, start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    limit: Optional[int] = None) -> List[WeightEntry]:
        """
        Retrieve weight entries ordered by date (newest first).

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Optional limit on number of entries

        Returns:
            List of WeightEntry objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM weight_entries WHERE 1=1"
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
            WeightEntry(
                entry_id=row['id'],
                date=row['date'],
                weight_lbs=row['weight_lbs'],
                notes=row['notes'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def get_trend_analysis(self, days: int = 30,
                          goal_weight: Optional[float] = None) -> List[WeightTrend]:
        """
        Get weight trend analysis with EWMA and moving averages.

        Args:
            days: Number of days to analyze (default 30)
            goal_weight: Optional goal weight for delta calculation

        Returns:
            List of WeightTrend objects with trend analysis
        """
        # Get weight entries in chronological order (oldest first)
        end_date = date.today().isoformat()
        start_date = (date.today() - timedelta(days=days)).isoformat()

        entries = self.get_weights(start_date=start_date, end_date=end_date)
        entries.reverse()  # Oldest first for trend calculation

        if not entries:
            return []

        # Extract weights and dates
        dates = [e.date for e in entries]
        weights = [e.weight_lbs for e in entries]

        # Calculate trends
        trend_weights = calculate_trend_weight(weights, alpha=0.3)
        moving_avgs = calculate_simple_moving_average(weights, window=7)

        # Calculate rate of change (lbs/week) if sufficient data
        rate_of_change = None
        if len(weights) >= 14:
            # Use trend weights for more stable rate calculation
            recent_trend = trend_weights[-1]
            older_trend = trend_weights[-14]
            rate_of_change = (recent_trend - older_trend) / 2  # 2 weeks = /2 for per-week

        # Build trend analysis
        results = []
        for i, entry in enumerate(entries):
            delta_from_goal = None
            if goal_weight is not None:
                delta_from_goal = entry.weight_lbs - goal_weight

            results.append(WeightTrend(
                date=entry.date,
                actual_weight=entry.weight_lbs,
                trend_weight=trend_weights[i],
                moving_average_7d=moving_avgs[i],
                delta_from_goal=delta_from_goal,
                rate_of_change_weekly=rate_of_change
            ))

        return results

    def get_latest_weight(self) -> Optional[WeightEntry]:
        """Get most recent weight entry"""
        entries = self.get_weights(limit=1)
        return entries[0] if entries else None

    def delete_weight(self, entry_date: str) -> bool:
        """
        Delete weight entry for specific date.

        Args:
            entry_date: Date in YYYY-MM-DD format

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM weight_entries WHERE date = ?", (entry_date,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted


def calculate_adaptive_tdee(
    weights: List[float],
    daily_calories: List[float],
    days: int = 14
) -> Optional[float]:
    """
    Back-calculate TDEE from actual weight change + calorie intake.

    MacroFactor-style algorithm:
        1. Calculate weight change over rolling window (use trend weight for stability)
        2. Convert weight change to calorie deficit/surplus (3500 cal = 1 lb)
        3. Add to average calorie intake to get estimated TDEE

    Formula:
        TDEE = Avg_Calories + (Weight_Change_lbs × 3500 / Days)

    Example:
        - Lost 2 lbs in 14 days (trend weight: 210 → 208)
        - Averaged 2100 cal/day
        - TDEE = 2100 + (-2 × 3500 / 14) = 2100 + (-500) = 2600 cal/day

    Args:
        weights: Daily weights in chronological order (oldest first)
        daily_calories: Daily calorie intake aligned with weights
        days: Rolling window for calculation (default 14)

    Returns:
        Estimated TDEE in calories/day, or None if insufficient data

    Raises:
        ValueError: If weights and calories lists don't match in length
    """
    if len(weights) != len(daily_calories):
        raise ValueError(
            f"Weights ({len(weights)}) and calories ({len(daily_calories)}) must have same length"
        )

    if len(weights) < days:
        return None  # Insufficient data

    # Use most recent 'days' entries
    recent_weights = weights[-days:]
    recent_calories = daily_calories[-days:]

    # Calculate trend weights for stability (less noise than actual weights)
    trend_weights = calculate_trend_weight(recent_weights, alpha=0.3)

    # Weight change from trend (first to last in window)
    weight_change_lbs = trend_weights[-1] - trend_weights[0]

    # Average calorie intake
    avg_calories = sum(recent_calories) / len(recent_calories)

    # Convert weight change to calories
    # 1 lb fat ≈ 3500 cal deficit/surplus
    calorie_equivalent = weight_change_lbs * 3500 / days

    # Back-calculate TDEE
    # If lost weight (negative change), we ate below TDEE
    # If gained weight (positive change), we ate above TDEE
    tdee = avg_calories - calorie_equivalent

    return round(tdee)


@dataclass
class MacroAdjustment:
    """Macro adjustment recommendation"""
    new_calories: int
    calorie_change: int
    reason: str
    coaching_message: str
    goal_rate: float
    actual_rate: float
    percent_deviation: float


def recommend_macro_adjustment(
    goal_rate_lbs_week: float,
    actual_rate_lbs_week: float,
    current_calories: int,
    current_protein_g: float,
    phase: str = "cut"
) -> MacroAdjustment:
    """
    Adherence-neutral macro adjustment recommendations.

    MacroFactor-style thresholds:
    - Within ±20% of goal: No change (natural variation)
    - Within ±50% of goal: ±100 cal adjustment (minor tweak)
    - Beyond ±50% of goal: ±150 cal adjustment (significant correction)

    Args:
        goal_rate_lbs_week: Target rate (negative for cut, positive for bulk)
        actual_rate_lbs_week: Actual measured rate from trend data
        current_calories: Current calorie target
        current_protein_g: Current protein target (stays constant)
        phase: "cut", "bulk", "maintain", or "recomp"

    Returns:
        MacroAdjustment with recommended changes and coaching message

    Examples:
        # Cutting too fast
        >>> recommend_macro_adjustment(-1.0, -1.5, 2100, 200, "cut")
        MacroAdjustment(
            new_calories=2200,
            calorie_change=100,
            reason="losing_too_fast",
            ...
        )

        # Bulking too slow
        >>> recommend_macro_adjustment(0.5, 0.2, 2800, 180, "bulk")
        MacroAdjustment(
            new_calories=2900,
            calorie_change=100,
            reason="gaining_too_slow",
            ...
        )
    """
    # Calculate deviation from goal
    if goal_rate_lbs_week == 0:
        # Maintenance: use absolute rate thresholds instead of percentage
        # Treat ±0.25 lbs/week as "stable"
        deviation_lbs = abs(actual_rate_lbs_week)
        percent_deviation = 0.0  # N/A for maintenance

        # For maintenance, check absolute thresholds differently
        if deviation_lbs < 0.25:
            # Stable - no change needed
            return MacroAdjustment(
                new_calories=current_calories,
                calorie_change=0,
                reason="stable",
                coaching_message=(
                    f"✅ Weight is stable (±0.25 lbs/week). Keep current calories at {current_calories}."
                ),
                goal_rate=goal_rate_lbs_week,
                actual_rate=actual_rate_lbs_week,
                percent_deviation=percent_deviation
            )
        # If deviation >= 0.25, will be handled by maintenance block below
    else:
        deviation_lbs = actual_rate_lbs_week - goal_rate_lbs_week
        percent_deviation = (deviation_lbs / abs(goal_rate_lbs_week)) * 100

    # Adherence-neutral thresholds (for non-maintenance phases)
    # MacroFactor logic: ignore small deviations (±20%), adjust for larger
    if goal_rate_lbs_week != 0 and abs(percent_deviation) <= 20:
        # On track - no change needed
        return MacroAdjustment(
            new_calories=current_calories,
            calorie_change=0,
            reason="on_track",
            coaching_message=(
                f"✅ You're on track! Actual rate: {actual_rate_lbs_week:+.1f} lbs/week "
                f"vs goal: {goal_rate_lbs_week:+.1f} lbs/week.\n\n"
                f"Keep doing what you're doing. Small weekly fluctuations are normal."
            ),
            goal_rate=goal_rate_lbs_week,
            actual_rate=actual_rate_lbs_week,
            percent_deviation=percent_deviation
        )

    # Determine adjustment magnitude
    if abs(percent_deviation) <= 50:
        cal_adjustment = 100  # Minor tweak
    else:
        cal_adjustment = 150  # Significant correction

    # Determine direction and reason
    if phase in ["cut", "recomp"]:
        # Cutting or recomp: negative rate is good
        if actual_rate_lbs_week < goal_rate_lbs_week:
            # Losing too fast
            new_calories = current_calories + cal_adjustment
            reason = "losing_too_fast"
            message = (
                f"⚠️ You're losing weight faster than planned.\n\n"
                f"**Actual:** {actual_rate_lbs_week:.2f} lbs/week (faster than goal: {goal_rate_lbs_week:.2f})\n"
                f"**Recommendation:** Increase to {new_calories} cal/day (+{cal_adjustment} cal)\n\n"
                f"**Why?** Faster weight loss can cost muscle mass. "
                f"Sustainable progress = better long-term results."
            )
        else:
            # Losing too slow
            new_calories = current_calories - cal_adjustment
            reason = "losing_too_slow"
            message = (
                f"📉 Weight loss is slower than expected.\n\n"
                f"**Actual:** {actual_rate_lbs_week:.2f} lbs/week (slower than goal: {goal_rate_lbs_week:.2f})\n"
                f"**Recommendation:** Decrease to {new_calories} cal/day (-{cal_adjustment} cal)\n\n"
                f"**Why?** A small adjustment will help you reach your goal on schedule."
            )

    elif phase == "bulk":
        # Bulking: positive rate is good
        if actual_rate_lbs_week > goal_rate_lbs_week:
            # Gaining too fast
            new_calories = current_calories - cal_adjustment
            reason = "gaining_too_fast"
            message = (
                f"⚠️ You're gaining weight faster than planned.\n\n"
                f"**Actual:** +{actual_rate_lbs_week:.2f} lbs/week (faster than goal: +{goal_rate_lbs_week:.2f})\n"
                f"**Recommendation:** Decrease to {new_calories} cal/day (-{cal_adjustment} cal)\n\n"
                f"**Why?** Too-fast gains = more fat, less muscle. "
                f"Slow and steady wins the bulking race."
            )
        else:
            # Gaining too slow
            new_calories = current_calories + cal_adjustment
            reason = "gaining_too_slow"
            message = (
                f"📈 Muscle gain is slower than expected.\n\n"
                f"**Actual:** +{actual_rate_lbs_week:.2f} lbs/week (slower than goal: +{goal_rate_lbs_week:.2f})\n"
                f"**Recommendation:** Increase to {new_calories} cal/day (+{cal_adjustment} cal)\n\n"
                f"**Why?** You have room to push harder and maximize muscle growth."
            )

    else:  # maintain
        # Maintenance: want rate near 0
        if abs(actual_rate_lbs_week) < 0.25:
            # Stable - no change
            new_calories = current_calories
            message = f"✅ Weight is stable (±0.25 lbs/week). Keep current calories at {current_calories}."
            reason = "stable"
        elif actual_rate_lbs_week < 0:
            # Losing weight unintentionally
            new_calories = current_calories + cal_adjustment
            reason = "unintended_loss"
            message = (
                f"📉 You're losing weight during maintenance.\n\n"
                f"**Actual:** {actual_rate_lbs_week:.2f} lbs/week\n"
                f"**Recommendation:** Increase to {new_calories} cal/day (+{cal_adjustment} cal)\n\n"
                f"**Why?** You're in a deficit. Add calories to stabilize weight."
            )
        else:
            # Gaining weight unintentionally
            new_calories = current_calories - cal_adjustment
            reason = "unintended_gain"
            message = (
                f"📈 You're gaining weight during maintenance.\n\n"
                f"**Actual:** +{actual_rate_lbs_week:.2f} lbs/week\n"
                f"**Recommendation:** Decrease to {new_calories} cal/day (-{cal_adjustment} cal)\n\n"
                f"**Why?** You're in a surplus. Reduce calories to stabilize weight."
            )

    return MacroAdjustment(
        new_calories=new_calories,
        calorie_change=new_calories - current_calories,
        reason=reason,
        coaching_message=message,
        goal_rate=goal_rate_lbs_week,
        actual_rate=actual_rate_lbs_week,
        percent_deviation=percent_deviation
    )


@dataclass
class AdaptiveTDEEInsight:
    """Complete adaptive TDEE analysis"""
    formula_tdee: int  # Mifflin-St Jeor estimate
    adaptive_tdee: Optional[int]  # Back-calculated from data
    tdee_delta: Optional[int]  # Difference (adaptive - formula)
    average_intake: Optional[float]  # Last 14 days
    weight_change_14d: Optional[float]  # Trend weight change
    has_sufficient_data: bool
    days_logged: int
    macro_adjustment: Optional[MacroAdjustment]


def get_adaptive_tdee_insight(
    weight_tracker: WeightTracker,
    food_logger,  # FoodLogger instance
    formula_tdee: int,
    goal_rate_lbs_week: float,
    current_calories: int,
    current_protein_g: float,
    phase: str = "cut",
    days: int = 14
) -> AdaptiveTDEEInsight:
    """
    Generate complete adaptive TDEE insight combining all data sources.

    This is the main integration function that pulls together:
    - Weight trend data
    - Food intake data
    - Formula-based TDEE
    - Goal tracking

    Args:
        weight_tracker: WeightTracker instance
        food_logger: FoodLogger instance
        formula_tdee: TDEE from Mifflin-St Jeor formula
        goal_rate_lbs_week: Target rate of change
        current_calories: Current calorie target
        current_protein_g: Current protein target
        phase: User's current phase
        days: Rolling window (default 14)

    Returns:
        AdaptiveTDEEInsight with complete analysis
    """
    # Get weight data
    weight_entries = weight_tracker.get_weights(limit=days)
    weight_entries.reverse()  # Chronological order (oldest first)

    if len(weight_entries) < days:
        return AdaptiveTDEEInsight(
            formula_tdee=formula_tdee,
            adaptive_tdee=None,
            tdee_delta=None,
            average_intake=None,
            weight_change_14d=None,
            has_sufficient_data=False,
            days_logged=len(weight_entries),
            macro_adjustment=None
        )

    # Get food data for same date range
    start_date = weight_entries[0].date
    end_date = weight_entries[-1].date

    try:
        # Get daily calories from food logger
        daily_nutrition = []
        for entry in weight_entries:
            day_summary = food_logger.get_daily_nutrition(entry.date)
            daily_nutrition.append(day_summary.total_calories)

        # Calculate adaptive TDEE
        weights = [e.weight_lbs for e in weight_entries]
        adaptive_tdee = calculate_adaptive_tdee(weights, daily_nutrition, days=days)

        # Calculate trend weight change
        trend_weights = calculate_trend_weight(weights, alpha=0.3)
        weight_change = trend_weights[-1] - trend_weights[0]

        # Average intake
        avg_intake = sum(daily_nutrition) / len(daily_nutrition)

        # Calculate macro adjustment recommendation
        # Use trend-based rate of change
        actual_rate = (weight_change / days) * 7  # Convert to lbs/week

        macro_adj = recommend_macro_adjustment(
            goal_rate_lbs_week=goal_rate_lbs_week,
            actual_rate_lbs_week=actual_rate,
            current_calories=current_calories,
            current_protein_g=current_protein_g,
            phase=phase
        )

        return AdaptiveTDEEInsight(
            formula_tdee=formula_tdee,
            adaptive_tdee=adaptive_tdee,
            tdee_delta=adaptive_tdee - formula_tdee if adaptive_tdee else None,
            average_intake=avg_intake,
            weight_change_14d=weight_change,
            has_sufficient_data=True,
            days_logged=len(weight_entries),
            macro_adjustment=macro_adj
        )

    except Exception as e:
        # Food data incomplete or error
        return AdaptiveTDEEInsight(
            formula_tdee=formula_tdee,
            adaptive_tdee=None,
            tdee_delta=None,
            average_intake=None,
            weight_change_14d=None,
            has_sufficient_data=False,
            days_logged=len(weight_entries),
            macro_adjustment=None
        )
