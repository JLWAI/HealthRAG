"""
Progress Photos Tracking System for HealthRAG

Provides progress photo storage, comparison, and visualization capabilities
for tracking visual body composition changes over time.

Features:
- Photo upload with metadata (date, weight, phase, angle, notes)
- Filesystem storage with SQLite metadata tracking
- Before/after comparison views
- Timeline visualization
- Multiple angle support (front, side, back)
- Photo deletion and management

Author: Claude (Anthropic)
Date: November 2025
"""

import sqlite3
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Tuple
from pathlib import Path


@dataclass
class ProgressPhoto:
    """
    Single progress photo with metadata.

    Attributes:
        photo_id: Unique photo identifier (None for new photos)
        date: Photo date (ISO format YYYY-MM-DD)
        file_path: Relative path to photo file (e.g., data/photos/2025-01-15_front.jpg)
        angle: Photo angle (front, side, back, other)
        weight_lbs: User's weight on photo date (optional)
        phase: Diet phase (cut, bulk, maintain, recomp)
        notes: User notes about this photo (optional)
        created_at: Timestamp when photo was uploaded
    """
    photo_id: Optional[int]
    date: str  # ISO format YYYY-MM-DD
    file_path: str
    angle: str  # front, side, back, other
    weight_lbs: Optional[float] = None
    phase: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class PhotoComparison:
    """
    Before/after photo comparison.

    Attributes:
        before_photo: Earlier progress photo
        after_photo: Later progress photo
        days_elapsed: Days between photos
        weight_change_lbs: Weight difference (after - before)
        phase_transition: Phase change description (e.g., "Cut → Maintain")
    """
    before_photo: ProgressPhoto
    after_photo: ProgressPhoto
    days_elapsed: int
    weight_change_lbs: Optional[float] = None
    phase_transition: Optional[str] = None


