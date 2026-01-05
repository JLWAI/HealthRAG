"""
Body Measurements Tracking System for HealthRAG

Tracks body measurements (waist, chest, arms, etc.) to complement weight tracking
and provide comprehensive progress monitoring. Includes body fat estimation using
validated formulas (waist-to-height ratio, Navy method).
"""

import sqlite3
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass
class BodyMeasurement:
    """Single body measurement entry"""
    entry_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD

    # Core measurements (inches)
    waist: Optional[float] = None
    chest: Optional[float] = None
    hips: Optional[float] = None
    neck: Optional[float] = None
    shoulders: Optional[float] = None

    # Arm measurements (inches)
    left_arm: Optional[float] = None
    right_arm: Optional[float] = None

    # Leg measurements (inches)
    left_thigh: Optional[float] = None
    right_thigh: Optional[float] = None
    left_calf: Optional[float] = None
    right_calf: Optional[float] = None

    # Optional notes
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class BodyFatEstimate:
    """Body fat percentage estimates using multiple methods"""
    waist_to_height_ratio: Optional[float] = None  # WHtR
    waist_to_height_bf_estimate: Optional[float] = None  # BF% from WHtR
    navy_method_bf: Optional[float] = None  # US Navy method
    bmi: Optional[float] = None  # Body Mass Index
    category: Optional[str] = None  # Fitness category


