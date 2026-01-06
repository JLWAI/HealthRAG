"""
Workout Service Layer - Wraps src/workout_logger.py for API use.

Provides database operations for workout tracking with user-scoped access.
Integrates existing HealthRAG workout logging with FastAPI backend.
"""

import sys
from pathlib import Path
from typing import List, Optional
from datetime import date, timedelta

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from workout_logger import WorkoutLogger, WorkoutLog, WorkoutSet


class WorkoutService:
    """
    Service layer for workout operations.

    Wraps WorkoutLogger to provide user-scoped access and
    API-friendly interfaces for FastAPI endpoints.
    """

    def __init__(self, db_path: str = "data/workouts.db"):
        """
        Initialize workout service with database path.

        Args:
            db_path: Path to SQLite workout database
        """
        self.logger = WorkoutLogger(db_path)

    def create_workout_session(
        self,
        user_id: str,
        date: str,
        workout_name: str,
        sets: List[dict],
        duration_minutes: int = 60,
        overall_pump: int = 3,
        overall_soreness: int = 3,
        overall_difficulty: int = 3,
        notes: Optional[str] = None
    ) -> int:
        """
        Create a new workout session.

        Args:
            user_id: User UUID (for multi-user support)
            date: Workout date (YYYY-MM-DD)
            workout_name: Name of workout (e.g., "Upper A", "Push Day")
            sets: List of set dictionaries with keys:
                - exercise_name (str)
                - weight_lbs (float)
                - reps (int)
                - rir (int)
                - notes (str, optional)
            duration_minutes: Workout duration
            overall_pump: Pump rating 1-5
            overall_soreness: Soreness rating 1-5
            overall_difficulty: Difficulty rating 1-5
            notes: Session notes

        Returns:
            workout_id (int): Database ID of created workout
        """
        # Convert dict sets to WorkoutSet objects
        workout_sets = [
            WorkoutSet(
                exercise_name=s["exercise_name"],
                weight_lbs=s["weight_lbs"],
                reps=s["reps_completed"],
                rir=s.get("rir", 2),  # Default RIR = 2
                notes=s.get("notes")
            )
            for s in sets
        ]

        # Create WorkoutLog object
        workout = WorkoutLog(
            workout_id=None,
            date=date,
            workout_name=workout_name,
            sets=workout_sets,
            duration_minutes=duration_minutes,
            overall_pump=overall_pump,
            overall_soreness=overall_soreness,
            overall_difficulty=overall_difficulty,
            notes=notes,
            completed=True
        )

        # Log workout and return ID
        return self.logger.log_workout(workout)

    def get_workout_session(self, workout_id: int, user_id: str) -> Optional[WorkoutLog]:
        """
        Retrieve a workout session by ID.

        Args:
            workout_id: Workout database ID
            user_id: User UUID (for authorization)

        Returns:
            WorkoutLog object or None if not found
        """
        # TODO: Add user_id authorization check
        return self.logger.get_workout(workout_id)

    def get_workouts_by_date_range(
        self,
        user_id: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> List[WorkoutLog]:
        """
        Get all workouts in a date range for a user.

        Args:
            user_id: User UUID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD), defaults to today

        Returns:
            List of WorkoutLog objects
        """
        if end_date is None:
            end_date = date.today().isoformat()

        # TODO: Add user_id filtering in query
        return self.logger.get_workouts_by_date_range(start_date, end_date)

    def get_recent_workouts(self, user_id: str, limit: int = 10) -> List[WorkoutLog]:
        """
        Get most recent workouts for a user.

        Args:
            user_id: User UUID
            limit: Number of workouts to return

        Returns:
            List of WorkoutLog objects (most recent first)
        """
        # TODO: Add user_id filtering in query
        return self.logger.get_recent_workouts(limit)

    def delete_workout_session(self, workout_id: int, user_id: str) -> bool:
        """
        Delete a workout session.

        Args:
            workout_id: Workout database ID
            user_id: User UUID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        # TODO: Add user_id authorization check
        # TODO: Add delete method to WorkoutLogger
        # For now, return False (not implemented)
        return False


# Singleton instance
_workout_service = None

def get_workout_service() -> WorkoutService:
    """
    Get singleton workout service instance.

    Returns:
        WorkoutService instance
    """
    global _workout_service
    if _workout_service is None:
        _workout_service = WorkoutService()
    return _workout_service
