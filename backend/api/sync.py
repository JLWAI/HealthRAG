"""
Sync Protocol API Endpoints.

Implements pull/push sync for mobile offline-first architecture:
- GET /api/sync/changes - Pull changes from server since last sync
- POST /api/sync/changes - Push local changes to server
- Conflict resolution: Last Write Wins (timestamp-based)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.schemas import TokenData
from models.database import (
    get_db,
    WorkoutSession,
    WorkoutSet,
    FoodEntry,
    WeightEntry,
    UserProfile
)
from api.auth import get_current_user

router = APIRouter()


@router.get("/changes", tags=["Sync"])
async def pull_changes(
    since: str = Query(..., description="ISO 8601 timestamp of last sync (e.g., '2025-01-05T12:00:00Z')"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pull all changes from server since last sync.

    Returns changes across all entities:
    - Workout sessions and sets
    - Food entries
    - Weight entries
    - Profile updates

    Mobile app should:
    1. Call this endpoint on app resume or manual sync
    2. Apply changes to local WatermelonDB
    3. Resolve conflicts using Last Write Wins (server timestamp > local timestamp)
    4. Update lastSyncTimestamp in AsyncStorage

    Args:
        since: ISO 8601 timestamp of last successful sync

    Returns:
        Dictionary with changes for each entity type

    Example Response:
        {
          "workout_sessions": [
            {
              "id": 1,
              "user_id": "uuid",
              "date": "2025-01-05",
              "workout_name": "Upper A",
              "notes": "Great session",
              "created_at": "2025-01-05T12:00:00Z",
              "updated_at": "2025-01-05T12:30:00Z"
            }
          ],
          "workout_sets": [...],
          "food_entries": [...],
          "weight_entries": [...],
          "profile_updates": [...],
          "sync_timestamp": "2025-01-05T13:00:00Z"
        }
    """
    try:
        # Parse the 'since' timestamp
        since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))

        changes: Dict[str, Any] = {
            "workout_sessions": [],
            "workout_sets": [],
            "food_entries": [],
            "weight_entries": [],
            "profile_updates": [],
            "sync_timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        # Pull workout sessions (updated after 'since')
        workout_sessions = db.query(WorkoutSession).filter(
            and_(
                WorkoutSession.user_id == current_user.user_id,
                or_(
                    WorkoutSession.created_at > since_dt,
                    WorkoutSession.updated_at > since_dt
                )
            )
        ).all()

        changes["workout_sessions"] = [
            {
                "id": ws.id,
                "user_id": ws.user_id,
                "date": ws.date,
                "workout_name": ws.workout_name,
                "notes": ws.notes,
                "created_at": ws.created_at.isoformat() + 'Z',
                "updated_at": (ws.updated_at or ws.created_at).isoformat() + 'Z'
            }
            for ws in workout_sessions
        ]

        # Pull workout sets for changed sessions
        if workout_sessions:
            session_ids = [ws.id for ws in workout_sessions]
            workout_sets = db.query(WorkoutSet).filter(
                WorkoutSet.session_id.in_(session_ids)
            ).all()

            changes["workout_sets"] = [
                {
                    "id": ws.id,
                    "session_id": ws.session_id,
                    "set_number": ws.set_number,
                    "exercise_name": ws.exercise_name,
                    "weight_lbs": ws.weight_lbs,
                    "reps_completed": ws.reps_completed,
                    "rir": ws.rir,
                    "notes": ws.notes,
                    "timestamp": ws.timestamp
                }
                for ws in workout_sets
            ]

        # Pull food entries
        food_entries = db.query(FoodEntry).filter(
            and_(
                FoodEntry.user_id == current_user.user_id,
                or_(
                    FoodEntry.created_at > since_dt,
                    FoodEntry.updated_at > since_dt
                )
            )
        ).all()

        changes["food_entries"] = [
            {
                "id": fe.id,
                "user_id": fe.user_id,
                "date": fe.date,
                "food_name": fe.food_name,
                "serving_size": fe.serving_size,
                "serving_quantity": fe.serving_quantity,
                "calories": fe.calories,
                "protein_g": fe.protein_g,
                "carbs_g": fe.carbs_g,
                "fat_g": fe.fat_g,
                "meal_type": fe.meal_type,
                "source": fe.source,
                "created_at": fe.created_at.isoformat() + 'Z',
                "updated_at": (fe.updated_at or fe.created_at).isoformat() + 'Z'
            }
            for fe in food_entries
        ]

        # Pull weight entries
        weight_entries = db.query(WeightEntry).filter(
            and_(
                WeightEntry.user_id == current_user.user_id,
                WeightEntry.created_at > since_dt
            )
        ).all()

        changes["weight_entries"] = [
            {
                "id": we.id,
                "user_id": we.user_id,
                "date": we.date,
                "weight_lbs": we.weight_lbs,
                "trend_weight_lbs": we.trend_weight_lbs,
                "notes": we.notes,
                "created_at": we.created_at.isoformat() + 'Z'
            }
            for we in weight_entries
        ]

        # Pull profile updates
        profile = db.query(UserProfile).filter(
            and_(
                UserProfile.id == current_user.user_id,
                UserProfile.updated_at > since_dt
            )
        ).first()

        if profile:
            changes["profile_updates"] = [{
                "id": profile.id,
                "email": profile.email,
                "name": profile.name,
                "age": profile.age,
                "sex": profile.sex,
                "height_inches": profile.height_inches,
                "current_weight_lbs": profile.current_weight_lbs,
                "goal_type": profile.goal_type,
                "target_weight_lbs": profile.target_weight_lbs,
                "training_experience": profile.training_experience,
                "equipment_access": profile.equipment_access,
                "bmr": profile.bmr,
                "tdee": profile.tdee,
                "target_calories": profile.target_calories,
                "target_protein_g": profile.target_protein_g,
                "target_carbs_g": profile.target_carbs_g,
                "target_fat_g": profile.target_fat_g,
                "updated_at": profile.updated_at.isoformat() + 'Z'
            }]

        return changes

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid timestamp format. Use ISO 8601 (e.g., '2025-01-05T12:00:00Z'): {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pull changes: {str(e)}"
        )


@router.post("/changes", tags=["Sync"])
async def push_changes(
    changes: Dict[str, List[Dict[str, Any]]],
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Push local changes to server.

    Conflict Resolution: Last Write Wins (LWW)
    - Compare timestamps: server updated_at vs. client updated_at
    - If server timestamp > client timestamp: Server wins, reject client change
    - If client timestamp > server timestamp: Client wins, update server
    - If timestamps equal: Server wins (tie-breaker)

    Mobile app should:
    1. Collect all local changes since last sync
    2. Send in batch to this endpoint
    3. Handle conflicts by accepting server version
    4. Update lastSyncTimestamp on success

    Args:
        changes: Dictionary with arrays of changes for each entity type

    Request Body Example:
        {
          "workout_sessions": [
            {
              "id": 1,
              "date": "2025-01-05",
              "workout_name": "Upper A",
              "notes": "Great session",
              "updated_at": "2025-01-05T12:30:00Z"
            }
          ],
          "food_entries": [...],
          "weight_entries": [...]
        }

    Returns:
        {
          "success": true,
          "conflicts": [],
          "sync_timestamp": "2025-01-05T13:00:00Z"
        }
    """
    try:
        conflicts = []

        # Process workout session updates
        for ws_data in changes.get("workout_sessions", []):
            session_id = ws_data.get("id")
            client_updated_at = datetime.fromisoformat(ws_data["updated_at"].replace('Z', '+00:00'))

            # Check for existing session
            existing = db.query(WorkoutSession).filter(
                and_(
                    WorkoutSession.id == session_id,
                    WorkoutSession.user_id == current_user.user_id
                )
            ).first()

            if existing:
                # Conflict check (Last Write Wins)
                server_updated_at = existing.updated_at or existing.created_at

                if server_updated_at > client_updated_at:
                    # Server wins - reject client change
                    conflicts.append({
                        "entity": "workout_session",
                        "id": session_id,
                        "reason": "Server version is newer",
                        "server_timestamp": server_updated_at.isoformat() + 'Z',
                        "client_timestamp": client_updated_at.isoformat() + 'Z'
                    })
                    continue

                # Client wins - update server
                existing.workout_name = ws_data.get("workout_name", existing.workout_name)
                existing.notes = ws_data.get("notes", existing.notes)
                existing.updated_at = client_updated_at
            else:
                # New session - create
                new_session = WorkoutSession(
                    id=session_id,
                    user_id=current_user.user_id,
                    date=ws_data["date"],
                    workout_name=ws_data["workout_name"],
                    notes=ws_data.get("notes"),
                    created_at=client_updated_at,
                    updated_at=client_updated_at
                )
                db.add(new_session)

        # Process food entry updates
        for fe_data in changes.get("food_entries", []):
            entry_id = fe_data.get("id")
            client_updated_at = datetime.fromisoformat(fe_data["updated_at"].replace('Z', '+00:00'))

            existing = db.query(FoodEntry).filter(
                and_(
                    FoodEntry.id == entry_id,
                    FoodEntry.user_id == current_user.user_id
                )
            ).first()

            if existing:
                server_updated_at = existing.updated_at or existing.created_at

                if server_updated_at > client_updated_at:
                    conflicts.append({
                        "entity": "food_entry",
                        "id": entry_id,
                        "reason": "Server version is newer",
                        "server_timestamp": server_updated_at.isoformat() + 'Z',
                        "client_timestamp": client_updated_at.isoformat() + 'Z'
                    })
                    continue

                # Client wins - update server
                existing.food_name = fe_data.get("food_name", existing.food_name)
                existing.serving_quantity = fe_data.get("serving_quantity", existing.serving_quantity)
                existing.calories = fe_data.get("calories", existing.calories)
                existing.protein_g = fe_data.get("protein_g", existing.protein_g)
                existing.carbs_g = fe_data.get("carbs_g", existing.carbs_g)
                existing.fat_g = fe_data.get("fat_g", existing.fat_g)
                existing.meal_type = fe_data.get("meal_type", existing.meal_type)
                existing.updated_at = client_updated_at
            else:
                # New entry - create
                new_entry = FoodEntry(
                    id=entry_id,
                    user_id=current_user.user_id,
                    date=fe_data["date"],
                    food_name=fe_data["food_name"],
                    serving_size=fe_data["serving_size"],
                    serving_quantity=fe_data["serving_quantity"],
                    calories=fe_data["calories"],
                    protein_g=fe_data["protein_g"],
                    carbs_g=fe_data["carbs_g"],
                    fat_g=fe_data["fat_g"],
                    meal_type=fe_data.get("meal_type", "other"),
                    source=fe_data.get("source", "manual"),
                    created_at=client_updated_at,
                    updated_at=client_updated_at
                )
                db.add(new_entry)

        # Process weight entry updates
        for we_data in changes.get("weight_entries", []):
            entry_id = we_data.get("id")
            client_created_at = datetime.fromisoformat(we_data["created_at"].replace('Z', '+00:00'))

            existing = db.query(WeightEntry).filter(
                and_(
                    WeightEntry.id == entry_id,
                    WeightEntry.user_id == current_user.user_id
                )
            ).first()

            if existing:
                # Weight entries are immutable - reject duplicates
                conflicts.append({
                    "entity": "weight_entry",
                    "id": entry_id,
                    "reason": "Entry already exists",
                    "server_timestamp": existing.created_at.isoformat() + 'Z',
                    "client_timestamp": client_created_at.isoformat() + 'Z'
                })
                continue
            else:
                # New entry - create (EWMA will be recalculated on server)
                new_entry = WeightEntry(
                    id=entry_id,
                    user_id=current_user.user_id,
                    date=we_data["date"],
                    weight_lbs=we_data["weight_lbs"],
                    notes=we_data.get("notes"),
                    created_at=client_created_at
                )
                db.add(new_entry)

        # Commit all changes
        db.commit()

        return {
            "success": True,
            "conflicts": conflicts,
            "conflicts_count": len(conflicts),
            "sync_timestamp": datetime.utcnow().isoformat() + 'Z'
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push changes: {str(e)}"
        )
