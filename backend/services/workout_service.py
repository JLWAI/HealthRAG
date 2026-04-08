"""
Workout Service Layer - PostgreSQL-backed workout tracking.

Provides user-scoped database operations for workout tracking
using SQLAlchemy models with proper user_id authorization.
"""

from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from models.database import WorkoutSession, WorkoutSet


class WorkoutService:
    """
    Service layer for workout operations.

    Uses SQLAlchemy + PostgreSQL with user_id scoping on all queries.
    """

    def create_workout_session(
        self,
        db: Session,
        user_id: str,
        workout_date: str,
        workout_name: str,
        sets: List[dict],
        notes: Optional[str] = None
    ) -> WorkoutSession:
        """
        Create a new workout session with sets.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            workout_date: Workout date (YYYY-MM-DD)
            workout_name: Name of workout (e.g., "Upper A", "Push Day")
            sets: List of set dicts with keys:
                - exercise_name (str)
                - weight_lbs (float)
                - reps_completed (int)
                - rir (int, optional)
                - notes (str, optional)
            notes: Session notes

        Returns:
            WorkoutSession object with sets
        """
        session = WorkoutSession(
            user_id=user_id,
            date=workout_date,
            workout_name=workout_name,
            notes=notes
        )
        db.add(session)
        db.flush()  # Get session ID for sets

        for i, s in enumerate(sets, start=1):
            workout_set = WorkoutSet(
                session_id=session.id,
                set_number=i,
                exercise_name=s["exercise_name"],
                weight_lbs=s["weight_lbs"],
                reps_completed=s["reps_completed"],
                rir=s.get("rir"),
                notes=s.get("notes")
            )
            db.add(workout_set)

        db.commit()
        db.refresh(session)
        return session

    def get_workout_session(
        self,
        db: Session,
        user_id: str,
        workout_id: int
    ) -> Optional[WorkoutSession]:
        """
        Retrieve a workout session by ID (user-scoped).

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            workout_id: Workout database ID

        Returns:
            WorkoutSession object or None if not found/not authorized
        """
        return db.query(WorkoutSession).filter(
            WorkoutSession.id == workout_id,
            WorkoutSession.user_id == user_id
        ).first()

    def get_workouts_by_date_range(
        self,
        db: Session,
        user_id: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> List[WorkoutSession]:
        """
        Get all workouts in a date range for a user.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today

        Returns:
            List of WorkoutSession objects
        """
        if end_date is None:
            end_date = date.today().isoformat()

        return db.query(WorkoutSession).filter(
            WorkoutSession.user_id == user_id,
            WorkoutSession.date >= start_date,
            WorkoutSession.date <= end_date
        ).order_by(WorkoutSession.date.desc()).all()

    def get_recent_workouts(
        self,
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> List[WorkoutSession]:
        """
        Get most recent workouts for a user.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            limit: Number of workouts to return

        Returns:
            List of WorkoutSession objects (most recent first)
        """
        return db.query(WorkoutSession).filter(
            WorkoutSession.user_id == user_id
        ).order_by(WorkoutSession.date.desc()).limit(limit).all()

    def delete_workout_session(
        self,
        db: Session,
        user_id: str,
        workout_id: int
    ) -> bool:
        """
        Delete a workout session and its sets (user-scoped).

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            workout_id: Workout database ID

        Returns:
            True if deleted, False if not found
        """
        session = db.query(WorkoutSession).filter(
            WorkoutSession.id == workout_id,
            WorkoutSession.user_id == user_id
        ).first()

        if not session:
            return False

        db.delete(session)  # Cascade deletes sets
        db.commit()
        return True


# Singleton instance
_workout_service = None


def get_workout_service() -> WorkoutService:
    """Get singleton workout service instance."""
    global _workout_service
    if _workout_service is None:
        _workout_service = WorkoutService()
    return _workout_service
