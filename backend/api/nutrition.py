"""
Nutrition API Endpoints.

CRUD operations for food logging and nutrition tracking:
- POST /api/nutrition/foods - Log food entry
- GET /api/nutrition/foods - Get food entries by date
- GET /api/nutrition/daily-totals - Get daily macro totals
- GET /api/nutrition/search - Search foods database
- POST /api/nutrition/meals/copy-yesterday - Copy yesterday's meals
- GET /api/nutrition/search/usda - Search USDA FDC (400K foods)
- GET /api/nutrition/search/off/barcode - Lookup Open Food Facts by barcode
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import date
import sys
import os

# Add parent directory to path for importing existing HealthRAG modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from models.schemas import (
    FoodEntryCreate,
    FoodEntryResponse,
    DailyNutritionSummary,
    FoodSearchResult,
    MessageResponse,
    TokenData
)
from api.auth import get_current_user
from services.food_service import get_food_service, FoodService

# Import external food API clients
try:
    from src.food_api_fdc import FDCAPIClient
    FDC_AVAILABLE = True
except ImportError:
    FDC_AVAILABLE = False

try:
    from src.food_api_off import OFFAPIClient, OFFProduct
    OFF_AVAILABLE = True
except ImportError:
    OFF_AVAILABLE = False

router = APIRouter()


@router.post("/foods", response_model=FoodEntryResponse, status_code=status.HTTP_201_CREATED, tags=["Nutrition"])
async def log_food_entry(
    request: FoodEntryCreate,
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Log a food entry.

    Args:
        request: FoodEntryCreate with food_name, serving_size, macros

    Returns:
        FoodEntryResponse with logged food

    Example:
        ```json
        {
          "date": "2025-01-05",
          "food_name": "Chicken Breast",
          "serving_size": "6 oz",
          "serving_quantity": 1.0,
          "calories": 281,
          "protein_g": 52.8,
          "carbs_g": 0,
          "fat_g": 6.1,
          "meal_type": "lunch"
        }
        ```
    """
    try:
        # Add food to database if not exists
        food_id = food_service.add_food(
            name=request.food_name,
            serving_size=request.serving_size or "1 serving",
            calories=request.calories,
            protein_g=request.protein_g,
            carbs_g=request.carbs_g,
            fat_g=request.fat_g,
            source=request.source or "manual"
        )

        # Log food entry
        entry_id = food_service.log_food_entry(
            user_id=current_user.user_id,
            food_id=food_id,
            servings=request.serving_quantity,
            log_date=request.date,
            meal_type=request.meal_type,
            notes=request.notes
        )

        # Return response
        return FoodEntryResponse(
            id=entry_id,
            user_id=current_user.user_id,
            date=request.date,
            meal_type=request.meal_type,
            food_name=request.food_name,
            serving_size=request.serving_size,
            serving_quantity=request.serving_quantity,
            calories=request.calories * request.serving_quantity,
            protein_g=request.protein_g * request.serving_quantity,
            carbs_g=request.carbs_g * request.serving_quantity,
            fat_g=request.fat_g * request.serving_quantity,
            fiber_g=request.fiber_g,
            sugar_g=request.sugar_g,
            sodium_mg=request.sodium_mg,
            barcode=request.barcode,
            source=request.source,
            notes=request.notes,
            timestamp=date.today().isoformat()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log food: {str(e)}"
        )


