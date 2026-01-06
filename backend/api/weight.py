"""
Weight Tracking API Endpoints.

CRUD operations for weight tracking with EWMA trend calculation:
- POST /api/weight/entries - Log weight entry
- GET /api/weight/entries - Get weight entries
- GET /api/weight/trend - Get weight trend data (EWMA)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models.schemas import (
    WeightEntryCreate,
    WeightEntryResponse,
    WeightTrendResponse,
    TokenData
)
from models.database import get_db
from api.auth import get_current_user
from services.weight_service import get_weight_service, WeightService

router = APIRouter()


@router.post("/entries", response_model=WeightEntryResponse, status_code=status.HTTP_201_CREATED, tags=["Weight"])
async def log_weight_entry(
    request: WeightEntryCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    weight_service: WeightService = Depends(get_weight_service)
):
    """
    Log a weight entry with automatic EWMA trend calculation.

    Args:
        request: WeightEntryCreate with date, weight_lbs, notes

    Returns:
        WeightEntryResponse with weight and trend_weight_lbs (EWMA)

    Example:
        ```json
        {
          "date": "2025-01-05",
          "weight_lbs": 185.2,
          "notes": "Morning weigh-in"
        }
        ```

    Note:
        The trend_weight_lbs is calculated using EWMA with alpha=0.3
        (MacroFactor-style smoothing). This provides a smoothed trend line
        that reduces noise from daily fluctuations.
    """
    try:
        weight_entry = weight_service.create_weight_entry(
            db=db,
            user_id=current_user.user_id,
            weight_lbs=request.weight_lbs,
            entry_date=request.date,
            notes=request.notes
        )

        return WeightEntryResponse(
            id=weight_entry.id,
            user_id=weight_entry.user_id,
            date=weight_entry.date,
            weight_lbs=weight_entry.weight_lbs,
            trend_weight_lbs=weight_entry.trend_weight_lbs,
            notes=weight_entry.notes,
            created_at=weight_entry.created_at
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log weight: {str(e)}"
        )


@router.get("/entries", response_model=List[WeightEntryResponse], tags=["Weight"])
async def get_weight_entries(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(30, ge=1, le=365, description="Max results (default 30 days)"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    weight_service: WeightService = Depends(get_weight_service)
):
    """
    Get weight entries for current user.

    Query Parameters:
        - start_date: Filter by start date (YYYY-MM-DD)
        - end_date: Filter by end date (YYYY-MM-DD)
        - limit: Max results to return (1-365)

    Returns:
        List of WeightEntryResponse objects (ordered by date ascending)
    """
    try:
        entries = weight_service.get_weight_entries(
            db=db,
            user_id=current_user.user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        return [
            WeightEntryResponse(
                id=e.id,
                user_id=e.user_id,
                date=e.date,
                weight_lbs=e.weight_lbs,
                trend_weight_lbs=e.trend_weight_lbs,
                notes=e.notes,
                created_at=e.created_at
            )
            for e in entries
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve weight entries: {str(e)}"
        )


@router.get("/trend", response_model=WeightTrendResponse, tags=["Weight"])
async def get_weight_trend(
    days: int = Query(30, ge=7, le=365, description="Number of days to include (7-365)"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    weight_service: WeightService = Depends(get_weight_service)
):
    """
    Get weight trend data with EWMA smoothing.

    Query Parameters:
        - days: Number of days to include (default 30, range 7-365)

    Returns:
        WeightTrendResponse with:
        - entries: List of weight entries
        - ewma_alpha: Smoothing factor (0.3)
        - latest_trend: Most recent trend weight
        - weekly_change_lbs: Change over last 7 days
        - monthly_change_lbs: Change over last 30 days

    Note:
        The trend line uses EWMA (Exponentially Weighted Moving Average)
        with alpha=0.3, which provides optimal smoothing for daily weight
        fluctuations while remaining responsive to real changes.

        Formula: trend[i] = (0.3 × weight[i]) + (0.7 × trend[i-1])
    """
    try:
        trend_data = weight_service.get_weight_trend(
            db=db,
            user_id=current_user.user_id,
            days=days
        )

        # Get weight entries for response
        entries = weight_service.get_weight_entries(
            db=db,
            user_id=current_user.user_id,
            limit=days
        )

        entry_responses = [
            WeightEntryResponse(
                id=e.id,
                user_id=e.user_id,
                date=e.date,
                weight_lbs=e.weight_lbs,
                trend_weight_lbs=e.trend_weight_lbs,
                notes=e.notes,
                created_at=e.created_at
            )
            for e in entries
        ]

        return WeightTrendResponse(
            entries=entry_responses,
            ewma_alpha=0.3,
            latest_trend=trend_data.get("latest_trend"),
            weekly_change_lbs=trend_data.get("weekly_change"),
            monthly_change_lbs=trend_data.get("monthly_change")
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve weight trend: {str(e)}"
        )
