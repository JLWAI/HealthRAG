"""
Body Measurements Tracking System

Track body circumferences (waist, chest, arms, etc.) to monitor body composition
changes beyond the scale. Essential for cutting/recomp phases where weight may
not tell the full story.

Features:
- Multiple measurement points (waist, chest, arms, thighs, etc.)
- Progress tracking over time
- Comparison with previous measurements
- Integration with weight and nutrition data
"""

import sqlite3
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass
class BodyMeasurement:
    """Complete body measurement entry"""
    measurement_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD

    # Upper body (inches)
    neck_inches: Optional[float] = None
    chest_inches: Optional[float] = None
    shoulders_inches: Optional[float] = None
    bicep_left_inches: Optional[float] = None
    bicep_right_inches: Optional[float] = None
    forearm_left_inches: Optional[float] = None
    forearm_right_inches: Optional[float] = None

    # Core (inches)
    waist_inches: Optional[float] = None  # At navel
    hips_inches: Optional[float] = None

    # Lower body (inches)
    thigh_left_inches: Optional[float] = None
    thigh_right_inches: Optional[float] = None
    calf_left_inches: Optional[float] = None
    calf_right_inches: Optional[float] = None

    # Optional metadata
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class MeasurementComparison:
    """Comparison between two measurement dates"""
    current_date: str
    previous_date: str
    days_between: int

    # Changes (current - previous)
    changes: Dict[str, float]  # {'waist_inches': -1.5, 'chest_inches': +0.5}

    # Summary
    total_inches_lost: float
    total_inches_gained: float
    net_change: float


