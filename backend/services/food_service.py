"""
Food Service Layer - Wraps src/food_logger.py for API use.

Provides database operations for nutrition tracking with user-scoped access.
Integrates existing HealthRAG food logging with FastAPI backend.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict
from datetime import date

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from food_logger import FoodLogger, Food, FoodEntry, DailyNutrition
from meal_templates import MealTemplateManager, MealTemplate


class FoodService:
    """
    Service layer for nutrition operations.

    Wraps FoodLogger to provide user-scoped access and
    API-friendly interfaces for FastAPI endpoints.
    """

    def __init__(self, db_path: str = "data/food_log.db"):
        """
        Initialize food service with database path.

        Args:
            db_path: Path to SQLite food log database
        """
        self.logger = FoodLogger(db_path)
        self.template_manager = MealTemplateManager(db_path, self.logger)

    def search_foods(
        self,
        query: str,
        limit: int = 20
    ) -> List[Food]:
        """
        Search for foods by name or brand.

        Args:
            query: Search query string
            limit: Maximum results to return

        Returns:
            List of Food objects matching query
        """
        return self.logger.search_foods(query, limit)

    def get_food(self, food_id: int) -> Optional[Food]:
        """
        Get food by ID.

        Args:
            food_id: Food database ID

        Returns:
            Food object or None if not found
        """
        return self.logger.get_food(food_id)

    def add_food(
        self,
        name: str,
        serving_size: str,
        calories: float,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
        brand: Optional[str] = None,
        source: str = "user",
        barcode: Optional[str] = None
    ) -> int:
        """
        Add a new food to the database.

        Args:
            name: Food name
            serving_size: Serving size description (e.g., "100g", "1 cup")
            calories: Calories per serving
            protein_g: Protein in grams per serving
            carbs_g: Carbs in grams per serving
            fat_g: Fat in grams per serving
            brand: Brand name (optional)
            source: Data source ("user", "usda", "off")
            barcode: Barcode/UPC (optional)

        Returns:
            food_id (int): Database ID of created/existing food
        """
        food = Food(
            food_id=None,
            name=name,
            brand=brand,
            serving_size=serving_size,
            calories=calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            source=source,
            barcode=barcode
        )

        return self.logger.add_food(food)

    def log_food_entry(
        self,
        user_id: str,
        food_id: int,
        servings: float,
        log_date: Optional[str] = None,
        meal_type: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Log a food entry for a user.

        Args:
            user_id: User UUID
            food_id: Food database ID
            servings: Number of servings consumed
            log_date: Date of consumption (YYYY-MM-DD), defaults to today
            meal_type: "breakfast", "lunch", "dinner", "snack"
            notes: Optional notes

        Returns:
            entry_id (int): Database ID of food entry
        """
        # TODO: Add user_id to food_entries table
        return self.logger.log_food(
            food_id=food_id,
            servings=servings,
            log_date=log_date,
            meal_type=meal_type,
            notes=notes
        )

    def get_daily_nutrition(
        self,
        user_id: str,
        log_date: Optional[str] = None
    ) -> DailyNutrition:
        """
        Get nutrition summary for a specific date.

        Args:
            user_id: User UUID
            log_date: Date (YYYY-MM-DD), defaults to today

        Returns:
            DailyNutrition object with totals and meal breakdown
        """
        # TODO: Add user_id filtering
        return self.logger.get_daily_nutrition(log_date)

    def get_food_entries_by_date(
        self,
        user_id: str,
        log_date: str
    ) -> List[FoodEntry]:
        """
        Get all food entries for a specific date.

        Args:
            user_id: User UUID
            log_date: Date (YYYY-MM-DD)

        Returns:
            List of FoodEntry objects
        """
        daily_nutrition = self.get_daily_nutrition(user_id, log_date)

        # Flatten meals dict into single list
        all_entries = []
        for entries in daily_nutrition.meals.values():
            all_entries.extend(entries)

        return all_entries

    def get_weekly_average(
        self,
        user_id: str,
        end_date: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """
        Get weekly average nutrition (for adaptive TDEE).

        Args:
            user_id: User UUID
            end_date: End date (YYYY-MM-DD), defaults to today
            days: Number of days to average (default 7)

        Returns:
            Dictionary with average calories and macros
        """
        # TODO: Add user_id filtering
        return self.logger.get_weekly_average(end_date, days)

    def copy_yesterday_meals(self, user_id: str) -> int:
        """
        Copy all food entries from yesterday to today.

        Args:
            user_id: User UUID

        Returns:
            Number of entries copied
        """
        yesterday = (date.today() - __import__('datetime').timedelta(days=1)).isoformat()
        today = date.today().isoformat()

        # Get yesterday's entries
        yesterday_entries = self.get_food_entries_by_date(user_id, yesterday)

        # Copy to today
        copied_count = 0
        for entry in yesterday_entries:
            self.log_food_entry(
                user_id=user_id,
                food_id=entry.food_id,
                servings=entry.servings,
                log_date=today,
                meal_type=entry.meal_type,
                notes=entry.notes
            )
            copied_count += 1

        return copied_count

    def delete_food_entry(self, user_id: str, entry_id: int) -> None:
        """
        Delete a food entry.

        Args:
            user_id: User UUID (for future multi-user support)
            entry_id: Food entry ID to delete

        Raises:
            ValueError: If entry doesn't exist
        """
        # Future: Add user ownership check
        self.logger.delete_entry(entry_id)

    def get_recent_foods(self, user_id: str, days: int = 14, limit: int = 10) -> List[Food]:
        """
        Get most frequently logged foods from recent days.

        Args:
            user_id: User UUID (for future multi-user support)
            days: Look back this many days (default 14)
            limit: Max foods to return (default 10)

        Returns:
            List of Food objects, ordered by frequency (most common first)
        """
        # Future: Add user_id filtering
        return self.logger.get_recent_foods(days, limit)

    # Meal Template Operations

    def list_templates(
        self,
        user_id: str,
        meal_type: Optional[str] = None,
        sort_by: str = "recent"
    ) -> List[MealTemplate]:
        """
        List meal templates, optionally filtered by meal type.

        Args:
            user_id: User UUID (for future multi-user support)
            meal_type: Filter by meal type (breakfast, lunch, dinner, snack)
            sort_by: "recent", "frequent", or "name"

        Returns:
            List of MealTemplate objects
        """
        # Future: Add user_id filtering
        return self.template_manager.list_templates(meal_type, sort_by)

    def get_template(self, user_id: str, template_id: int) -> Optional[MealTemplate]:
        """
        Get template by ID with all foods and calculated totals.

        Args:
            user_id: User UUID (for future multi-user support)
            template_id: Template ID

        Returns:
            MealTemplate or None if not found
        """
        # Future: Add user ownership check
        return self.template_manager.get_template(template_id)

    def create_template_from_today(
        self,
        user_id: str,
        name: str,
        meal_type: str,
        description: Optional[str] = None
    ) -> int:
        """
        Create template from today's logged foods for a specific meal type.

        Args:
            user_id: User UUID
            name: Template name
            meal_type: breakfast, lunch, dinner, or snack
            description: Optional description

        Returns:
            Template ID
        """
        today = date.today().isoformat()
        return self.template_manager.create_template_from_date(
            name=name,
            source_date=today,
            meal_type=meal_type,
            description=description
        )

    def log_template(
        self,
        user_id: str,
        template_id: int,
        log_date: Optional[str] = None,
        multiplier: float = 1.0
    ) -> int:
        """
        Log all foods from template (one-click logging).

        Args:
            user_id: User UUID (for future multi-user support)
            template_id: Template to log
            log_date: Date to log foods (defaults to today)
            multiplier: Multiply all servings (e.g., 0.5 for half portions)

        Returns:
            Number of food entries created
        """
        # Future: Add user ownership check
        return self.template_manager.log_template(template_id, log_date, multiplier)

    def delete_template(self, user_id: str, template_id: int) -> bool:
        """
        Delete a meal template.

        Args:
            user_id: User UUID (for future multi-user support)
            template_id: Template to delete

        Returns:
            True if deleted, False if not found
        """
        # Future: Add user ownership check
        return self.template_manager.delete_template(template_id)


# Singleton instance
_food_service = None

def get_food_service() -> FoodService:
    """
    Get singleton food service instance.

    Returns:
        FoodService instance
    """
    global _food_service
    if _food_service is None:
        _food_service = FoodService()
    return _food_service
