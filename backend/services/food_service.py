"""
Food Service Layer - PostgreSQL-backed nutrition tracking.

Provides user-scoped database operations for nutrition tracking
using SQLAlchemy models with proper user_id authorization.
"""

from typing import List, Optional, Dict
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.database import FoodEntry


class FoodService:
    """
    Service layer for nutrition operations.

    Uses SQLAlchemy + PostgreSQL with user_id scoping on all queries.
    """

    def log_food_entry(
        self,
        db: Session,
        user_id: str,
        food_name: str,
        calories: float,
        protein_g: float,
        carbs_g: float,
        fat_g: float,
        serving_size: Optional[str] = None,
        serving_quantity: float = 1.0,
        log_date: Optional[str] = None,
        meal_type: Optional[str] = None,
        source: Optional[str] = None,
        barcode: Optional[str] = None,
        notes: Optional[str] = None
    ) -> FoodEntry:
        """
        Log a food entry for a user.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            food_name: Name of food
            calories: Calories per serving
            protein_g: Protein in grams
            carbs_g: Carbs in grams
            fat_g: Fat in grams
            serving_size: Serving size description
            serving_quantity: Number of servings
            log_date: Date (YYYY-MM-DD), defaults to today
            meal_type: "breakfast", "lunch", "dinner", "snack"
            source: Data source ("usda_fdc", "open_food_facts", "manual")
            barcode: Barcode/UPC (optional)
            notes: Optional notes

        Returns:
            FoodEntry object
        """
        if log_date is None:
            log_date = date.today().isoformat()

        entry = FoodEntry(
            user_id=user_id,
            date=log_date,
            food_name=food_name,
            serving_size=serving_size,
            serving_quantity=serving_quantity,
            calories=calories * serving_quantity,
            protein_g=protein_g * serving_quantity,
            carbs_g=carbs_g * serving_quantity,
            fat_g=fat_g * serving_quantity,
            meal_type=meal_type,
            source=source,
            barcode=barcode,
            notes=notes
        )

        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def get_daily_nutrition(
        self,
        db: Session,
        user_id: str,
        log_date: Optional[str] = None
    ) -> Dict:
        """
        Get nutrition summary for a specific date.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            log_date: Date (YYYY-MM-DD), defaults to today

        Returns:
            Dictionary with daily totals and entries by meal
        """
        if log_date is None:
            log_date = date.today().isoformat()

        entries = db.query(FoodEntry).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date == log_date
        ).order_by(FoodEntry.timestamp).all()

        total_calories = sum(e.calories for e in entries)
        total_protein = sum(e.protein_g for e in entries)
        total_carbs = sum(e.carbs_g for e in entries)
        total_fat = sum(e.fat_g for e in entries)

        # Group by meal type
        meals = {}
        for entry in entries:
            meal_type = entry.meal_type or "unspecified"
            if meal_type not in meals:
                meals[meal_type] = []
            meals[meal_type].append(entry)

        return {
            "date": log_date,
            "total_calories": total_calories,
            "total_protein_g": total_protein,
            "total_carbs_g": total_carbs,
            "total_fat_g": total_fat,
            "entry_count": len(entries),
            "meals": meals
        }

    def get_food_entries_by_date(
        self,
        db: Session,
        user_id: str,
        log_date: str
    ) -> List[FoodEntry]:
        """
        Get all food entries for a specific date.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            log_date: Date (YYYY-MM-DD)

        Returns:
            List of FoodEntry objects
        """
        return db.query(FoodEntry).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date == log_date
        ).order_by(FoodEntry.timestamp).all()

    def get_weekly_average(
        self,
        db: Session,
        user_id: str,
        end_date: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """
        Get weekly average nutrition (for adaptive TDEE).

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            end_date: End date (YYYY-MM-DD), defaults to today
            days: Number of days to average (default 7)

        Returns:
            Dictionary with average calories and macros
        """
        if end_date is None:
            end_date = date.today().isoformat()

        start_date = (date.fromisoformat(end_date) - timedelta(days=days - 1)).isoformat()

        # Get daily totals grouped by date
        daily_totals = db.query(
            FoodEntry.date,
            func.sum(FoodEntry.calories).label("daily_calories"),
            func.sum(FoodEntry.protein_g).label("daily_protein"),
            func.sum(FoodEntry.carbs_g).label("daily_carbs"),
            func.sum(FoodEntry.fat_g).label("daily_fat")
        ).filter(
            FoodEntry.user_id == user_id,
            FoodEntry.date >= start_date,
            FoodEntry.date <= end_date
        ).group_by(FoodEntry.date).all()

        if not daily_totals:
            return {
                "start_date": start_date,
                "end_date": end_date,
                "days_logged": 0,
                "days_requested": days,
                "avg_calories": 0,
                "avg_protein_g": 0,
                "avg_carbs_g": 0,
                "avg_fat_g": 0
            }

        avg_calories = sum(d.daily_calories for d in daily_totals) / len(daily_totals)
        avg_protein = sum(d.daily_protein for d in daily_totals) / len(daily_totals)
        avg_carbs = sum(d.daily_carbs for d in daily_totals) / len(daily_totals)
        avg_fat = sum(d.daily_fat for d in daily_totals) / len(daily_totals)

        return {
            "start_date": start_date,
            "end_date": end_date,
            "days_logged": len(daily_totals),
            "days_requested": days,
            "avg_calories": avg_calories,
            "avg_protein_g": avg_protein,
            "avg_carbs_g": avg_carbs,
            "avg_fat_g": avg_fat
        }

    def delete_entry(self, db: Session, user_id: str, entry_id: int) -> bool:
        """
        Delete a food entry (user-scoped).

        Args:
            db: SQLAlchemy database session
            user_id: User UUID
            entry_id: Food entry ID

        Returns:
            True if deleted, False if not found
        """
        entry = db.query(FoodEntry).filter(
            FoodEntry.id == entry_id,
            FoodEntry.user_id == user_id
        ).first()

        if not entry:
            return False

        db.delete(entry)
        db.commit()
        return True

    def copy_yesterday_meals(self, db: Session, user_id: str) -> int:
        """
        Copy all food entries from yesterday to today.

        Args:
            db: SQLAlchemy database session
            user_id: User UUID

        Returns:
            Number of entries copied
        """
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today = date.today().isoformat()

        yesterday_entries = self.get_food_entries_by_date(db, user_id, yesterday)

        copied_count = 0
        for entry in yesterday_entries:
            new_entry = FoodEntry(
                user_id=user_id,
                date=today,
                food_name=entry.food_name,
                serving_size=entry.serving_size,
                serving_quantity=entry.serving_quantity,
                calories=entry.calories,
                protein_g=entry.protein_g,
                carbs_g=entry.carbs_g,
                fat_g=entry.fat_g,
                meal_type=entry.meal_type,
                source=entry.source,
                barcode=entry.barcode,
                notes=entry.notes
            )
            db.add(new_entry)
            copied_count += 1

        db.commit()
        return copied_count


# Singleton instance
_food_service = None


def get_food_service() -> FoodService:
    """Get singleton food service instance."""
    global _food_service
    if _food_service is None:
        _food_service = FoodService()
    return _food_service
