"""
Meal Template API Endpoints.

CRUD operations for meal templates (one-click logging of multi-food meals):
- GET /api/templates - List all templates
- GET /api/templates/{id} - Get template by ID
- POST /api/templates - Create template from today's meal
- POST /api/templates/{id}/log - Log template (one-click)
- DELETE /api/templates/{id} - Delete template
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from models.schemas import (
    MealTemplateCreate,
    MealTemplateResponse,
    TemplateFoodItem,
    TemplateLogRequest,
    MessageResponse,
    TokenData
)
from api.auth import get_current_user
from services.food_service import get_food_service, FoodService

router = APIRouter()


@router.get("/", response_model=List[MealTemplateResponse], tags=["Meal Templates"])
async def list_templates(
    meal_type: Optional[str] = Query(None, description="Filter by meal type (breakfast, lunch, dinner, snack)"),
    sort_by: str = Query("recent", description="Sort by: recent, frequent, or name"),
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    List all meal templates.

    Query Parameters:
        - meal_type: Optional filter (breakfast, lunch, dinner, snack)
        - sort_by: "recent" (last used), "frequent" (use count), or "name"

    Returns:
        List of MealTemplateResponse objects with calculated totals
    """
    try:
        templates = food_service.list_templates(current_user.user_id, meal_type, sort_by)

        return [
            MealTemplateResponse(
                template_id=t.template_id,
                name=t.name,
                description=t.description,
                meal_type=t.meal_type,
                foods=[
                    TemplateFoodItem(
                        food_id=f.food_id,
                        food_name=f.food_name,
                        servings=f.servings,
                        serving_size=f.serving_size,
                        calories=f.calories,
                        protein_g=f.protein_g,
                        carbs_g=f.carbs_g,
                        fat_g=f.fat_g
                    )
                    for f in t.foods
                ],
                total_calories=t.total_calories,
                total_protein_g=t.total_protein_g,
                total_carbs_g=t.total_carbs_g,
                total_fat_g=t.total_fat_g,
                created_at=t.created_at,
                last_used=t.last_used,
                use_count=t.use_count
            )
            for t in templates
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/{template_id}", response_model=MealTemplateResponse, tags=["Meal Templates"])
async def get_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Get template by ID with all foods and calculated totals.

    Path Parameters:
        - template_id: Template ID

    Returns:
        MealTemplateResponse with all foods
    """
    try:
        template = food_service.get_template(current_user.user_id, template_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )

        return MealTemplateResponse(
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            meal_type=template.meal_type,
            foods=[
                TemplateFoodItem(
                    food_id=f.food_id,
                    food_name=f.food_name,
                    servings=f.servings,
                    serving_size=f.serving_size,
                    calories=f.calories,
                    protein_g=f.protein_g,
                    carbs_g=f.carbs_g,
                    fat_g=f.fat_g
                )
                for f in template.foods
            ],
            total_calories=template.total_calories,
            total_protein_g=template.total_protein_g,
            total_carbs_g=template.total_carbs_g,
            total_fat_g=template.total_fat_g,
            created_at=template.created_at,
            last_used=template.last_used,
            use_count=template.use_count
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


@router.post("/", response_model=MealTemplateResponse, status_code=status.HTTP_201_CREATED, tags=["Meal Templates"])
async def create_template(
    request: MealTemplateCreate,
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Create template from today's logged foods for a specific meal type.

    Example: If you logged 5 foods for breakfast today, create a "Morning Shake"
    template from those foods for one-click logging in the future.

    Request Body:
        - name: Template name (e.g., "Morning Shake")
        - meal_type: breakfast, lunch, dinner, or snack
        - description: Optional description

    Returns:
        MealTemplateResponse with created template
    """
    try:
        template_id = food_service.create_template_from_today(
            user_id=current_user.user_id,
            name=request.name,
            meal_type=request.meal_type,
            description=request.description
        )

        # Fetch the created template to return full response
        template = food_service.get_template(current_user.user_id, template_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Template created but could not be retrieved"
            )

        return MealTemplateResponse(
            template_id=template.template_id,
            name=template.name,
            description=template.description,
            meal_type=template.meal_type,
            foods=[
                TemplateFoodItem(
                    food_id=f.food_id,
                    food_name=f.food_name,
                    servings=f.servings,
                    serving_size=f.serving_size,
                    calories=f.calories,
                    protein_g=f.protein_g,
                    carbs_g=f.carbs_g,
                    fat_g=f.fat_g
                )
                for f in template.foods
            ],
            total_calories=template.total_calories,
            total_protein_g=template.total_protein_g,
            total_carbs_g=template.total_carbs_g,
            total_fat_g=template.total_fat_g,
            created_at=template.created_at,
            last_used=template.last_used,
            use_count=template.use_count
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.post("/{template_id}/log", response_model=MessageResponse, tags=["Meal Templates"])
async def log_template(
    template_id: int,
    multiplier: float = Query(1.0, gt=0, le=10, description="Multiply all servings (e.g., 0.5 for half portions)"),
    date: Optional[str] = Query(None, description="Date to log (YYYY-MM-DD), defaults to today"),
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Log all foods from template (one-click logging).

    This is the primary value of templates - log an entire multi-food meal
    with one click instead of adding each food individually.

    Path Parameters:
        - template_id: Template to log

    Query Parameters:
        - multiplier: Multiply all servings (default 1.0, e.g., 0.5 for half portions)
        - date: Optional date (YYYY-MM-DD), defaults to today

    Returns:
        MessageResponse with count of entries created
    """
    try:
        count = food_service.log_template(
            user_id=current_user.user_id,
            template_id=template_id,
            log_date=date,
            multiplier=multiplier
        )

        return MessageResponse(
            message="Template logged successfully",
            detail=f"Created {count} food entries"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log template: {str(e)}"
        )


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Meal Templates"])
async def delete_template(
    template_id: int,
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Delete a meal template.

    Path Parameters:
        - template_id: Template to delete

    Returns:
        204 No Content on success
    """
    try:
        deleted = food_service.delete_template(current_user.user_id, template_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )

        return

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete template: {str(e)}"
        )
