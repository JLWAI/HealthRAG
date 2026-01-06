"""
Weight Service Layer - Integrates weight tracking with adaptive TDEE.

Provides database operations for weight tracking with EWMA trend calculation.
Uses src/adaptive_tdee.py for MacroFactor-style trend weight smoothing.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import date, timedelta
from sqlalchemy.orm import Session

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from adaptive_tdee import calculate_trend_weight

# Import database models
from models.database import WeightEntry


class WeightService:
    """
    Service layer for weight tracking operations.

    Integrates weight logging with EWMA trend calculation
    for adaptive TDEE (MacroFactor-style).
    """

    def __init__(self):
        """Initialize weight service."""
        self.alpha = 0.3  # EWMA smoothing factor (MacroFactor-style)

    def create_weight_entry(
        self,
        db: Session,
        user_id: str,
        weight_lbs: float,
        entry_date: str,
        notes: Optional[str] = None
    ) -> WeightEntry:
        """
        Create a new weight entry with EWMA trend calculation.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            weight_lbs: Weight in pounds
            entry_date: Date (YYYY-MM-DD)
            notes: Optional notes

        Returns:
            WeightEntry object with calculated trend_weight_lbs
        """
        # Get all previous weights for trend calculation
        previous_weights = self.get_weight_entries(db, user_id)

        # Calculate new trend weight
        weights = [w.weight_lbs for w in previous_weights]
        weights.append(weight_lbs)  # Add current weight

        trend_weights = calculate_trend_weight(weights, alpha=self.alpha)
        new_trend_weight = trend_weights[-1]  # Latest trend value

        # Create weight entry
        weight_entry = WeightEntry(
            user_id=user_id,
            date=entry_date,
            weight_lbs=weight_lbs,
            trend_weight_lbs=new_trend_weight,
            notes=notes
        )

        db.add(weight_entry)
        db.commit()
        db.refresh(weight_entry)

        return weight_entry

    def get_weight_entries(
        self,
        db: Session,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[WeightEntry]:
        """
        Get weight entries for a user.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            start_date: Start date (YYYY-MM-DD), optional
            end_date: End date (YYYY-MM-DD), optional
            limit: Maximum number of entries to return

        Returns:
            List of WeightEntry objects (ordered by date ascending)
        """
        query = db.query(WeightEntry).filter(WeightEntry.user_id == user_id)

        if start_date:
            query = query.filter(WeightEntry.date >= start_date)

        if end_date:
            query = query.filter(WeightEntry.date <= end_date)

        query = query.order_by(WeightEntry.date.asc())

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_weight_trend(
        self,
        db: Session,
        user_id: str,
        days: int = 30
    ) -> Dict:
        """
        Get weight trend data for visualization.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            days: Number of days to include (default 30)

        Returns:
            Dictionary with:
            - dates: List of dates
            - weights: List of daily weights
            - trend_weights: List of EWMA trend weights
            - weekly_change: Change in trend weight over last 7 days
            - monthly_change: Change in trend weight over last 30 days
        """
        end_date = date.today().isoformat()
        start_date = (date.today() - timedelta(days=days)).isoformat()

        entries = self.get_weight_entries(db, user_id, start_date, end_date)

        if not entries:
            return {
                "dates": [],
                "weights": [],
                "trend_weights": [],
                "weekly_change": None,
                "monthly_change": None
            }

        dates = [e.date for e in entries]
        weights = [e.weight_lbs for e in entries]
        trend_weights = [e.trend_weight_lbs for e in entries]

        # Calculate weekly change (last 7 days)
        weekly_change = None
        if len(trend_weights) >= 7:
            weekly_change = trend_weights[-1] - trend_weights[-7]

        # Calculate monthly change (last 30 days)
        monthly_change = None
        if len(trend_weights) >= 30:
            monthly_change = trend_weights[-1] - trend_weights[-30]
        elif len(trend_weights) > 0:
            # If less than 30 days, use first available entry
            monthly_change = trend_weights[-1] - trend_weights[0]

        return {
            "dates": dates,
            "weights": weights,
            "trend_weights": trend_weights,
            "weekly_change": weekly_change,
            "monthly_change": monthly_change,
            "latest_weight": weights[-1] if weights else None,
            "latest_trend": trend_weights[-1] if trend_weights else None,
            "entry_count": len(entries)
        }

    def recalculate_all_trends(
        self,
        db: Session,
        user_id: str
    ) -> int:
        """
        Recalculate EWMA trend weights for all entries.

        Useful if alpha parameter changes or data is corrected.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID

        Returns:
            Number of entries updated
        """
        # Get all weight entries (sorted by date)
        entries = self.get_weight_entries(db, user_id)

        if not entries:
            return 0

        # Extract weights
        weights = [e.weight_lbs for e in entries]

        # Recalculate trends
        trend_weights = calculate_trend_weight(weights, alpha=self.alpha)

        # Update database
        for i, entry in enumerate(entries):
            entry.trend_weight_lbs = trend_weights[i]

        db.commit()

        return len(entries)

    def get_latest_weight(
        self,
        db: Session,
        user_id: str
    ) -> Optional[WeightEntry]:
        """
        Get most recent weight entry for a user.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID

        Returns:
            Latest WeightEntry or None
        """
        return db.query(WeightEntry)\
            .filter(WeightEntry.user_id == user_id)\
            .order_by(WeightEntry.date.desc())\
            .first()


# Singleton instance
_weight_service = None

def get_weight_service() -> WeightService:
    """
    Get singleton weight service instance.

    Returns:
        WeightService instance
    """
    global _weight_service
    if _weight_service is None:
        _weight_service = WeightService()
    return _weight_service
