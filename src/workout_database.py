"""
Workout Database for HealthRAG

SQLite database for storing and querying workout data.
Supports workout sessions, exercise logs, sets, and progress tracking.
"""

import sqlite3
import os
from datetime import date, datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

try:
    from workout_models import WorkoutSession, ExerciseLog, WorkoutSet, ExerciseProgress
except ImportError:
    from src.workout_models import WorkoutSession, ExerciseLog, WorkoutSet, ExerciseProgress


class WorkoutDatabase:
    """
    SQLite database for workout tracking.

    Stores:
    - Workout sessions (date, muscle group, completion status)
    - Exercise logs (exercise name, target protocol)
    - Sets (weight, reps, RIR, timestamp)
    - Progress tracking (PRs, volume, trends)
    """

    def __init__(self, db_path: str = "data/workouts.db"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_directory()
        self._init_database()

    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Workout sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                muscle_group TEXT NOT NULL,
                duration_minutes INTEGER,
                completed INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        # Exercise logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                target_sets INTEGER NOT NULL,
                target_reps_min INTEGER NOT NULL,
                target_reps_max INTEGER NOT NULL,
                target_rir INTEGER NOT NULL,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES workout_sessions (session_id)
            )
        ''')

        # Sets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workout_sets (
                set_id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER NOT NULL,
                set_number INTEGER NOT NULL,
                weight_lbs REAL NOT NULL,
                reps_completed INTEGER NOT NULL,
                rir INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (log_id) REFERENCES exercise_logs (log_id)
            )
        ''')

        # Exercise progress table (materialized view for quick queries)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_progress (
                exercise_name TEXT PRIMARY KEY,
                first_logged TEXT NOT NULL,
                last_logged TEXT NOT NULL,
                best_weight REAL NOT NULL DEFAULT 0,
                best_reps_at_weight INTEGER NOT NULL DEFAULT 0,
                total_volume REAL NOT NULL DEFAULT 0,
                total_sets INTEGER NOT NULL DEFAULT 0,
                avg_rir REAL NOT NULL DEFAULT 0
            )
        ''')

        # Create indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_date ON workout_sessions(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_exercise ON exercise_logs(exercise_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sets_log ON workout_sets(log_id)')

        conn.commit()
        conn.close()

    # ========================================================================
    # CREATE OPERATIONS
    # ========================================================================

    def save_session(self, session: WorkoutSession) -> int:
        """
        Save workout session to database.

        Args:
            session: WorkoutSession to save

        Returns:
            session_id of saved session
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        # Insert session
        cursor.execute('''
            INSERT INTO workout_sessions
            (date, muscle_group, duration_minutes, completed, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.date.isoformat(),
            session.muscle_group,
            session.duration_minutes,
            1 if session.completed else 0,
            session.notes,
            now,
            now
        ))

        session_id = cursor.lastrowid
        session.session_id = session_id

        # Insert exercises and sets
        for exercise_log in session.exercises:
            log_id = self._save_exercise_log(cursor, session_id, exercise_log)
            exercise_log.log_id = log_id

            # Update progress
            self._update_exercise_progress(cursor, exercise_log, session.date)

        conn.commit()
        conn.close()

        return session_id

    def _save_exercise_log(self, cursor, session_id: int, exercise_log: ExerciseLog) -> int:
        """Save exercise log and its sets"""
        cursor.execute('''
            INSERT INTO exercise_logs
            (session_id, exercise_name, target_sets, target_reps_min, target_reps_max, target_rir, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            exercise_log.exercise_name,
            exercise_log.target_sets,
            exercise_log.target_reps_min,
            exercise_log.target_reps_max,
            exercise_log.target_rir,
            exercise_log.notes
        ))

        log_id = cursor.lastrowid

        # Save sets
        for workout_set in exercise_log.sets:
            cursor.execute('''
                INSERT INTO workout_sets
                (log_id, set_number, weight_lbs, reps_completed, rir, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                log_id,
                workout_set.set_number,
                workout_set.weight_lbs,
                workout_set.reps_completed,
                workout_set.rir,
                workout_set.timestamp.isoformat()
            ))

            workout_set.set_id = cursor.lastrowid

        return log_id

    def _update_exercise_progress(self, cursor, exercise_log: ExerciseLog, session_date: date):
        """Update exercise progress table"""
        exercise_name = exercise_log.exercise_name

        # Check if exercise exists in progress table
        cursor.execute('SELECT * FROM exercise_progress WHERE exercise_name = ?', (exercise_name,))
        existing = cursor.fetchone()

        if existing:
            # Update existing progress
            progress = ExerciseProgress(
                exercise_name=exercise_name,
                first_logged=date.fromisoformat(existing['first_logged']),
                last_logged=date.fromisoformat(existing['last_logged']),
                best_weight=existing['best_weight'],
                best_reps_at_weight=existing['best_reps_at_weight'],
                total_volume=existing['total_volume'],
                total_sets=existing['total_sets'],
                avg_rir=existing['avg_rir']
            )
            progress.update_from_log(exercise_log, session_date)

            cursor.execute('''
                UPDATE exercise_progress
                SET last_logged = ?, best_weight = ?, best_reps_at_weight = ?,
                    total_volume = ?, total_sets = ?, avg_rir = ?
                WHERE exercise_name = ?
            ''', (
                progress.last_logged.isoformat(),
                progress.best_weight,
                progress.best_reps_at_weight,
                progress.total_volume,
                progress.total_sets,
                progress.avg_rir,
                exercise_name
            ))
        else:
            # Create new progress entry
            progress = ExerciseProgress(
                exercise_name=exercise_name,
                first_logged=session_date,
                last_logged=session_date
            )
            progress.update_from_log(exercise_log, session_date)

            cursor.execute('''
                INSERT INTO exercise_progress
                (exercise_name, first_logged, last_logged, best_weight, best_reps_at_weight,
                 total_volume, total_sets, avg_rir)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                exercise_name,
                progress.first_logged.isoformat(),
                progress.last_logged.isoformat(),
                progress.best_weight,
                progress.best_reps_at_weight,
                progress.total_volume,
                progress.total_sets,
                progress.avg_rir
            ))

    # ========================================================================
    # READ OPERATIONS
    # ========================================================================

    def get_session(self, session_id: int) -> Optional[WorkoutSession]:
        """Get workout session by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM workout_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        session = self._row_to_session(cursor, row)
        conn.close()
        return session

    def get_sessions_by_date_range(self, start_date: date, end_date: date) -> List[WorkoutSession]:
        """Get all sessions within date range"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM workout_sessions
            WHERE date >= ? AND date <= ?
            ORDER BY date DESC
        ''', (start_date.isoformat(), end_date.isoformat()))

        sessions = [self._row_to_session(cursor, row) for row in cursor.fetchall()]
        conn.close()
        return sessions

    def get_latest_session_for_muscle(self, muscle_group: str) -> Optional[WorkoutSession]:
        """Get most recent session for a muscle group"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM workout_sessions
            WHERE muscle_group = ?
            ORDER BY date DESC
            LIMIT 1
        ''', (muscle_group,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        session = self._row_to_session(cursor, row)
        conn.close()
        return session

    def get_exercise_progress(self, exercise_name: str) -> Optional[ExerciseProgress]:
        """Get progress for a specific exercise"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM exercise_progress WHERE exercise_name = ?', (exercise_name,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        progress = ExerciseProgress(
            exercise_name=row['exercise_name'],
            first_logged=date.fromisoformat(row['first_logged']),
            last_logged=date.fromisoformat(row['last_logged']),
            best_weight=row['best_weight'],
            best_reps_at_weight=row['best_reps_at_weight'],
            total_volume=row['total_volume'],
            total_sets=row['total_sets'],
            avg_rir=row['avg_rir']
        )

        conn.close()
        return progress

    def get_last_exercise_log(self, exercise_name: str) -> Optional[Tuple[ExerciseLog, date]]:
        """Get the most recent log for an exercise"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT el.*, ws.date
            FROM exercise_logs el
            JOIN workout_sessions ws ON el.session_id = ws.session_id
            WHERE el.exercise_name = ?
            ORDER BY ws.date DESC
            LIMIT 1
        ''', (exercise_name,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        exercise_log = self._row_to_exercise_log(cursor, row)
        session_date = date.fromisoformat(row['date'])

        conn.close()
        return (exercise_log, session_date)

    def _row_to_session(self, cursor, row) -> WorkoutSession:
        """Convert database row to WorkoutSession"""
        session_id = row['session_id']

        # Get exercise logs
        cursor.execute('SELECT * FROM exercise_logs WHERE session_id = ?', (session_id,))
        exercise_rows = cursor.fetchall()

        exercises = [self._row_to_exercise_log(cursor, ex_row) for ex_row in exercise_rows]

        return WorkoutSession(
            date=date.fromisoformat(row['date']),
            muscle_group=row['muscle_group'],
            exercises=exercises,
            duration_minutes=row['duration_minutes'],
            completed=bool(row['completed']),
            notes=row['notes'],
            session_id=session_id
        )

    def _row_to_exercise_log(self, cursor, row) -> ExerciseLog:
        """Convert database row to ExerciseLog"""
        log_id = row['log_id']

        # Get sets
        cursor.execute('SELECT * FROM workout_sets WHERE log_id = ? ORDER BY set_number', (log_id,))
        set_rows = cursor.fetchall()

        sets = [
            WorkoutSet(
                set_number=s['set_number'],
                weight_lbs=s['weight_lbs'],
                reps_completed=s['reps_completed'],
                rir=s['rir'],
                timestamp=datetime.fromisoformat(s['timestamp']),
                set_id=s['set_id']
            )
            for s in set_rows
        ]

        return ExerciseLog(
            exercise_name=row['exercise_name'],
            target_sets=row['target_sets'],
            target_reps_min=row['target_reps_min'],
            target_reps_max=row['target_reps_max'],
            target_rir=row['target_rir'],
            sets=sets,
            notes=row['notes'],
            log_id=log_id
        )


if __name__ == "__main__":
    # Test database
    print("=== Workout Database Test ===\n")

    # Initialize database
    db = WorkoutDatabase("data/test_workouts.db")
    print("✅ Database initialized\n")

    # Create test session
    session = WorkoutSession(
        date=date.today(),
        muscle_group="Chest & Triceps"
    )

    # Add bench press
    bench = session.add_exercise(
        exercise_name="barbell_bench_press",
        target_sets=4,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )
    bench.add_set(225, 12, 2)
    bench.add_set(225, 10, 2)
    bench.add_set(225, 9, 3)
    bench.add_set(225, 8, 3)

    session.completed = True
    session.duration_minutes = 45

    # Save session
    session_id = db.save_session(session)
    print(f"✅ Saved session {session_id}\n")

    # Retrieve session
    retrieved = db.get_session(session_id)
    print(f"Retrieved session: {retrieved.muscle_group}")
    print(f"Exercises: {len(retrieved.exercises)}")
    print(f"Sets: {retrieved.get_total_sets()}")
    print(f"Volume: {retrieved.get_total_volume():.0f} lbs\n")

    # Check progress
    progress = db.get_exercise_progress("barbell_bench_press")
    if progress:
        print(f"Progress for barbell_bench_press:")
        print(f"  Best: {progress.best_weight} lbs × {progress.best_reps_at_weight} reps")
        print(f"  Total volume: {progress.total_volume:.0f} lbs")
        print(f"  Total sets: {progress.total_sets}")
        print(f"  Avg RIR: {progress.avg_rir:.1f}")

    print("\n✅ All tests passed!")

    # Clean up test database
    import os
    if os.path.exists("data/test_workouts.db"):
        os.remove("data/test_workouts.db")
        print("✅ Test database cleaned up")
