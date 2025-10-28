"""
Food Logging System for HealthRAG
Track daily food intake: calories, protein, carbs, fat

Designed to integrate with adaptive TDEE calculation (MacroFactor methodology)
Database supports future integration with USDA FDC and Open Food Facts
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass
class Food:
    """Food item with nutritional information"""
    food_id: Optional[int]
    name: str
    brand: Optional[str]
    serving_size: str  # "100g", "1 cup", "1 medium banana"
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    source: str = "user"  # "user", "usda", "off" (Open Food Facts)
    barcode: Optional[str] = None


@dataclass
class FoodEntry:
    """Single food log entry"""
    entry_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD
    food_id: int
    food_name: str  # Cached for display
    servings: float  # Number of servings consumed
    calories: float  # Total calories (servings × per-serving)
    protein_g: float
    carbs_g: float
    fat_g: float
    meal_type: Optional[str] = None  # "breakfast", "lunch", "dinner", "snack"
    notes: Optional[str] = None


@dataclass
class DailyNutrition:
    """Daily nutrition summary"""
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    entry_count: int
    meals: Dict[str, List[FoodEntry]]  # Grouped by meal_type


class FoodLogger:
    """
    Food logging system with SQLite backend.

    Features:
    - Track food intake with macronutrients
    - Quick-add from recent foods
    - Custom user foods
    - Daily nutrition summaries
    - Weekly/monthly averages (for adaptive TDEE)
    """

    def __init__(self, db_path: str = "data/food_log.db"):
        self.db_path = db_path
        self._init_database()
        self._add_starter_foods()

    def _init_database(self):
        """Create database tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Foods table (nutritional database)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT,
                serving_size TEXT NOT NULL,
                calories REAL NOT NULL,
                protein_g REAL NOT NULL,
                carbs_g REAL NOT NULL,
                fat_g REAL NOT NULL,
                source TEXT DEFAULT 'user',
                barcode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, brand, serving_size)
            )
        """)

        # Food log entries
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                food_id INTEGER NOT NULL,
                servings REAL NOT NULL,
                calories REAL NOT NULL,
                protein_g REAL NOT NULL,
                carbs_g REAL NOT NULL,
                fat_g REAL NOT NULL,
                meal_type TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (food_id) REFERENCES foods (id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_food_entries_date ON food_entries(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_foods_name ON foods(name)")

        conn.commit()
        conn.close()

    def _add_starter_foods(self):
        """Add common starter foods if database is empty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM foods")
        count = cursor.fetchone()[0]

        if count == 0:
            # Add common foods for quick start
            starter_foods = [
                # Proteins
                ("Chicken Breast", None, "100g", 165, 31, 0, 3.6, "user"),
                ("Salmon", None, "100g", 208, 20, 0, 13, "user"),
                ("Egg", None, "1 large", 78, 6.3, 0.6, 5.3, "user"),
                ("Greek Yogurt", "Plain", "1 cup (227g)", 100, 17, 6, 0.7, "user"),
                ("Protein Powder", "Whey", "1 scoop (30g)", 120, 24, 3, 1.5, "user"),

                # Carbs
                ("White Rice", "Cooked", "1 cup (158g)", 205, 4.2, 45, 0.4, "user"),
                ("Oatmeal", "Cooked", "1 cup (234g)", 166, 5.9, 28, 3.6, "user"),
                ("Banana", None, "1 medium (118g)", 105, 1.3, 27, 0.4, "user"),
                ("Sweet Potato", "Baked", "1 medium (114g)", 103, 2.3, 24, 0.2, "user"),
                ("Whole Wheat Bread", None, "1 slice (28g)", 80, 4, 14, 1, "user"),

                # Fats
                ("Almonds", None, "1 oz (28g)", 164, 6, 6, 14, "user"),
                ("Peanut Butter", None, "2 tbsp (32g)", 188, 8, 7, 16, "user"),
                ("Avocado", None, "1/2 medium (68g)", 114, 1.4, 6, 10.5, "user"),
                ("Olive Oil", None, "1 tbsp (14g)", 119, 0, 0, 13.5, "user"),

                # Mixed
                ("Apple", None, "1 medium (182g)", 95, 0.5, 25, 0.3, "user"),
                ("Broccoli", "Cooked", "1 cup (156g)", 55, 3.7, 11, 0.6, "user"),
            ]

            for food in starter_foods:
                cursor.execute("""
                    INSERT OR IGNORE INTO foods (name, brand, serving_size, calories, protein_g, carbs_g, fat_g, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, food)

            conn.commit()

        conn.close()

    def add_food(self, food: Food) -> int:
        """Add new food to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO foods (name, brand, serving_size, calories, protein_g, carbs_g, fat_g, source, barcode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                food.name,
                food.brand,
                food.serving_size,
                food.calories,
                food.protein_g,
                food.carbs_g,
                food.fat_g,
                food.source,
                food.barcode
            ))

            food_id = cursor.lastrowid
            conn.commit()
            return food_id

        except sqlite3.IntegrityError:
            # Food already exists
            cursor.execute("""
                SELECT id FROM foods
                WHERE name = ? AND brand IS ? AND serving_size = ?
            """, (food.name, food.brand, food.serving_size))
            return cursor.fetchone()[0]

        finally:
            conn.close()

    def search_foods(self, query: str, limit: int = 20) -> List[Food]:
        """Search foods by name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM foods
            WHERE name LIKE ? OR brand LIKE ?
            ORDER BY name
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_food(row) for row in rows]

    def get_food(self, food_id: int) -> Optional[Food]:
        """Get food by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM foods WHERE id = ?", (food_id,))
        row = cursor.fetchone()
        conn.close()

        return self._row_to_food(row) if row else None

    def log_food(
        self,
        food_id: int,
        servings: float,
        log_date: Optional[str] = None,
        meal_type: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Log food consumption.

        Args:
            food_id: ID of food from foods table
            servings: Number of servings consumed
            log_date: Date of consumption (defaults to today)
            meal_type: "breakfast", "lunch", "dinner", "snack"
            notes: Optional notes

        Returns:
            entry_id: ID of created food entry
        """
        if log_date is None:
            log_date = date.today().isoformat()

        # Get food details
        food = self.get_food(food_id)
        if not food:
            raise ValueError(f"Food ID {food_id} not found")

        # Calculate totals
        calories = food.calories * servings
        protein_g = food.protein_g * servings
        carbs_g = food.carbs_g * servings
        fat_g = food.fat_g * servings

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO food_entries (
                date, food_id, servings, calories, protein_g, carbs_g, fat_g, meal_type, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (log_date, food_id, servings, calories, protein_g, carbs_g, fat_g, meal_type, notes))

        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return entry_id

    def get_daily_nutrition(self, log_date: Optional[str] = None) -> DailyNutrition:
        """Get nutrition summary for a specific date"""
        if log_date is None:
            log_date = date.today().isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all entries for this date
        cursor.execute("""
            SELECT
                fe.*,
                f.name as food_name
            FROM food_entries fe
            JOIN foods f ON fe.food_id = f.id
            WHERE fe.date = ?
            ORDER BY fe.created_at
        """, (log_date,))

        rows = cursor.fetchall()
        conn.close()

        # Calculate totals
        total_calories = sum(row['calories'] for row in rows)
        total_protein = sum(row['protein_g'] for row in rows)
        total_carbs = sum(row['carbs_g'] for row in rows)
        total_fat = sum(row['fat_g'] for row in rows)

        # Group by meal type
        meals = {}
        for row in rows:
            meal_type = row['meal_type'] or 'unspecified'
            if meal_type not in meals:
                meals[meal_type] = []

            entry = FoodEntry(
                entry_id=row['id'],
                date=row['date'],
                food_id=row['food_id'],
                food_name=row['food_name'],
                servings=row['servings'],
                calories=row['calories'],
                protein_g=row['protein_g'],
                carbs_g=row['carbs_g'],
                fat_g=row['fat_g'],
                meal_type=row['meal_type'],
                notes=row['notes']
            )
            meals[meal_type].append(entry)

        return DailyNutrition(
            date=log_date,
            total_calories=total_calories,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fat_g=total_fat,
            entry_count=len(rows),
            meals=meals
        )

    def get_weekly_average(
        self,
        end_date: Optional[str] = None,
        days: int = 7
    ) -> Dict:
        """
        Get weekly average nutrition (for adaptive TDEE calculation).

        Args:
            end_date: End date (defaults to today)
            days: Number of days to average (default 7)

        Returns:
            Dictionary with average calories and macros
        """
        if end_date is None:
            end_date = date.today().isoformat()

        start_date = (date.fromisoformat(end_date) - timedelta(days=days-1)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                date,
                SUM(calories) as daily_calories,
                SUM(protein_g) as daily_protein,
                SUM(carbs_g) as daily_carbs,
                SUM(fat_g) as daily_fat
            FROM food_entries
            WHERE date BETWEEN ? AND ?
            GROUP BY date
        """, (start_date, end_date))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {
                'days_logged': 0,
                'avg_calories': 0,
                'avg_protein_g': 0,
                'avg_carbs_g': 0,
                'avg_fat_g': 0,
                'error': 'No food logged in this period'
            }

        avg_calories = sum(row[1] for row in rows) / len(rows)
        avg_protein = sum(row[2] for row in rows) / len(rows)
        avg_carbs = sum(row[3] for row in rows) / len(rows)
        avg_fat = sum(row[4] for row in rows) / len(rows)

        return {
            'start_date': start_date,
            'end_date': end_date,
            'days_logged': len(rows),
            'days_requested': days,
            'avg_calories': avg_calories,
            'avg_protein_g': avg_protein,
            'avg_carbs_g': avg_carbs,
            'avg_fat_g': avg_fat
        }

    def delete_entry(self, entry_id: int):
        """Delete food entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()

    def _row_to_food(self, row) -> Food:
        """Convert database row to Food object"""
        return Food(
            food_id=row['id'],
            name=row['name'],
            brand=row['brand'],
            serving_size=row['serving_size'],
            calories=row['calories'],
            protein_g=row['protein_g'],
            carbs_g=row['carbs_g'],
            fat_g=row['fat_g'],
            source=row['source'],
            barcode=row['barcode']
        )


if __name__ == "__main__":
    # Example usage and testing
    print("=== Food Logger Test ===\n")

    # Create logger
    logger = FoodLogger("data/test_food_log.db")

    # Test 1: Search foods
    print("TEST 1: Search for 'chicken'")
    print("=" * 60)
    results = logger.search_foods("chicken")
    for food in results:
        print(f"{food.name} - {food.serving_size}: {food.calories} cal, {food.protein_g}g protein")
    print()

    # Test 2: Log food
    print("TEST 2: Log today's meals")
    print("=" * 60)
    chicken = logger.search_foods("chicken")[0]
    rice = logger.search_foods("rice")[0]
    broccoli = logger.search_foods("broccoli")[0]

    logger.log_food(chicken.food_id, servings=2.0, meal_type="lunch")
    logger.log_food(rice.food_id, servings=1.5, meal_type="lunch")
    logger.log_food(broccoli.food_id, servings=1.0, meal_type="lunch")

    print(f"✅ Logged lunch: 2 servings chicken, 1.5 cups rice, 1 cup broccoli\n")

    # Test 3: Daily summary
    print("TEST 3: Daily nutrition summary")
    print("=" * 60)
    daily = logger.get_daily_nutrition()
    print(f"Date: {daily.date}")
    print(f"Total Calories: {daily.total_calories:.0f}")
    print(f"Protein: {daily.total_protein_g:.1f}g")
    print(f"Carbs: {daily.total_carbs_g:.1f}g")
    print(f"Fat: {daily.total_fat_g:.1f}g")
    print(f"Total Entries: {daily.entry_count}")
    print()

    # Test 4: Weekly average
    print("TEST 4: Weekly average nutrition")
    print("=" * 60)
    weekly = logger.get_weekly_average(days=7)
    if 'error' not in weekly:
        print(f"Days logged: {weekly['days_logged']}/{weekly['days_requested']}")
        print(f"Avg calories: {weekly['avg_calories']:.0f}")
        print(f"Avg protein: {weekly['avg_protein_g']:.1f}g")
    else:
        print(weekly['error'])