@router.get("/foods", response_model=List[FoodEntryResponse], tags=["Nutrition"])
async def get_food_entries(
    log_date: str = Query(..., description="Date (YYYY-MM-DD)"),
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Get all food entries for a specific date.

    Query Parameters:
        - log_date: Date to retrieve (YYYY-MM-DD)

    Returns:
        List of FoodEntryResponse objects
    """
    try:
        entries = food_service.get_food_entries_by_date(current_user.user_id, log_date)

        return [
            FoodEntryResponse(
                id=e.entry_id or 0,
                user_id=current_user.user_id,
                date=e.date,
                meal_type=e.meal_type,
                food_name=e.food_name,
                serving_size="",  # TODO: Get from food table
                serving_quantity=e.servings,
                calories=e.calories,
                protein_g=e.protein_g,
                carbs_g=e.carbs_g,
                fat_g=e.fat_g,
                timestamp=e.date
            )
            for e in entries
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve food entries: {str(e)}"
        )


@router.get("/daily-totals", response_model=DailyNutritionSummary, tags=["Nutrition"])
async def get_daily_nutrition_totals(
    log_date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Get daily nutrition totals and meal breakdown.

    Query Parameters:
        - log_date: Date to retrieve (YYYY-MM-DD), defaults to today

    Returns:
        DailyNutritionSummary with total macros and entries by meal
    """
    try:
        daily_nutrition = food_service.get_daily_nutrition(current_user.user_id, log_date)

        # Convert to response format
        all_entries = []
        for entries in daily_nutrition.meals.values():
            for e in entries:
                all_entries.append(FoodEntryResponse(
                    id=e.entry_id or 0,
                    user_id=current_user.user_id,
                    date=e.date,
                    meal_type=e.meal_type,
                    food_name=e.food_name,
                    serving_size="",  # TODO: Get from food table
                    serving_quantity=e.servings,
                    calories=e.calories,
                    protein_g=e.protein_g,
                    carbs_g=e.carbs_g,
                    fat_g=e.fat_g,
                    timestamp=e.date
                ))

        return DailyNutritionSummary(
            date=daily_nutrition.date,
            total_calories=daily_nutrition.total_calories,
            total_protein_g=daily_nutrition.total_protein_g,
            total_carbs_g=daily_nutrition.total_carbs_g,
            total_fat_g=daily_nutrition.total_fat_g,
            entry_count=daily_nutrition.entry_count,
            entries=all_entries
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve daily nutrition: {str(e)}"
        )


@router.get("/search", response_model=List[FoodSearchResult], tags=["Nutrition"])
async def search_foods(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Search for foods in database.

    Query Parameters:
        - q: Search query (min 2 characters)
        - limit: Max results (1-100)

    Returns:
        List of FoodSearchResult objects
    """
    try:
        foods = food_service.search_foods(q, limit)

        return [
            FoodSearchResult(
                food_name=f.name,
                serving_size=f.serving_size,
                calories=f.calories,
                protein_g=f.protein_g,
                carbs_g=f.carbs_g,
                fat_g=f.fat_g,
                source=f.source,
                external_id=str(f.food_id) if f.food_id else None
            )
            for f in foods
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search foods: {str(e)}"
        )


@router.post("/meals/copy-yesterday", response_model=MessageResponse, tags=["Nutrition"])
async def copy_yesterday_meals(
    current_user: TokenData = Depends(get_current_user),
    food_service: FoodService = Depends(get_food_service)
):
    """
    Copy all food entries from yesterday to today.

    Returns:
        MessageResponse with count of entries copied
    """
    try:
        count = food_service.copy_yesterday_meals(current_user.user_id)

        return MessageResponse(
            message="Yesterday's meals copied successfully",
            detail=f"Copied {count} food entries to today"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to copy meals: {str(e)}"
        )


@router.get("/search/usda", response_model=List[FoodSearchResult], tags=["Nutrition - External APIs"])
async def search_usda_fdc(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    data_type: Optional[str] = Query(None, description="Filter by data type: Foundation, SR Legacy, Branded"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Search USDA FoodData Central API (400K foods).

    **Requires**: USDA_FDC_API_KEY environment variable
    **Get API Key**: https://fdc.nal.usda.gov/api-key-signup (free)

    Query Parameters:
        - q: Search query (min 2 characters)
        - limit: Max results (1-100)
        - data_type: Optional filter ("Foundation", "SR Legacy", "Branded")

    Returns:
        List of FoodSearchResult objects from USDA database

    Example:
        GET /api/nutrition/search/usda?q=chicken%20breast&limit=10
    """
    if not FDC_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="USDA FDC integration not available. Install required dependencies."
        )

    try:
        # Initialize FDC client (will check for API key)
        fdc_client = FDCAPIClient()

        # Parse data_type filter
        data_type_filter = None
        if data_type:
            data_type_filter = [data_type]

        # Search USDA FDC
        fdc_foods = fdc_client.search_and_parse(q, limit=limit, data_type=data_type_filter)

        # Convert to FoodSearchResult format
        results = []
        for food in fdc_foods:
            # FDC uses per-100g values, convert to serving if available
            serving_desc = food.household_serving or f"{food.serving_size or 100}g"

            results.append(FoodSearchResult(
                food_name=food.description,
                brand=food.brand_name,
                serving_size=serving_desc,
                calories=food.calories,
                protein_g=food.protein_g,
                carbs_g=food.carbs_g,
                fat_g=food.fat_g,
                fiber_g=food.fiber_g,
                sugar_g=food.sugar_g,
                sodium_mg=food.sodium_mg,
                source="usda_fdc",
                external_id=str(food.fdc_id),
                barcode=food.gtin_upc
            ))

        return results

    except ValueError as e:
        # API key missing or invalid
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"USDA FDC API unavailable: {str(e)}. Add USDA_FDC_API_KEY to environment."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"USDA FDC search failed: {str(e)}"
        )


