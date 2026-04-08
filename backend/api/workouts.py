"""
Workout API Endpoints.

CRUD operations for workout tracking:
- POST /api/workouts/sessions - Create workout session
- GET /api/workouts/sessions - Get workout sessions
- GET /api/workouts/sessions/{id} - Get specific session
- DELETE /api/workouts/sessions/{id} - Delete session
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from models.schemas import (
    WorkoutSessionCreate,
    WorkoutSessionResponse,
    WorkoutSetResponse,
    TokenData
)
from models.database import get_db
from api.auth import get_current_user
from services.workout_service import get_workout_service, WorkoutService

router = APIRouter()


@router.post("/sessions", response_model=WorkoutSessionResponse, status_code=status.HTTP_201_CREATED, tags=["Workouts"])
async def create_workout_session(
    request: WorkoutSessionCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Create a new workout session with sets.

    Args:
        request: WorkoutSessionCreate with date, workout_name, sets

    Returns:
        WorkoutSessionResponse with workout_id and all sets
    """
    try:
        session = workout_service.create_workout_session(
            db=db,
            user_id=current_user.user_id,
            workout_date=request.date,
            workout_name=request.workout_name or "Workout",
            sets=[s.dict() for s in request.sets],
            notes=request.notes
        )

        sets = [
            WorkoutSetResponse(
                id=s.id,
                session_id=session.id,
                set_number=s.set_number,
                exercise_name=s.exercise_name,
                weight_lbs=s.weight_lbs,
                reps_completed=s.reps_completed,
                rir=s.rir,
                notes=s.notes,
                timestamp=s.timestamp.isoformat() if s.timestamp else date.today().isoformat()
            )
            for s in session.sets
        ]

        return WorkoutSessionResponse(
            id=session.id,
            user_id=current_user.user_id,
            date=session.date,
            workout_name=session.workout_name,
            notes=session.notes,
            created_at=session.created_at.isoformat() if session.created_at else date.today().isoformat(),
            sets=sets
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workout: {str(e)}"
        )


@router.get("/sessions", response_model=List[WorkoutSessionResponse], tags=["Workouts"])
async def get_workout_sessions(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Get workout sessions for current user.

    Query Parameters:
        - start_date: Filter by start date (YYYY-MM-DD)
        - end_date: Filter by end date (YYYY-MM-DD)
        - limit: Max results to return (1-100)

    Returns:
        List of WorkoutSessionResponse objects
    """
    try:
        if start_date:
            workouts = workout_service.get_workouts_by_date_range(
                db=db,
                user_id=current_user.user_id,
                start_date=start_date,
                end_date=end_date
            )
        else:
            workouts = workout_service.get_recent_workouts(
                db=db,
                user_id=current_user.user_id,
                limit=limit
            )

        responses = []
        for workout in workouts:
            sets = [
                WorkoutSetResponse(
                    id=s.id,
                    session_id=workout.id,
                    set_number=s.set_number,
                    exercise_name=s.exercise_name,
                    weight_lbs=s.weight_lbs,
                    reps_completed=s.reps_completed,
                    rir=s.rir,
                    notes=s.notes,
                    timestamp=s.timestamp.isoformat() if s.timestamp else workout.date
                )
                for s in workout.sets
            ]

            responses.append(WorkoutSessionResponse(
                id=workout.id,
                user_id=current_user.user_id,
                date=workout.date,
                workout_name=workout.workout_name,
                notes=workout.notes,
                created_at=workout.created_at.isoformat() if workout.created_at else workout.date,
                sets=sets
            ))

        return responses

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workouts: {str(e)}"
        )


@router.get("/sessions/{workout_id}", response_model=WorkoutSessionResponse, tags=["Workouts"])
async def get_workout_session(
    workout_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Get a specific workout session by ID.

    Args:
        workout_id: Workout database ID

    Returns:
        WorkoutSessionResponse with all sets
    """
    workout = workout_service.get_workout_session(db, current_user.user_id, workout_id)

    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout {workout_id} not found"
        )

    sets = [
        WorkoutSetResponse(
            id=s.id,
            session_id=workout_id,
            set_number=s.set_number,
            exercise_name=s.exercise_name,
            weight_lbs=s.weight_lbs,
            reps_completed=s.reps_completed,
            rir=s.rir,
            notes=s.notes,
            timestamp=s.timestamp.isoformat() if s.timestamp else workout.date
        )
        for s in workout.sets
    ]

    return WorkoutSessionResponse(
        id=workout_id,
        user_id=current_user.user_id,
        date=workout.date,
        workout_name=workout.workout_name,
        notes=workout.notes,
        created_at=workout.created_at.isoformat() if workout.created_at else workout.date,
        sets=sets
    )


@router.delete("/sessions/{workout_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Workouts"])
async def delete_workout_session(
    workout_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    workout_service: WorkoutService = Depends(get_workout_service)
):
    """
    Delete a workout session.

    Args:
        workout_id: Workout database ID
    """
    deleted = workout_service.delete_workout_session(db, current_user.user_id, workout_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workout {workout_id} not found or already deleted"
        )

    return None
