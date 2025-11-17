"""
Meal Templates System

Enables one-click logging of frequently eaten multi-food meals.
Perfect for meal prep scenarios where you eat the same combinations repeatedly.

Example:
    "Morning Shake" template with 5 ingredients → Log entire meal in 1 click
    Saves 2-3 minutes/day vs manually adding each food.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import sqlite3
from datetime import datetime
from pathlib import Path

from food_logger import FoodLogger, Food


@dataclass
class TemplateFoodItem:
    """Single food item within a meal template"""
    food_id: int
    food_name: str  # Denormalized for display
    servings: float
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


@dataclass
class MealTemplate:
    """Complete meal template with multiple foods"""
    template_id: Optional[int]
    name: str
    description: Optional[str]
    meal_type: str  # breakfast, lunch, dinner, snack
    foods: List[TemplateFoodItem]

    # Calculated totals
    total_calories: float = 0
    total_protein_g: float = 0
    total_carbs_g: float = 0
    total_fat_g: float = 0

    # Metadata
    created_at: Optional[str] = None
    last_used: Optional[str] = None
    use_count: int = 0

    def calculate_totals(self):
        """Calculate macro totals from all foods"""
        self.total_calories = sum(f.calories * f.servings for f in self.foods)
        self.total_protein_g = sum(f.protein_g * f.servings for f in self.foods)
        self.total_carbs_g = sum(f.carbs_g * f.servings for f in self.foods)
        self.total_fat_g = sum(f.fat_g * f.servings for f in self.foods)


class MealTemplateManager:
    """
    Manages meal templates for quick logging.

    Features:
    - Create templates from combinations of foods
    - One-click logging (copies all foods to food_entries)
    - Edit templates (add/remove foods, adjust servings)
    - Track usage frequency
    - Auto-sort by recent usage

    Database Schema:
        meal_templates:
            id, name, description, meal_type, created_at, last_used, use_count

        template_foods:
            id, template_id, food_id, servings, created_at
    """

    def __init__(self, db_path: str, food_logger: FoodLogger):
        """
        Initialize meal template manager.

        Args:
            db_path: Path to SQLite database
            food_logger: FoodLogger instance for food operations
        """
        self.db_path = Path(db_path)
        self.food_logger = food_logger
        self._init_database()

    def _init_database(self):
        """Create meal template tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Meal templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meal_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                meal_type TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used TEXT,
                use_count INTEGER DEFAULT 0,
                UNIQUE(name)
            )
        """)

        # Template foods junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                food_id INTEGER NOT NULL,
                servings REAL NOT NULL DEFAULT 1.0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES meal_templates(id) ON DELETE CASCADE,
                FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE CASCADE,
                UNIQUE(template_id, food_id)
            )
        """)

        # Index for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_template_foods_template_id
            ON template_foods(template_id)
        """)

        conn.commit()
        conn.close()

    def create_template(
        self,
        name: str,
        foods_with_servings: List[Tuple[int, float]],  # [(food_id, servings), ...]
        meal_type: str,
        description: Optional[str] = None
    ) -> int:
        """
        Create a new meal template.

        Args:
            name: Template name (e.g., "Morning Shake")
            foods_with_servings: List of (food_id, servings) tuples
            meal_type: breakfast, lunch, dinner, snack
            description: Optional description

        Returns:
            template_id

        Example:
            template_id = manager.create_template(
                name="Morning Shake",
                foods_with_servings=[
                    (protein_powder_id, 2.0),  # 2 scoops
                    (banana_id, 0.5),          # 1/2 banana
                    (yogurt_id, 1.0),          # 1 cup
                    (creatine_id, 1.0)         # 5g
                ],
                meal_type="breakfast",
                description="Post-workout protein shake"
            )
        """
        if not foods_with_servings:
            raise ValueError("Template must contain at least one food")

        # Validate all foods exist
        for food_id, _ in foods_with_servings:
            food = self.food_logger.get_food(food_id)
            if not food:
                raise ValueError(f"Food ID {food_id} not found")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Create template
            cursor.execute("""
                INSERT INTO meal_templates (name, description, meal_type, created_at)
                VALUES (?, ?, ?, ?)
            """, (name, description, meal_type, datetime.now().isoformat()))

            template_id = cursor.lastrowid

            # Add foods to template
            for food_id, servings in foods_with_servings:
                cursor.execute("""
                    INSERT INTO template_foods (template_id, food_id, servings, created_at)
                    VALUES (?, ?, ?, ?)
                """, (template_id, food_id, servings, datetime.now().isoformat()))

            conn.commit()
            return template_id

        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint failed: meal_templates.name" in str(e):
                raise ValueError(f"Template '{name}' already exists")
            raise
        finally:
            conn.close()

    def get_template(self, template_id: int) -> Optional[MealTemplate]:
        """
        Get template by ID with all foods and calculated totals.

        Returns:
            MealTemplate or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get template metadata
        cursor.execute("""
            SELECT id, name, description, meal_type, created_at, last_used, use_count
            FROM meal_templates
            WHERE id = ?
        """, (template_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        template_id, name, description, meal_type, created_at, last_used, use_count = row

        # Get all foods in template
        cursor.execute("""
            SELECT
                f.id,
                f.name,
                tf.servings,
                f.serving_size,
                f.calories,
                f.protein_g,
                f.carbs_g,
                f.fat_g
            FROM template_foods tf
            JOIN foods f ON tf.food_id = f.id
            WHERE tf.template_id = ?
            ORDER BY tf.created_at
        """, (template_id,))

        foods = []
        for row in cursor.fetchall():
            foods.append(TemplateFoodItem(
                food_id=row[0],
                food_name=row[1],
                servings=row[2],
                serving_size=row[3],
                calories=row[4],
                protein_g=row[5],
                carbs_g=row[6],
                fat_g=row[7]
            ))

        conn.close()

        # Build template object
        template = MealTemplate(
            template_id=template_id,
            name=name,
            description=description,
            meal_type=meal_type,
            foods=foods,
            created_at=created_at,
            last_used=last_used,
            use_count=use_count
        )

        template.calculate_totals()
        return template

    def list_templates(
        self,
        meal_type: Optional[str] = None,
        sort_by: str = "recent"  # "recent", "frequent", "name"
    ) -> List[MealTemplate]:
        """
        List all templates, optionally filtered by meal type.

        Args:
            meal_type: Filter by meal type (breakfast, lunch, etc.)
            sort_by: "recent" (last_used), "frequent" (use_count), "name"

        Returns:
            List of MealTemplate objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build query
        query = "SELECT id FROM meal_templates"
        params = []

        if meal_type:
            query += " WHERE meal_type = ?"
            params.append(meal_type)

        # Sort order
        if sort_by == "recent":
            query += " ORDER BY last_used DESC NULLS LAST, created_at DESC"
        elif sort_by == "frequent":
            query += " ORDER BY use_count DESC, last_used DESC"
        else:  # name
            query += " ORDER BY name"

        cursor.execute(query, params)
        template_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Load full template objects
        templates = []
        for template_id in template_ids:
            template = self.get_template(template_id)
            if template:
                templates.append(template)

        return templates

    def log_template(
        self,
        template_id: int,
        date: Optional[str] = None,
        multiplier: float = 1.0
    ) -> int:
        """
        Log all foods from template as individual entries.

        This is the "one-click" logging feature - copies all template foods
        to food_entries for the specified date.

        Args:
            template_id: Template to log
            date: Date to log for (YYYY-MM-DD), defaults to today
            multiplier: Scale all servings (e.g., 0.5 for half portion)

        Returns:
            Number of entries created

        Example:
            # Log "Morning Shake" template
            count = manager.log_template(template_id=1)
            # Creates 5 food_entries (one per ingredient)
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # Log each food in template
        entries_created = 0
        for food in template.foods:
            self.food_logger.log_food(
                food_id=food.food_id,
                servings=food.servings * multiplier,
                log_date=date,
                meal_type=template.meal_type
            )
            entries_created += 1

        # Update template usage stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE meal_templates
            SET last_used = ?, use_count = use_count + 1
            WHERE id = ?
        """, (datetime.now().isoformat(), template_id))
        conn.commit()
        conn.close()

        return entries_created

    def update_template(
        self,
        template_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        meal_type: Optional[str] = None,
        foods_with_servings: Optional[List[Tuple[int, float]]] = None
    ) -> bool:
        """
        Update template metadata or foods.

        Args:
            template_id: Template to update
            name: New name (optional)
            description: New description (optional)
            meal_type: New meal type (optional)
            foods_with_servings: Replace all foods (optional)

        Returns:
            True if updated, False if template not found
        """
        template = self.get_template(template_id)
        if not template:
            return False

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Update metadata
            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if meal_type is not None:
                updates.append("meal_type = ?")
                params.append(meal_type)

            if updates:
                params.append(template_id)
                cursor.execute(f"""
                    UPDATE meal_templates
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)

            # Update foods if provided
            if foods_with_servings is not None:
                # Delete existing foods
                cursor.execute("DELETE FROM template_foods WHERE template_id = ?", (template_id,))

                # Add new foods
                for food_id, servings in foods_with_servings:
                    cursor.execute("""
                        INSERT INTO template_foods (template_id, food_id, servings, created_at)
                        VALUES (?, ?, ?, ?)
                    """, (template_id, food_id, servings, datetime.now().isoformat()))

            conn.commit()
            return True

        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint failed: meal_templates.name" in str(e):
                raise ValueError(f"Template name '{name}' already exists")
            raise
        finally:
            conn.close()

    def delete_template(self, template_id: int) -> bool:
        """
        Delete a meal template.

        Args:
            template_id: Template to delete

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM meal_templates WHERE id = ?", (template_id,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def create_template_from_date(
        self,
        name: str,
        source_date: str,
        meal_type: str,
        description: Optional[str] = None
    ) -> int:
        """
        Create template from all foods logged on a specific date/meal.

        Convenience method for turning a day's meals into a reusable template.

        Args:
            name: Template name
            source_date: Date to copy from (YYYY-MM-DD)
            meal_type: Which meal to copy (breakfast, lunch, etc.)
            description: Optional description

        Returns:
            template_id

        Example:
            # Turn Monday's breakfast into a template
            template_id = manager.create_template_from_date(
                name="Weekday Breakfast",
                source_date="2025-01-13",
                meal_type="breakfast"
            )
        """
        # Get all entries for that date/meal
        daily_nutrition = self.food_logger.get_daily_nutrition(source_date)

        # Filter by meal type and extract (food_id, servings)
        foods_with_servings = []
        if meal_type in daily_nutrition.meals:
            foods_with_servings = [
                (entry.food_id, entry.servings)
                for entry in daily_nutrition.meals[meal_type]
            ]

        if not foods_with_servings:
            raise ValueError(f"No entries found for {source_date} {meal_type}")

        return self.create_template(
            name=name,
            foods_with_servings=foods_with_servings,
            meal_type=meal_type,
            description=description
        )


if __name__ == "__main__":
    # Test the meal template system
    print("=== Meal Templates System Test ===\n")

    # Initialize
    food_logger = FoodLogger("data/test_food_log.db")
    manager = MealTemplateManager("data/test_food_log.db", food_logger)

    # Create some test foods if they don't exist
    print("Setting up test foods...")

    # Protein powder
    protein_powder = Food(
        food_id=None,
        name="Whey Protein Powder",
        brand="Optimum Nutrition",
        serving_size="1 scoop (30g)",
        calories=120,
        protein_g=24,
        carbs_g=3,
        fat_g=1,
        source="manual"
    )
    pp_id = food_logger.add_food(protein_powder)

    # Banana
    banana = Food(
        food_id=None,
        name="Banana",
        brand=None,
        serving_size="1 medium (118g)",
        calories=105,
        protein_g=1,
        carbs_g=27,
        fat_g=0.4,
        source="fdc"
    )
    banana_id = food_logger.add_food(banana)

    # Greek yogurt
    yogurt = Food(
        food_id=None,
        name="Non-Fat Greek Yogurt",
        brand="Fage",
        serving_size="1 cup (227g)",
        calories=100,
        protein_g=17,
        carbs_g=7,
        fat_g=0,
        source="manual"
    )
    yogurt_id = food_logger.add_food(yogurt)

    # Creatine
    creatine = Food(
        food_id=None,
        name="Creatine Monohydrate",
        brand="",
        serving_size="5g",
        calories=0,
        protein_g=0,
        carbs_g=0,
        fat_g=0,
        source="manual"
    )
    creatine_id = food_logger.add_food(creatine)

    print(f"✅ Created test foods (IDs: {pp_id}, {banana_id}, {yogurt_id}, {creatine_id})\n")

    # Test 1: Create template
    print("TEST 1: Create 'Morning Shake' template")
    print("=" * 60)

    template_id = manager.create_template(
        name="Morning Shake",
        foods_with_servings=[
            (pp_id, 2.0),        # 2 scoops protein powder
            (banana_id, 0.5),    # 1/2 banana
            (yogurt_id, 1.0),    # 1 cup yogurt
            (creatine_id, 1.0)   # 5g creatine
        ],
        meal_type="breakfast",
        description="Post-workout protein shake"
    )

    print(f"✅ Created template ID: {template_id}\n")

    # Test 2: Load template and display
    print("TEST 2: Load template and show details")
    print("=" * 60)

    template = manager.get_template(template_id)
    print(f"Template: {template.name}")
    print(f"Type: {template.meal_type}")
    print(f"Description: {template.description}")
    print(f"\nIngredients:")
    for food in template.foods:
        print(f"  - {food.servings}x {food.food_name} ({food.serving_size})")
        print(f"    {food.calories * food.servings:.0f} cal, {food.protein_g * food.servings:.1f}g P")

    print(f"\nTOTALS:")
    print(f"  Calories: {template.total_calories:.0f}")
    print(f"  Protein: {template.total_protein_g:.1f}g")
    print(f"  Carbs: {template.total_carbs_g:.1f}g")
    print(f"  Fat: {template.total_fat_g:.1f}g")
    print()

    # Test 3: Log template (one-click)
    print("TEST 3: One-click log template for today")
    print("=" * 60)

    entries_created = manager.log_template(template_id)
    print(f"✅ Created {entries_created} food entries for breakfast")

    # Verify entries were created
    today = datetime.now().strftime("%Y-%m-%d")
    daily_nutrition = food_logger.get_daily_nutrition(today)
    breakfast_entries = daily_nutrition.meals.get("breakfast", [])

    print(f"Verified {len(breakfast_entries)} breakfast entries logged:")
    for entry in breakfast_entries:
        print(f"  - {entry.servings}x {entry.food_name}")
    print()

    # Test 4: List templates
    print("TEST 4: List all templates")
    print("=" * 60)

    templates = manager.list_templates()
    print(f"Found {len(templates)} template(s):")
    for t in templates:
        print(f"\n{t.name} ({t.meal_type})")
        print(f"  {len(t.foods)} foods, {t.total_calories:.0f} cal")
        print(f"  Used {t.use_count} times")
        if t.last_used:
            print(f"  Last used: {t.last_used[:10]}")

    print("\n✅ All tests completed!")
