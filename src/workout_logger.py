"""
Workout Logging System for HealthRAG
Track actual workout performance: sets, reps, weight, RIR, feedback

Integrates with program_generator.py to compare prescribed vs actual performance
"""

import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass
class WorkoutSet:
    """Single set logged by user"""
    exercise_name: str
    weight_lbs: float
    reps: int
    rir: int  # Reps in Reserve (0-3)
    notes: Optional[str] = None


@dataclass
class WorkoutLog:
    """Complete workout session log"""
    workout_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD
    workout_name: str  # "Upper A", "Push", etc.
    sets: List[WorkoutSet]
    duration_minutes: int
    overall_pump: int  # 1-5 scale
    overall_soreness: int  # 1-5 scale
    overall_difficulty: int  # 1-5 scale
    notes: Optional[str] = None
    completed: bool = True


@dataclass
class WorkoutFeedback:
    """Post-workout feedback (autoregulation signals)"""
    pump_rating: int  # 1-5 (1=no pump, 5=huge pump)
    soreness_rating: int  # 1-5 (1=no soreness, 5=extremely sore)
    difficulty_rating: int  # 1-5 (1=too easy, 5=too hard)
    performance_notes: str  # "Felt strong", "Struggled with last sets", etc.


class WorkoutLogger:
    """
    Workout logging system with SQLite backend.

    Features:
    - Log individual sets (exercise, weight, reps, RIR)
    - Track workout feedback (pump, soreness, difficulty)
    - Compare prescribed vs actual performance
    - Calculate strength progress over time
    """

    def __init__(self, db_path: str = "data/workouts.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Workouts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                workout_name TEXT NOT NULL,
                duration_minutes INTEGER,
                overall_pump INTEGER,
                overall_soreness INTEGER,
                overall_difficulty INTEGER,
                notes TEXT,
                completed BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sets table (individual logged sets)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                weight_lbs REAL NOT NULL,
                reps INTEGER NOT NULL,
                rir INTEGER NOT NULL,
                set_order INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (workout_id) REFERENCES workouts (id)
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sets_workout_id ON sets(workout_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sets_exercise_name ON sets(exercise_name)")

        conn.commit()
        conn.close()

    def log_workout(self, workout: WorkoutLog) -> int:
        """
        Log a complete workout session.

        Args:
            workout: WorkoutLog object with all sets and feedback

        Returns:
            workout_id (int): Database ID of logged workout
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Insert workout
            cursor.execute("""
                INSERT INTO workouts (
                    date, workout_name, duration_minutes,
                    overall_pump, overall_soreness, overall_difficulty,
                    notes, completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workout.date,
                workout.workout_name,
                workout.duration_minutes,
                workout.overall_pump,
                workout.overall_soreness,
                workout.overall_difficulty,
                workout.notes,
                workout.completed
            ))

            workout_id = cursor.lastrowid

            # Insert sets
            for i, workout_set in enumerate(workout.sets, 1):
                cursor.execute("""
                    INSERT INTO sets (
                        workout_id, exercise_name, weight_lbs, reps, rir, set_order, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    workout_id,
                    workout_set.exercise_name,
                    workout_set.weight_lbs,
                    workout_set.reps,
                    workout_set.rir,
                    i,
                    workout_set.notes
                ))

            conn.commit()
            return workout_id

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_workout(self, workout_id: int) -> Optional[WorkoutLog]:
        """Get workout by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get workout metadata
        cursor.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,))
        workout_row = cursor.fetchone()

        if not workout_row:
            conn.close()
            return None

        # Get sets
        cursor.execute("""
            SELECT * FROM sets
            WHERE workout_id = ?
            ORDER BY set_order
        """, (workout_id,))
        set_rows = cursor.fetchall()

        conn.close()

        # Build WorkoutLog object
        sets = [
            WorkoutSet(
                exercise_name=row['exercise_name'],
                weight_lbs=row['weight_lbs'],
                reps=row['reps'],
                rir=row['rir'],
                notes=row['notes']
            )
            for row in set_rows
        ]

        return WorkoutLog(
            workout_id=workout_row['id'],
            date=workout_row['date'],
            workout_name=workout_row['workout_name'],
            sets=sets,
            duration_minutes=workout_row['duration_minutes'],
            overall_pump=workout_row['overall_pump'],
            overall_soreness=workout_row['overall_soreness'],
            overall_difficulty=workout_row['overall_difficulty'],
            notes=workout_row['notes'],
            completed=bool(workout_row['completed'])
        )

    def get_workouts_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[WorkoutLog]:
        """Get all workouts in date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM workouts
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """, (start_date, end_date))

        workout_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_workout(wid) for wid in workout_ids]

    def get_recent_workouts(self, limit: int = 10) -> List[WorkoutLog]:
        """Get most recent workouts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM workouts
            ORDER BY date DESC, created_at DESC
            LIMIT ?
        """, (limit,))

        workout_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        return [self.get_workout(wid) for wid in workout_ids]

    def get_exercise_history(
        self,
        exercise_name: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get performance history for an exercise.

        Returns list of dicts with date, weight, reps, RIR, estimated 1RM
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                w.date,
                s.weight_lbs,
                s.reps,
                s.rir,
                s.notes
            FROM sets s
            JOIN workouts w ON s.workout_id = w.id
            WHERE s.exercise_name = ?
            ORDER BY w.date DESC, s.set_order
            LIMIT ?
        """, (exercise_name, limit))

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            # Calculate estimated 1RM (Epley formula)
            weight = row['weight_lbs']
            reps = row['reps']
            rir = row['rir']

            # Adjust reps for RIR (if user had 2 RIR, they could've done 2 more reps)
            total_possible_reps = reps + rir
            estimated_1rm = weight * (1 + total_possible_reps / 30)

            history.append({
                'date': row['date'],
                'weight_lbs': weight,
                'reps': reps,
                'rir': rir,
                'estimated_1rm': estimated_1rm,
                'notes': row['notes']
            })

        return history

    def get_strength_progress(
        self,
        exercise_name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Calculate strength progress for an exercise over time.

        Returns:
            dict with starting 1RM, current 1RM, gain, percentage gain
        """
        history = self.get_exercise_history(exercise_name, limit=100)

        if not history:
            return {
                'exercise': exercise_name,
                'data_points': 0,
                'error': 'No data available'
            }

        # Filter by date range if provided
        if start_date:
            history = [h for h in history if h['date'] >= start_date]
        if end_date:
            history = [h for h in history if h['date'] <= end_date]

        if len(history) < 2:
            return {
                'exercise': exercise_name,
                'data_points': len(history),
                'error': 'Need at least 2 data points to calculate progress'
            }

        # Reverse to get chronological order
        history.reverse()

        starting_1rm = history[0]['estimated_1rm']
        current_1rm = history[-1]['estimated_1rm']
        gain_lbs = current_1rm - starting_1rm
        gain_pct = (gain_lbs / starting_1rm) * 100

        return {
            'exercise': exercise_name,
            'data_points': len(history),
            'starting_date': history[0]['date'],
            'current_date': history[-1]['date'],
            'starting_1rm': starting_1rm,
            'current_1rm': current_1rm,
            'gain_lbs': gain_lbs,
            'gain_percentage': gain_pct,
            'trend': 'improving' if gain_lbs > 0 else 'declining'
        }

    def get_workout_stats(self, days: int = 30) -> Dict:
        """
        Get workout statistics for last N days.

        Returns:
            dict with total workouts, total sets, average duration, etc.
        """
        start_date = (date.today() - timedelta(days=days)).isoformat()
        end_date = date.today().isoformat()

        workouts = self.get_workouts_by_date_range(start_date, end_date)

        if not workouts:
            return {
                'period_days': days,
                'total_workouts': 0,
                'error': 'No workouts logged in this period'
            }

        total_sets = sum(len(w.sets) for w in workouts)
        total_volume_lbs = sum(
            sum(s.weight_lbs * s.reps for s in w.sets)
            for w in workouts
        )
        avg_duration = sum(w.duration_minutes for w in workouts) / len(workouts)
        avg_pump = sum(w.overall_pump for w in workouts) / len(workouts)
        avg_soreness = sum(w.overall_soreness for w in workouts) / len(workouts)
        avg_difficulty = sum(w.overall_difficulty for w in workouts) / len(workouts)

        return {
            'period_days': days,
            'start_date': start_date,
            'end_date': end_date,
            'total_workouts': len(workouts),
            'total_sets': total_sets,
            'total_volume_lbs': total_volume_lbs,
            'avg_duration_minutes': avg_duration,
            'avg_pump_rating': avg_pump,
            'avg_soreness_rating': avg_soreness,
            'avg_difficulty_rating': avg_difficulty,
            'workouts_per_week': (len(workouts) / days) * 7
        }

    def delete_workout(self, workout_id: int):
        """Delete workout and all associated sets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM sets WHERE workout_id = ?", (workout_id,))
        cursor.execute("DELETE FROM workouts WHERE id = ?", (workout_id,))

        conn.commit()
        conn.close()


if __name__ == "__main__":
    # Example usage and testing
    print("=== Workout Logger Test ===\n")

    # Create logger
    logger = WorkoutLogger("data/test_workouts.db")

    # Test 1: Log a workout
    print("TEST 1: Logging a workout")
    print("=" * 60)

    workout = WorkoutLog(
        workout_id=None,
        date=date.today().isoformat(),
        workout_name="Upper A (Chest/Back Focus)",
        sets=[
            WorkoutSet("Barbell Bench Press", weight_lbs=185, reps=8, rir=2, notes="Felt strong"),
            WorkoutSet("Barbell Bench Press", weight_lbs=185, reps=8, rir=2),
            WorkoutSet("Barbell Bench Press", weight_lbs=185, reps=7, rir=1, notes="Last set was tough"),
            WorkoutSet("Incline Dumbbell Press", weight_lbs=60, reps=10, rir=2),
            WorkoutSet("Incline Dumbbell Press", weight_lbs=60, reps=9, rir=1),
            WorkoutSet("Chest Supported Row", weight_lbs=90, reps=12, rir=2),
            WorkoutSet("Chest Supported Row", weight_lbs=90, reps=11, rir=1),
        ],
        duration_minutes=65,
        overall_pump=4,
        overall_soreness=3,
        overall_difficulty=3,
        notes="Great workout, bench felt strong"
    )

    workout_id = logger.log_workout(workout)
    print(f"✅ Workout logged successfully! ID: {workout_id}\n")

    # Test 2: Retrieve workout
    print("TEST 2: Retrieve logged workout")
    print("=" * 60)
    retrieved = logger.get_workout(workout_id)
    print(f"Date: {retrieved.date}")
    print(f"Workout: {retrieved.workout_name}")
    print(f"Duration: {retrieved.duration_minutes} minutes")
    print(f"Total Sets: {len(retrieved.sets)}")
    print(f"Feedback: Pump={retrieved.overall_pump}, Soreness={retrieved.overall_soreness}, Difficulty={retrieved.overall_difficulty}")
    print()

    # Test 3: Exercise history
    print("TEST 3: Exercise history (Barbell Bench Press)")
    print("=" * 60)
    history = logger.get_exercise_history("Barbell Bench Press")
    for entry in history:
        print(f"{entry['date']}: {entry['weight_lbs']} lbs × {entry['reps']} @ {entry['rir']} RIR (Est 1RM: {entry['estimated_1rm']:.1f} lbs)")
    print()

    # Test 4: Workout stats
    print("TEST 4: Workout statistics (last 30 days)")
    print("=" * 60)
    stats = logger.get_workout_stats(30)
    print(f"Total workouts: {stats['total_workouts']}")
    print(f"Total sets: {stats['total_sets']}")
    print(f"Total volume: {stats['total_volume_lbs']:,.0f} lbs")
    print(f"Avg duration: {stats['avg_duration_minutes']:.0f} minutes")
    print(f"Avg pump: {stats['avg_pump_rating']:.1f}/5")
    print(f"Workouts per week: {stats['workouts_per_week']:.1f}")
