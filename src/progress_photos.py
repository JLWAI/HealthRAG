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
import logging
from PIL import Image
import time

from performance_utils import timing_decorator, log_query_performance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    def __init__(self, db_path: str = "data/photos.db", photos_dir: str = "data/photos",
                 thumbnails_dir: str = "data/photos/thumbnails"):
        """
        Initialize progress photo tracker.

        Args:
            db_path: Path to SQLite database file
            photos_dir: Directory to store photo files
            thumbnails_dir: Directory to store thumbnail images (default: data/photos/thumbnails)
        """
        self.db_path = db_path
        self.photos_dir = photos_dir
        self.thumbnails_dir = thumbnails_dir
        self._init_database()
        self._init_photos_directory()
        self._init_thumbnails_directory()

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
        try:
            Path(self.photos_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Photos directory initialized: {self.photos_dir}")
        except PermissionError:
            logger.error(f"Permission denied creating photos directory: {self.photos_dir}")
            raise ValueError(f"Cannot create photos directory (permission denied): {self.photos_dir}")
        except OSError as e:
            logger.error(f"Failed to create photos directory: {e}")
            raise ValueError(f"Failed to create photos directory: {e}")

    def _init_thumbnails_directory(self):
        """Create thumbnails directory if it doesn't exist."""
        try:
            Path(self.thumbnails_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Thumbnails directory initialized: {self.thumbnails_dir}")
        except PermissionError:
            logger.error(f"Permission denied creating thumbnails directory: {self.thumbnails_dir}")
            # Non-fatal - thumbnails are optional
        except OSError as e:
            logger.error(f"Failed to create thumbnails directory: {e}")
            # Non-fatal - thumbnails are optional

    def generate_thumbnail(self, photo_path: str, size: Tuple[int, int] = (200, 200),
                          force_regenerate: bool = False) -> Optional[str]:
        """
        Generate thumbnail for a photo.

        PERFORMANCE: Thumbnails are cached and only regenerated if force_regenerate=True.

        Args:
            photo_path: Path to full-size photo
            size: Thumbnail size (width, height) in pixels (default: 200x200)
            force_regenerate: Force regenerate even if thumbnail exists

        Returns:
            Path to thumbnail file, or None if generation failed
        """
        try:
            if not os.path.exists(photo_path):
                logger.warning(f"Photo not found: {photo_path}")
                return None

            # Generate thumbnail filename
            photo_filename = os.path.basename(photo_path)
            thumbnail_path = os.path.join(self.thumbnails_dir, f"thumb_{photo_filename}")

            # Check if thumbnail already exists
            if os.path.exists(thumbnail_path) and not force_regenerate:
                logger.debug(f"Thumbnail already exists: {thumbnail_path}")
                return thumbnail_path

            # Load and resize image
            start_time = time.time()
            with Image.open(photo_path) as img:
                # Convert to RGB if needed (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Create thumbnail (maintains aspect ratio)
                img.thumbnail(size, Image.LANCZOS)

                # Save thumbnail with optimization
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(f"Generated thumbnail in {elapsed_ms:.1f}ms: {thumbnail_path}")

            return thumbnail_path

        except Exception as e:
            logger.error(f"Failed to generate thumbnail for {photo_path}: {e}")
            return None

    def _check_disk_space(self, required_mb: float = 10.0) -> bool:
        """
        Check if sufficient disk space is available.

        Args:
            required_mb: Required disk space in MB

        Returns:
            True if sufficient space available

        Raises:
            ValueError: If insufficient disk space
        """
        try:
            stat = os.statvfs(self.photos_dir)
            # Available space in MB
            available_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)

            if available_mb < required_mb:
                raise ValueError(f"Insufficient disk space: {available_mb:.1f}MB available, {required_mb:.1f}MB required")

            return True
        except AttributeError:
            # statvfs not available on Windows - skip check
            logger.warning("Disk space check not available on this platform")
            return True

    def _validate_image_file(self, photo_file, max_size_mb: float = 10.0) -> Tuple[bool, str]:
        """
        Validate uploaded image file.

        Args:
            photo_file: File-like object
            max_size_mb: Maximum file size in MB

        Returns:
            (is_valid, error_message) tuple

        Raises:
            ValueError: If file is invalid
        """
        # Check file size
        if hasattr(photo_file, 'size'):
            size_mb = photo_file.size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise ValueError(f"Photo upload failed: File size ({size_mb:.1f}MB) exceeds {max_size_mb}MB limit")

        # Check file type by extension
        if hasattr(photo_file, 'name'):
            ext = photo_file.name.split('.')[-1].lower()
            valid_extensions = ['jpg', 'jpeg', 'png']
            if ext not in valid_extensions:
                raise ValueError(f"Photo upload failed: Invalid file type '.{ext}'. Must be JPG or PNG")

        # Try to open and validate image
        try:
            if hasattr(photo_file, 'seek'):
                photo_file.seek(0)  # Reset file pointer

            # Attempt to open image
            img = Image.open(photo_file)
            img.verify()  # Verify it's a valid image

            # Reset file pointer after verify()
            if hasattr(photo_file, 'seek'):
                photo_file.seek(0)

            logger.info(f"Image validated: {img.format} {img.size}")
            return True, ""

        except Exception as e:
            raise ValueError(f"Photo upload failed: Corrupt or invalid image file ({str(e)})")

    def _validate_date(self, date_str: str):
        """
        Validate date string is in ISO format and not in the future.

        Args:
            date_str: Date string (YYYY-MM-DD)

        Raises:
            ValueError: If date is invalid
        """
        try:
            photo_date = datetime.fromisoformat(date_str).date()
        except ValueError:
            raise ValueError(f"Invalid date format: '{date_str}'. Must be YYYY-MM-DD")

        # Check if date is in the future
        if photo_date > date.today():
            raise ValueError(f"Photo date cannot be in the future: {date_str}")

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
            ValueError: If validation fails or photo already exists
        """
        logger.info(f"Saving photo: date={date_str}, angle={angle}")

        # Validate date
        self._validate_date(date_str)

        # Validate angle
        valid_angles = ["front", "side", "back", "other"]
        if angle not in valid_angles:
            raise ValueError(f"Invalid angle '{angle}'. Must be one of: {valid_angles}")

        # Validate phase if provided
        if phase:
            valid_phases = ["cut", "bulk", "maintain", "recomp"]
            if phase not in valid_phases:
                raise ValueError(f"Invalid phase '{phase}'. Must be one of: {valid_phases}")

        # Validate weight if provided
        if weight_lbs is not None:
            if weight_lbs <= 0 or weight_lbs > 1000:
                raise ValueError(f"Invalid weight: {weight_lbs} lbs. Must be between 0 and 1000")

        # Validate image file (size, type, corruption)
        self._validate_image_file(photo_file, max_size_mb=10.0)

        # Check disk space
        self._check_disk_space(required_mb=10.0)

        # Ensure photos directory exists
        if not os.path.exists(self.photos_dir):
            logger.warning(f"Photos directory missing, recreating: {self.photos_dir}")
            self._init_photos_directory()

        # Generate filename: YYYY-MM-DD_angle.jpg
        file_extension = photo_file.name.split('.')[-1] if hasattr(photo_file, 'name') else 'jpg'
        filename = f"{date_str}_{angle}.{file_extension}"
        file_path = os.path.join(self.photos_dir, filename)

        # Check if photo already exists
        if os.path.exists(file_path):
            raise ValueError(f"Photo already exists for {date_str} {angle}. Delete it first to replace.")

        # Save file to disk
        try:
            with open(file_path, 'wb') as f:
                if hasattr(photo_file, 'read'):
                    f.write(photo_file.read())
                else:
                    f.write(photo_file)
            logger.info(f"Photo saved to disk: {file_path}")

        except PermissionError:
            logger.error(f"Permission denied writing photo: {file_path}")
            raise ValueError(f"Photo upload failed: Permission denied")
        except OSError as e:
            logger.error(f"Failed to write photo: {e}")
            raise ValueError(f"Photo upload failed: {str(e)}")

        # Save metadata to database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO photos (date, file_path, angle, weight_lbs, phase, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date_str, file_path, angle, weight_lbs, phase, notes))

            photo_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Photo metadata saved to database: photo_id={photo_id}")
            return photo_id

        except sqlite3.IntegrityError:
            # If DB insert fails, remove the file we just saved
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Database integrity error: duplicate photo for {date_str} {angle}")
            raise ValueError(f"Photo already exists for {date_str} {angle}")

        except sqlite3.OperationalError as e:
            # Database locked or inaccessible
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Database error: {e}")
            raise ValueError(f"Photo upload failed: Database error ({str(e)})")

        except Exception as e:
            # Cleanup on any unexpected error
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.error(f"Unexpected error saving photo: {e}")
            raise ValueError(f"Photo upload failed: {str(e)}")

        finally:
            if 'conn' in locals():
                conn.close()

    @timing_decorator(threshold_ms=100)
    def get_photos(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        angle: Optional[str] = None,
        phase: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ProgressPhoto]:
        """
        Retrieve progress photos with optional filters.

        PERFORMANCE: Added pagination support (limit/offset) to prevent loading too many photos.

        Args:
            start_date: Filter photos from this date onwards (ISO format)
            end_date: Filter photos up to this date (ISO format)
            angle: Filter by angle (front, side, back, other)
            phase: Filter by phase (cut, bulk, maintain, recomp)
            limit: Maximum number of photos to return (default: all)
            offset: Number of photos to skip (for pagination, default: 0)

        Returns:
            List of ProgressPhoto objects, sorted by date (oldest first)
        """
        start_time = time.time()

        try:
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

            # Add pagination
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            elapsed_ms = (time.time() - start_time) * 1000
            log_query_performance("get_photos", len(rows), elapsed_ms)

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

            logger.info(f"Retrieved {len(photos)} photos (limit={limit}, offset={offset})")
            return photos

        except sqlite3.OperationalError as e:
            logger.error(f"Database error retrieving photos: {e}")
            return []  # Graceful degradation
        except Exception as e:
            logger.error(f"Unexpected error retrieving photos: {e}")
            return []

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