class BodyMeasurementTracker:
    """
    Body measurement tracking system with SQLite backend.

    Features:
    - Track 11 body measurements (waist, chest, arms, legs, etc.)
    - Body fat estimation (WHtR, Navy method)
    - Progress tracking vs. previous measurements
    - Measurement trends over time
    - Integration with weight tracking for comprehensive analysis

    Designed to complement weight tracking and adaptive TDEE.
    """

    def __init__(self, db_path: str = "data/body_measurements.db"):
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
                waist REAL,
                chest REAL,
                hips REAL,
                neck REAL,
                shoulders REAL,
                left_arm REAL,
                right_arm REAL,
                left_thigh REAL,
                right_thigh REAL,
                left_calf REAL,
                right_calf REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index for date lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_body_measurements_date
            ON body_measurements(date DESC)
        """)

        conn.commit()
        conn.close()

    def log_measurement(
        self,
        measurement_date: Optional[str] = None,
        waist: Optional[float] = None,
        chest: Optional[float] = None,
        hips: Optional[float] = None,
        neck: Optional[float] = None,
        shoulders: Optional[float] = None,
        left_arm: Optional[float] = None,
        right_arm: Optional[float] = None,
        left_thigh: Optional[float] = None,
        right_thigh: Optional[float] = None,
        left_calf: Optional[float] = None,
        right_calf: Optional[float] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Log body measurements (replaces existing entry for same date).

        Args:
            measurement_date: Date in YYYY-MM-DD format (default: today)
            waist: Waist circumference in inches (at narrowest point)
            chest: Chest circumference in inches (at nipple line)
            hips: Hip circumference in inches (at widest point)
            neck: Neck circumference in inches (just below larynx)
            shoulders: Shoulder width in inches (across deltoids)
            left_arm: Left arm circumference in inches (flexed bicep)
            right_arm: Right arm circumference in inches (flexed bicep)
            left_thigh: Left thigh circumference in inches (mid-thigh)
            right_thigh: Right thigh circumference in inches (mid-thigh)
            left_calf: Left calf circumference in inches (widest point)
            right_calf: Right calf circumference in inches (widest point)
            notes: Optional notes

        Returns:
            entry_id of logged measurement

        Raises:
            ValueError: If all measurements are None
        """
        if measurement_date is None:
            measurement_date = date.today().isoformat()

        # Validate that at least one measurement is provided
        measurements = [waist, chest, hips, neck, shoulders, left_arm, right_arm,
                       left_thigh, right_thigh, left_calf, right_calf]
        if all(m is None for m in measurements):
            raise ValueError("At least one measurement must be provided")

        # Validate measurement ranges (inches)
        for name, value in [
            ("waist", waist), ("chest", chest), ("hips", hips),
            ("neck", neck), ("shoulders", shoulders),
            ("left_arm", left_arm), ("right_arm", right_arm),
            ("left_thigh", left_thigh), ("right_thigh", right_thigh),
            ("left_calf", left_calf), ("right_calf", right_calf)
        ]:
            if value is not None and (value <= 0 or value > 100):
                raise ValueError(f"Invalid {name} measurement: {value} inches")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Use INSERT OR REPLACE to handle duplicate dates
            cursor.execute("""
                INSERT OR REPLACE INTO body_measurements (
                    date, waist, chest, hips, neck, shoulders,
                    left_arm, right_arm, left_thigh, right_thigh,
                    left_calf, right_calf, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (measurement_date, waist, chest, hips, neck, shoulders,
                  left_arm, right_arm, left_thigh, right_thigh,
                  left_calf, right_calf, notes))

            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id

        finally:
            conn.close()

    def get_measurements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[BodyMeasurement]:
        """
        Retrieve body measurement entries ordered by date (newest first).

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
                entry_id=row['id'],
                date=row['date'],
                waist=row['waist'],
                chest=row['chest'],
                hips=row['hips'],
                neck=row['neck'],
                shoulders=row['shoulders'],
                left_arm=row['left_arm'],
                right_arm=row['right_arm'],
                left_thigh=row['left_thigh'],
                right_thigh=row['right_thigh'],
                left_calf=row['left_calf'],
                right_calf=row['right_calf'],
                notes=row['notes'],
                created_at=row['created_at']
            )
            for row in rows
        ]

    def get_latest_measurement(self) -> Optional[BodyMeasurement]:
        """Get most recent body measurement entry"""
        entries = self.get_measurements(limit=1)
        return entries[0] if entries else None

    def delete_measurement(self, entry_date: str) -> bool:
        """
        Delete body measurement entry for specific date.

        Args:
            entry_date: Date in YYYY-MM-DD format

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM body_measurements WHERE date = ?", (entry_date,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted

    def calculate_body_fat(
        self,
        measurement: BodyMeasurement,
        weight_lbs: float,
        height_inches: float,
        sex: str
    ) -> BodyFatEstimate:
        """
        Calculate body fat estimates using multiple methods.

        Methods:
        1. Waist-to-Height Ratio (WHtR) - Simple screening tool
        2. US Navy Method - Gender-specific using neck/waist/hips
        3. BMI - Body Mass Index for reference

        Args:
            measurement: BodyMeasurement with waist/neck/hips data
            weight_lbs: Current body weight in pounds
            height_inches: Height in inches
            sex: "male" or "female"

        Returns:
            BodyFatEstimate with multiple calculations
        """
        estimate = BodyFatEstimate()

        # Calculate BMI
        if weight_lbs > 0 and height_inches > 0:
            estimate.bmi = (weight_lbs / (height_inches ** 2)) * 703

        # Waist-to-Height Ratio (WHtR)
        if measurement.waist and height_inches > 0:
            estimate.waist_to_height_ratio = measurement.waist / height_inches

            # Body fat estimate from WHtR (rough approximation)
            # WHtR < 0.5 = healthy, 0.5-0.6 = overweight, > 0.6 = obese
            if sex.lower() == "male":
                # Male approximation: BF% ≈ (WHtR - 0.42) × 100
                estimate.waist_to_height_bf_estimate = max(5, (estimate.waist_to_height_ratio - 0.35) * 100)
            else:
                # Female approximation: BF% ≈ (WHtR - 0.38) × 100
                estimate.waist_to_height_bf_estimate = max(8, (estimate.waist_to_height_ratio - 0.31) * 100)

        # US Navy Method (more accurate)
        if sex.lower() == "male":
            if measurement.waist and measurement.neck and height_inches > 0:
                # Male: BF% = 86.010 × log10(abdomen - neck) - 70.041 × log10(height) + 36.76
                import math
                abdomen = measurement.waist
                neck = measurement.neck
                log_abdomen_minus_neck = math.log10(abdomen - neck)
                log_height = math.log10(height_inches)
                estimate.navy_method_bf = 86.010 * log_abdomen_minus_neck - 70.041 * log_height + 36.76
        else:
            if measurement.waist and measurement.hips and measurement.neck and height_inches > 0:
                # Female: BF% = 163.205 × log10(waist + hip - neck) - 97.684 × log10(height) - 78.387
                import math
                waist_plus_hip_minus_neck = measurement.waist + measurement.hips - measurement.neck
                log_whm = math.log10(waist_plus_hip_minus_neck)
                log_height = math.log10(height_inches)
                estimate.navy_method_bf = 163.205 * log_whm - 97.684 * log_height - 78.387

        # Determine fitness category based on Navy method (most accurate)
        if estimate.navy_method_bf:
            bf = estimate.navy_method_bf
            if sex.lower() == "male":
                if bf < 6:
                    estimate.category = "Essential Fat"
                elif bf < 14:
                    estimate.category = "Athletic"
                elif bf < 18:
                    estimate.category = "Fitness"
                elif bf < 25:
                    estimate.category = "Average"
                else:
                    estimate.category = "Obese"
            else:  # female
                if bf < 14:
                    estimate.category = "Essential Fat"
                elif bf < 21:
                    estimate.category = "Athletic"
                elif bf < 25:
                    estimate.category = "Fitness"
                elif bf < 32:
                    estimate.category = "Average"
                else:
                    estimate.category = "Obese"

        return estimate

    def get_measurement_changes(
        self,
        current_date: Optional[str] = None,
        comparison_date: Optional[str] = None
    ) -> Dict[str, Optional[float]]:
        """
        Calculate changes between two measurement entries.

        Args:
            current_date: Date of current measurement (default: latest)
            comparison_date: Date of comparison measurement (default: previous entry)

        Returns:
            Dictionary with changes for each measurement (current - previous)
            Positive = gained, Negative = lost
        """
        if current_date is None:
            # Get latest measurement
            current = self.get_latest_measurement()
            if not current:
                return {}
            current_date = current.date
        else:
            entries = self.get_measurements(start_date=current_date, end_date=current_date)
            current = entries[0] if entries else None
            if not current:
                return {}

        if comparison_date is None:
            # Get previous measurement (entry before current)
            all_entries = self.get_measurements(end_date=current_date)
            if len(all_entries) < 2:
                return {}  # No previous measurement to compare
            previous = all_entries[1]  # Second entry (first is current)
        else:
            entries = self.get_measurements(start_date=comparison_date, end_date=comparison_date)
            previous = entries[0] if entries else None
            if not previous:
                return {}

        # Calculate changes
        changes = {}
        for field in ['waist', 'chest', 'hips', 'neck', 'shoulders',
                     'left_arm', 'right_arm', 'left_thigh', 'right_thigh',
                     'left_calf', 'right_calf']:
            current_val = getattr(current, field)
            previous_val = getattr(previous, field)

            if current_val is not None and previous_val is not None:
                changes[field] = current_val - previous_val
            else:
                changes[field] = None

        return changes