class ProgressPhotoTracker:
    """
    Progress photo tracking system with SQLite backend and filesystem storage.

    Features:
    - Save photos with metadata
    - Retrieve photos by date range, angle, phase
    - Compare photos (before/after)
    - Delete photos
    - Timeline visualization support

    Database Schema:
        photos (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            file_path TEXT NOT NULL UNIQUE,
            angle TEXT NOT NULL,
            weight_lbs REAL,
            phase TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )

    Filesystem Structure:
        data/photos/
            2025-01-15_front.jpg
            2025-01-15_side.jpg
            2025-01-15_back.jpg
            2025-02-15_front.jpg
            ...
    """

    def __init__(self, db_path: str = "data/photos.db", photos_dir: str = "data/photos"):
        """
        Initialize progress photo tracker.

        Args:
            db_path: Path to SQLite database file
            photos_dir: Directory to store photo files
        """
        self.db_path = db_path
        self.photos_dir = photos_dir
        self._init_database()
        self._init_photos_directory()

    def _init_database(self):
        """Create photos table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                angle TEXT NOT NULL,
                weight_lbs REAL,
                phase TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index for efficient date queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_photos_date
            ON photos(date)
        """)

        # Index for angle filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_photos_angle
            ON photos(angle)
        """)

        conn.commit()
        conn.close()

    def _init_photos_directory(self):
        """Create photos directory if it doesn't exist."""
        Path(self.photos_dir).mkdir(parents=True, exist_ok=True)

    def save_photo(
        self,
        photo_file,  # File-like object (e.g., from Streamlit file uploader)
        date_str: str,
        angle: str,
        weight_lbs: Optional[float] = None,
        phase: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Save progress photo to filesystem and database.

        Args:
            photo_file: File-like object containing photo data
            date_str: Photo date (ISO format YYYY-MM-DD)
            angle: Photo angle (front, side, back, other)
            weight_lbs: User's weight on photo date (optional)
            phase: Diet phase (optional)
            notes: User notes (optional)

        Returns:
            photo_id: ID of saved photo

        Raises:
            ValueError: If angle is invalid or photo already exists for date+angle
        """
        # Validate angle
        valid_angles = ["front", "side", "back", "other"]
        if angle not in valid_angles:
            raise ValueError(f"Invalid angle '{angle}'. Must be one of: {valid_angles}")

        # Generate filename: YYYY-MM-DD_angle.jpg
        file_extension = photo_file.name.split('.')[-1] if hasattr(photo_file, 'name') else 'jpg'
        filename = f"{date_str}_{angle}.{file_extension}"
        file_path = os.path.join(self.photos_dir, filename)

        # Check if photo already exists
        if os.path.exists(file_path):
            raise ValueError(f"Photo already exists for {date_str} {angle}. Delete it first to replace.")

        # Save file to disk
        with open(file_path, 'wb') as f:
            if hasattr(photo_file, 'read'):
                f.write(photo_file.read())
            else:
                f.write(photo_file)

        # Save metadata to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO photos (date, file_path, angle, weight_lbs, phase, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, file_path, angle, weight_lbs, phase, notes))

            photo_id = cursor.lastrowid
            conn.commit()

            return photo_id

        except sqlite3.IntegrityError as e:
            # If DB insert fails, remove the file we just saved
            os.remove(file_path)
            raise ValueError(f"Photo already exists for {date_str} {angle}")

        finally:
            conn.close()

    def get_photos(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        angle: Optional[str] = None,
        phase: Optional[str] = None
    ) -> List[ProgressPhoto]:
        """
        Retrieve progress photos with optional filters.

        Args:
            start_date: Filter photos from this date onwards (ISO format)
            end_date: Filter photos up to this date (ISO format)
            angle: Filter by angle (front, side, back, other)
            phase: Filter by phase (cut, bulk, maintain, recomp)

        Returns:
            List of ProgressPhoto objects, sorted by date (oldest first)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT id, date, file_path, angle, weight_lbs, phase, notes, created_at FROM photos WHERE 1=1"
        params = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        if angle:
            query += " AND angle = ?"
            params.append(angle)

        if phase:
            query += " AND phase = ?"
            params.append(phase)

        query += " ORDER BY date ASC, angle ASC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        photos = []
        for row in rows:
            photo = ProgressPhoto(
                photo_id=row[0],
                date=row[1],
                file_path=row[2],
                angle=row[3],
                weight_lbs=row[4],
                phase=row[5],
                notes=row[6],
                created_at=row[7]
            )
            photos.append(photo)

        return photos

    def get_photo_by_id(self, photo_id: int) -> Optional[ProgressPhoto]:
        """
        Retrieve a single photo by ID.

        Args:
            photo_id: Photo ID

        Returns:
            ProgressPhoto object or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, date, file_path, angle, weight_lbs, phase, notes, created_at
            FROM photos
            WHERE id = ?
        """, (photo_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return ProgressPhoto(
            photo_id=row[0],
            date=row[1],
            file_path=row[2],
            angle=row[3],
            weight_lbs=row[4],
            phase=row[5],
            notes=row[6],
            created_at=row[7]
        )

    def compare_photos(
        self,
        before_photo_id: int,
        after_photo_id: int
    ) -> Optional[PhotoComparison]:
        """
        Create a before/after photo comparison.

        Args:
            before_photo_id: ID of earlier photo
            after_photo_id: ID of later photo

        Returns:
            PhotoComparison object or None if photos not found
        """
        before = self.get_photo_by_id(before_photo_id)
        after = self.get_photo_by_id(after_photo_id)

        if not before or not after:
            return None

        # Calculate days elapsed
        before_date = datetime.fromisoformat(before.date)
        after_date = datetime.fromisoformat(after.date)
        days_elapsed = (after_date - before_date).days

        # Calculate weight change
        weight_change = None
        if before.weight_lbs and after.weight_lbs:
            weight_change = after.weight_lbs - before.weight_lbs

        # Phase transition
        phase_transition = None
        if before.phase and after.phase:
            if before.phase != after.phase:
                phase_transition = f"{before.phase.capitalize()} → {after.phase.capitalize()}"
            else:
                phase_transition = f"{before.phase.capitalize()} (same phase)"

        return PhotoComparison(
            before_photo=before,
            after_photo=after,
            days_elapsed=days_elapsed,
            weight_change_lbs=weight_change,
            phase_transition=phase_transition
        )

    def delete_photo(self, photo_id: int) -> bool:
        """
        Delete a progress photo (both file and database entry).

        Args:
            photo_id: ID of photo to delete

        Returns:
            True if deleted successfully, False if photo not found
        """
        photo = self.get_photo_by_id(photo_id)
        if not photo:
            return False

        # Delete file if it exists
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)

        # Delete database entry
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM photos WHERE id = ?", (photo_id,))
        conn.commit()
        conn.close()

        return True

    def get_latest_photos_by_angle(self) -> dict:
        """
        Get the most recent photo for each angle.

        Returns:
            Dictionary mapping angle -> ProgressPhoto
            Example: {"front": ProgressPhoto(...), "side": ProgressPhoto(...)}
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get latest photo for each angle
        cursor.execute("""
            SELECT DISTINCT angle FROM photos
        """)
        angles = [row[0] for row in cursor.fetchall()]

        latest_photos = {}
        for angle in angles:
            cursor.execute("""
                SELECT id, date, file_path, angle, weight_lbs, phase, notes, created_at
                FROM photos
                WHERE angle = ?
                ORDER BY date DESC, created_at DESC
                LIMIT 1
            """, (angle,))

            row = cursor.fetchone()
            if row:
                photo = ProgressPhoto(
                    photo_id=row[0],
                    date=row[1],
                    file_path=row[2],
                    angle=row[3],
                    weight_lbs=row[4],
                    phase=row[5],
                    notes=row[6],
                    created_at=row[7]
                )
                latest_photos[angle] = photo

        conn.close()
        return latest_photos

    def get_photo_count(self) -> int:
        """
        Get total number of photos stored.

        Returns:
            Total photo count
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM photos")
        count = cursor.fetchone()[0]

        conn.close()
        return count

    def get_date_range(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get date range of all photos (earliest to latest).

        Returns:
            (earliest_date, latest_date) as ISO strings, or (None, None) if no photos
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT MIN(date), MAX(date) FROM photos")
        result = cursor.fetchone()

        conn.close()

        if result[0] is None:
            return (None, None)

        return (result[0], result[1])