@router.get("/search/off/barcode/{barcode}", response_model=FoodSearchResult, tags=["Nutrition - External APIs"])
async def lookup_barcode_off(
    barcode: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Lookup product by barcode in Open Food Facts (2.8M products).

    **No API key required** - Free, open database

    Path Parameters:
        - barcode: UPC/EAN barcode (e.g., "737628064502")

    Returns:
        FoodSearchResult if found, 404 if not found

    Example:
        GET /api/nutrition/search/off/barcode/737628064502
    """
    if not OFF_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Open Food Facts integration not available. Install required dependencies."
        )

    try:
        # Initialize OFF client (no API key needed)
        off_client = OFFAPIClient()

        # Lookup barcode
        product = off_client.lookup_barcode(barcode)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with barcode '{barcode}' not found in Open Food Facts database"
            )

        # Convert to FoodSearchResult format
        result = FoodSearchResult(
            food_name=product.product_name,
            brand=product.brands,
            serving_size=product.serving_size or "100g",
            calories=product.calories,
            protein_g=product.protein_g,
            carbs_g=product.carbs_g,
            fat_g=product.fat_g,
            fiber_g=product.fiber_g,
            sugar_g=product.sugar_g,
            sodium_mg=product.sodium_mg,
            source="open_food_facts",
            external_id=product.barcode,
            barcode=product.barcode
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Open Food Facts lookup failed: {str(e)}"
        )


@router.get("/search/off", response_model=List[FoodSearchResult], tags=["Nutrition - External APIs"])
async def search_open_food_facts(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Search Open Food Facts database (2.8M products).

    **No API key required** - Free, open database

    Query Parameters:
        - q: Search query (min 2 characters)
        - limit: Max results (1-100)

    Returns:
        List of FoodSearchResult objects from Open Food Facts

    Example:
        GET /api/nutrition/search/off?q=greek%20yogurt&limit=10
    """
    if not OFF_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Open Food Facts integration not available. Install required dependencies."
        )

    try:
        # Initialize OFF client (no API key needed)
        off_client = OFFAPIClient()

        # Search products
        products = off_client.search_and_parse(q, limit=limit)

        # Convert to FoodSearchResult format
        results = []
        for product in products:
            results.append(FoodSearchResult(
                food_name=product.product_name,
                brand=product.brands,
                serving_size=product.serving_size or "100g",
                calories=product.calories,
                protein_g=product.protein_g,
                carbs_g=product.carbs_g,
                fat_g=product.fat_g,
                fiber_g=product.fiber_g,
                sugar_g=product.sugar_g,
                sodium_mg=product.sodium_mg,
                source="open_food_facts",
                external_id=product.barcode,
                barcode=product.barcode
            ))

        return results

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Open Food Facts search failed: {str(e)}"
        )