class BodyMeasurementTracker:
    """
    Body measurements tracking system with SQLite backend.

    Complements weight tracking to provide complete body composition picture.
    """

    def __init__(self, db_path: str = "data/measurements.db"):
        """
        Initialize body measurement tracker.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Body measurements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS body_measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,

                -- Upper body (inches)
                neck_inches REAL,
                chest_inches REAL,
                shoulders_inches REAL,
                bicep_left_inches REAL,
                bicep_right_inches REAL,
                forearm_left_inches REAL,
                forearm_right_inches REAL,

                -- Core (inches)
                waist_inches REAL,
                hips_inches REAL,

                -- Lower body (inches)
                thigh_left_inches REAL,
                thigh_right_inches REAL,
                calf_left_inches REAL,
                calf_right_inches REAL,

                -- Metadata
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for date lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_measurements_date
            ON body_measurements(date DESC)
        """)

        conn.commit()
        conn.close()

    def log_measurements(self, measurement: BodyMeasurement) -> int:
        """
        Log body measurements (replaces existing entry for same date).

        Args:
            measurement: BodyMeasurement object with data

        Returns:
            measurement_id of logged entry
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Convert dataclass to dict, exclude id and created_at
            data = asdict(measurement)
            data.pop('measurement_id', None)
            data.pop('created_at', None)

            # Build INSERT OR REPLACE query
            columns = list(data.keys())
            placeholders = ['?' for _ in columns]
            values = [data[col] for col in columns]

            query = f"""
                INSERT OR REPLACE INTO body_measurements ({', '.join(columns)})
                VALUES ({', '.join(placeholders)})
            """

            cursor.execute(query, values)
            measurement_id = cursor.lastrowid
            conn.commit()

            return measurement_id

        finally:
            conn.close()

    def get_measurements(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        limit: Optional[int] = None) -> List[BodyMeasurement]:
        """
        Retrieve body measurements ordered by date (newest first).

        Args:
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            limit: Optional limit on number of entries

        Returns:
            List of BodyMeasurement objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = "SELECT * FROM body_measurements WHERE 1=1"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " ORDER BY date DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [
            BodyMeasurement(
                measurement_id=row['id'],
                date=row['date'],
                neck_inches=row['neck_inches'],
                chest_inches=row['chest_inches'],
                shoulders_inches=row['shoulders_inches'],
                bicep_left_inches=row['bicep_left_inches'],
                bicep_right_inches=row['bicep_right_inches'],
                forearm_left_inches=row['forearm_left_inches'],
                forearm_right_inches=row['forearm_right_inches'],
                waist_inches=row['waist_inches'],
                hips_inches=row['hips_inches'],
                thigh_left_inches=row['thigh_left_inches'],
                thigh_right_inches=row['thigh_right_inches'],
                calf_left_inches=row['calf_left_inches'],
                calf_right_inches=row['calf_right_inches'],
                notes=row['notes'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def get_latest_measurement(self) -> Optional[BodyMeasurement]:
        """Get most recent measurement entry"""
        measurements = self.get_measurements(limit=1)
        return measurements[0] if measurements else None

    def compare_measurements(self, date1: str, date2: str) -> Optional[MeasurementComparison]:
        """
        Compare two measurement dates.

        Args:
            date1: More recent date (YYYY-MM-DD)
            date2: Earlier date (YYYY-MM-DD)

        Returns:
            MeasurementComparison with changes, or None if dates not found
        """
        m1_list = self.get_measurements(start_date=date1, end_date=date1)
        m2_list = self.get_measurements(start_date=date2, end_date=date2)

        if not m1_list or not m2_list:
            return None

        m1 = m1_list[0]
        m2 = m2_list[0]

        # Calculate date difference
        d1 = datetime.fromisoformat(date1).date()
        d2 = datetime.fromisoformat(date2).date()
        days_between = (d1 - d2).days

        # Calculate changes for all measurement points
        measurement_fields = [
            'neck_inches', 'chest_inches', 'shoulders_inches',
            'bicep_left_inches', 'bicep_right_inches',
            'forearm_left_inches', 'forearm_right_inches',
            'waist_inches', 'hips_inches',
            'thigh_left_inches', 'thigh_right_inches',
            'calf_left_inches', 'calf_right_inches'
        ]

        changes = {}
        total_lost = 0.0
        total_gained = 0.0

        for field in measurement_fields:
            val1 = getattr(m1, field)
            val2 = getattr(m2, field)

            if val1 is not None and val2 is not None:
                change = val1 - val2
                changes[field] = round(change, 2)

                if change < 0:
                    total_lost += abs(change)
                elif change > 0:
                    total_gained += change

        net_change = total_gained - total_lost

        return MeasurementComparison(
            current_date=date1,
            previous_date=date2,
            days_between=days_between,
            changes=changes,
            total_inches_lost=round(total_lost, 2),
            total_inches_gained=round(total_gained, 2),
            net_change=round(net_change, 2)
        )

    def get_measurement_progress(self, days: int = 90) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get measurement progress over time for all body parts.

        Args:
            days: Number of days to look back

        Returns:
            Dict mapping measurement field to list of (date, value) tuples
        """
        start_date = (date.today() - timedelta(days=days)).isoformat()
        measurements = self.get_measurements(start_date=start_date)
        measurements.reverse()  # Chronological order

        progress = {}
        measurement_fields = [
            'neck_inches', 'chest_inches', 'shoulders_inches',
            'bicep_left_inches', 'bicep_right_inches',
            'waist_inches', 'hips_inches',
            'thigh_left_inches', 'thigh_right_inches',
            'calf_left_inches', 'calf_right_inches'
        ]

        for field in measurement_fields:
            progress[field] = [
                (m.date, getattr(m, field))
                for m in measurements
                if getattr(m, field) is not None
            ]

        return progress

    def delete_measurement(self, measurement_date: str) -> bool:
        """
        Delete measurement entry for specific date.

        Args:
            measurement_date: Date in YYYY-MM-DD format

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM body_measurements WHERE date = ?", (measurement_date,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def calculate_waist_to_hip_ratio(self, measurement: BodyMeasurement) -> Optional[float]:
        """
        Calculate waist-to-hip ratio (WHR).

        WHR Guidelines (Health Risk):
        - Men: <0.90 (low risk), 0.90-0.99 (moderate), ≥1.0 (high)
        - Women: <0.80 (low risk), 0.80-0.84 (moderate), ≥0.85 (high)

        Args:
            measurement: BodyMeasurement object

        Returns:
            WHR ratio or None if measurements missing
        """
        if measurement.waist_inches and measurement.hips_inches:
            return round(measurement.waist_inches / measurement.hips_inches, 3)
        return None
