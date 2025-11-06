"""
Unit Tests for Progress Photos Tracking System

Tests photo upload, retrieval, deletion, comparison, and metadata management.
"""

import pytest
import os
import tempfile
import shutil
from datetime import date, timedelta
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from progress_photos import (
    ProgressPhoto,
    PhotoComparison,
    ProgressPhotoTracker
)


def create_test_image(width=800, height=600, color=(100, 150, 200), text=None):
    """
    Create a real test image using PIL for testing photo upload/storage.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: RGB tuple for background color
        text: Optional text to draw on image

    Returns:
        BytesIO object containing a real JPEG image
    """
    # Create new RGB image
    img = Image.new('RGB', (width, height), color=color)

    # Add text if provided
    if text:
        draw = ImageDraw.Draw(img)
        # Use default font (PIL will handle this gracefully)
        try:
            # Try to use a larger font if available
            font = ImageFont.load_default()
        except:
            font = None

        # Calculate text position (centered)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((width - text_width) // 2, (height - text_height) // 2)

        # Draw text in white
        draw.text(position, text, fill=(255, 255, 255), font=font)

    # Save to BytesIO
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)
    img_bytes.name = "test_photo.jpg"

    return img_bytes


class TestProgressPhotoTracker:
    """Test ProgressPhotoTracker database and file operations"""

    @pytest.fixture
    def tracker(self):
        """Create temporary photo tracker for testing"""
        # Create temporary database and photos directory
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        photos_dir = tempfile.mkdtemp()

        tracker = ProgressPhotoTracker(db_path=db_path, photos_dir=photos_dir)
        yield tracker

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)
        if os.path.exists(photos_dir):
            shutil.rmtree(photos_dir)

    @pytest.fixture
    def sample_photo_file(self):
        """Create a sample photo file for testing"""
        # Create a real JPEG image using PIL
        return create_test_image(width=800, height=600, color=(100, 150, 200), text="Test Photo")

    def test_init_creates_database(self, tracker):
        """Test that initialization creates database and directory"""
        assert os.path.exists(tracker.db_path)
        assert os.path.exists(tracker.photos_dir)

    def test_save_photo_basic(self, tracker, sample_photo_file):
        """Test saving a basic progress photo"""
        photo_id = tracker.save_photo(
            photo_file=sample_photo_file,
            date_str="2025-10-15",
            angle="front",
            weight_lbs=210.5,
            phase="cut",
            notes="Week 1 starting photo"
        )

        assert photo_id > 0

        # Verify file was saved
        expected_path = os.path.join(tracker.photos_dir, "2025-10-15_front.jpg")
        assert os.path.exists(expected_path)

        # Verify database entry
        photo = tracker.get_photo_by_id(photo_id)
        assert photo is not None
        assert photo.date == "2025-10-15"
        assert photo.angle == "front"
        assert photo.weight_lbs == 210.5
        assert photo.phase == "cut"
        assert photo.notes == "Week 1 starting photo"

    def test_save_photo_minimal(self, tracker, sample_photo_file):
        """Test saving photo with only required fields"""
        photo_id = tracker.save_photo(
            photo_file=sample_photo_file,
            date_str="2025-10-15",
            angle="side"
        )

        assert photo_id > 0

        photo = tracker.get_photo_by_id(photo_id)
        assert photo.weight_lbs is None
        assert photo.phase is None
        assert photo.notes is None

    def test_save_photo_invalid_angle(self, tracker, sample_photo_file):
        """Test that invalid angle raises ValueError"""
        with pytest.raises(ValueError, match="Invalid angle"):
            tracker.save_photo(
                photo_file=sample_photo_file,
                date_str="2025-10-15",
                angle="diagonal"  # Invalid angle
            )

    def test_save_photo_duplicate_raises_error(self, tracker):
        """Test that duplicate date+angle raises error"""
        # Create first photo
        photo1 = create_test_image(color=(100, 150, 200), text="First Photo")
        tracker.save_photo(photo1, date_str="2025-10-15", angle="front")

        # Try to save duplicate
        photo2 = create_test_image(color=(200, 100, 150), text="Duplicate Photo")

        with pytest.raises(ValueError, match="Photo already exists"):
            tracker.save_photo(photo2, date_str="2025-10-15", angle="front")

    def test_get_photos_all(self, tracker):
        """Test retrieving all photos"""
        # Save 3 photos
        colors = [(100, 150, 200), (150, 200, 100), (200, 100, 150)]
        for i, angle in enumerate(["front", "side", "back"]):
            photo = create_test_image(color=colors[i], text=f"{angle.capitalize()} View")
            tracker.save_photo(
                photo,
                date_str="2025-10-15",
                angle=angle,
                weight_lbs=210.0 + i
            )

        photos = tracker.get_photos()
        assert len(photos) == 3

    def test_get_photos_by_date_range(self, tracker):
        """Test filtering photos by date range"""
        # Save photos across multiple dates
        for i in range(5):
            photo = create_test_image(color=(100 + i*20, 150, 200 - i*20), text=f"Day {i+1}")
            date_str = (date(2025, 10, 1) + timedelta(days=i)).isoformat()
            tracker.save_photo(photo, date_str=date_str, angle="front")

        # Get photos from Oct 2-4
        photos = tracker.get_photos(
            start_date="2025-10-02",
            end_date="2025-10-04"
        )

        assert len(photos) == 3
        assert photos[0].date == "2025-10-02"
        assert photos[-1].date == "2025-10-04"

    def test_get_photos_by_angle(self, tracker):
        """Test filtering photos by angle"""
        # Save front and side photos with unique dates
        for i, angle in enumerate(["front", "side", "front", "side"]):
            color = (100, 150, 200) if angle == "front" else (200, 150, 100)
            photo = create_test_image(color=color, text=f"{angle.capitalize()} {i+1}")
            # Use different dates to avoid duplicates
            date_str = (date(2025, 10, 1) + timedelta(days=i)).isoformat()
            tracker.save_photo(photo, date_str=date_str, angle=angle)

        # Should have 2 front and 2 side photos
        photos = tracker.get_photos(angle="front")
        assert len(photos) == 2
        assert all(p.angle == "front" for p in photos)

    def test_get_photos_by_phase(self, tracker):
        """Test filtering photos by phase"""
        # Save photos with different phases
        colors = [(200, 100, 100), (100, 200, 100), (200, 100, 100)]  # Red for cut, green for bulk
        for i, phase in enumerate(["cut", "bulk", "cut"]):
            photo = create_test_image(color=colors[i], text=f"{phase.capitalize()} Phase")
            date_str = (date(2025, 10, 1) + timedelta(days=i)).isoformat()
            tracker.save_photo(photo, date_str=date_str, angle="front", phase=phase)

        photos = tracker.get_photos(phase="cut")
        assert len(photos) == 2
        assert all(p.phase == "cut" for p in photos)

    def test_get_photo_by_id_exists(self, tracker, sample_photo_file):
        """Test retrieving photo by ID"""
        photo_id = tracker.save_photo(
            sample_photo_file,
            date_str="2025-10-15",
            angle="front"
        )

        photo = tracker.get_photo_by_id(photo_id)
        assert photo is not None
        assert photo.photo_id == photo_id

    def test_get_photo_by_id_not_found(self, tracker):
        """Test retrieving nonexistent photo returns None"""
        photo = tracker.get_photo_by_id(9999)
        assert photo is None

    def test_compare_photos_basic(self, tracker):
        """Test comparing two photos"""
        # Save before photo
        before = create_test_image(color=(210, 150, 150), text="Before - 210 lbs")
        before_id = tracker.save_photo(
            before,
            date_str="2025-09-01",
            angle="front",
            weight_lbs=210.0,
            phase="cut"
        )

        # Save after photo
        after = create_test_image(color=(150, 200, 150), text="After - 200 lbs")
        after_id = tracker.save_photo(
            after,
            date_str="2025-10-15",
            angle="front",
            weight_lbs=200.0,
            phase="cut"
        )

        comparison = tracker.compare_photos(before_id, after_id)

        assert comparison is not None
        assert comparison.days_elapsed == 44  # Sep 1 to Oct 15
        assert comparison.weight_change_lbs == -10.0
        assert comparison.phase_transition == "Cut (same phase)"

    def test_compare_photos_phase_transition(self, tracker):
        """Test comparison with phase transition"""
        before = create_test_image(color=(200, 100, 100), text="Cut Phase")
        before_id = tracker.save_photo(
            before,
            date_str="2025-09-01",
            angle="front",
            phase="cut"
        )

        after = create_test_image(color=(100, 200, 100), text="Bulk Phase")
        after_id = tracker.save_photo(
            after,
            date_str="2025-10-15",
            angle="front",
            phase="bulk"
        )

        comparison = tracker.compare_photos(before_id, after_id)

        assert comparison.phase_transition == "Cut → Bulk"

    def test_compare_photos_not_found(self, tracker):
        """Test comparison with nonexistent photo returns None"""
        comparison = tracker.compare_photos(9999, 8888)
        assert comparison is None

    def test_delete_photo(self, tracker, sample_photo_file):
        """Test deleting a photo removes both file and database entry"""
        photo_id = tracker.save_photo(
            sample_photo_file,
            date_str="2025-10-15",
            angle="front"
        )

        # Verify file exists
        expected_path = os.path.join(tracker.photos_dir, "2025-10-15_front.jpg")
        assert os.path.exists(expected_path)

        # Delete photo
        deleted = tracker.delete_photo(photo_id)
        assert deleted is True

        # Verify file removed
        assert not os.path.exists(expected_path)

        # Verify database entry removed
        photo = tracker.get_photo_by_id(photo_id)
        assert photo is None

    def test_delete_photo_not_found(self, tracker):
        """Test deleting nonexistent photo returns False"""
        deleted = tracker.delete_photo(9999)
        assert deleted is False

    def test_get_latest_photos_by_angle(self, tracker):
        """Test retrieving latest photo for each angle"""
        # Save multiple photos at different dates
        dates = ["2025-09-01", "2025-09-15", "2025-10-01"]
        for i, date_str in enumerate(dates):
            for angle in ["front", "side"]:
                color = (100 + i*30, 150, 200 - i*30) if angle == "front" else (200 - i*30, 150, 100 + i*30)
                photo = create_test_image(color=color, text=f"{angle.capitalize()} - {date_str}")
                tracker.save_photo(photo, date_str=date_str, angle=angle)

        latest = tracker.get_latest_photos_by_angle()

        assert len(latest) == 2
        assert "front" in latest
        assert "side" in latest
        assert latest["front"].date == "2025-10-01"
        assert latest["side"].date == "2025-10-01"

    def test_get_photo_count(self, tracker):
        """Test counting total photos"""
        assert tracker.get_photo_count() == 0

        # Save 3 photos
        for i in range(3):
            photo = create_test_image(color=(100 + i*40, 150 + i*20, 200 - i*40), text=f"Photo {i+1}")
            date_str = (date(2025, 10, 1) + timedelta(days=i)).isoformat()
            tracker.save_photo(photo, date_str=date_str, angle="front")

        assert tracker.get_photo_count() == 3

    def test_get_date_range_empty(self, tracker):
        """Test date range with no photos"""
        start, end = tracker.get_date_range()
        assert start is None
        assert end is None

    def test_get_date_range_with_photos(self, tracker):
        """Test date range with multiple photos"""
        dates = ["2025-09-01", "2025-09-15", "2025-10-01"]
        colors = [(150, 100, 100), (150, 150, 100), (150, 200, 100)]
        for i, date_str in enumerate(dates):
            photo = create_test_image(color=colors[i], text=f"Date: {date_str}")
            tracker.save_photo(photo, date_str=date_str, angle="front")

        start, end = tracker.get_date_range()
        assert start == "2025-09-01"
        assert end == "2025-10-01"

    def test_save_photo_with_bytes_directly(self, tracker):
        """Test saving photo with BytesIO object (real image bytes)"""
        # Create a real image and get its bytes
        photo_io = create_test_image(color=(180, 160, 140), text="Raw Bytes Test")
        # Extract the raw bytes from BytesIO
        photo_bytes = photo_io.read()
        photo_io.seek(0)  # Reset for saving

        photo_id = tracker.save_photo(
            photo_file=photo_io,
            date_str="2025-10-15",
            angle="back"
        )

        assert photo_id > 0

        # Verify file was saved
        expected_path = os.path.join(tracker.photos_dir, "2025-10-15_back.jpg")
        assert os.path.exists(expected_path)


@pytest.mark.integration
class TestProgressPhotoWorkflow:
    """Integration tests for complete photo tracking workflow"""

    def test_complete_progress_tracking_workflow(self):
        """Test complete workflow: upload, track, compare, delete"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name

        photos_dir = tempfile.mkdtemp()
        tracker = ProgressPhotoTracker(db_path=db_path, photos_dir=photos_dir)

        # Week 1: Starting photos
        week1_photos = []
        week1_colors = [(210, 150, 150), (210, 160, 160), (210, 170, 170)]  # Reddish tones for starting weight
        for i, angle in enumerate(["front", "side", "back"]):
            photo = create_test_image(color=week1_colors[i], text=f"Week 1 - {angle.capitalize()}")
            photo_id = tracker.save_photo(
                photo,
                date_str="2025-09-01",
                angle=angle,
                weight_lbs=210.0,
                phase="cut",
                notes="Starting week 1"
            )
            week1_photos.append(photo_id)

        # Week 8: Progress photos
        week8_photos = []
        week8_colors = [(150, 200, 150), (160, 200, 160), (170, 200, 170)]  # Greenish tones for progress
        for i, angle in enumerate(["front", "side", "back"]):
            photo = create_test_image(color=week8_colors[i], text=f"Week 8 - {angle.capitalize()}")
            photo_id = tracker.save_photo(
                photo,
                date_str="2025-10-27",
                angle=angle,
                weight_lbs=200.0,
                phase="cut",
                notes="8 weeks progress"
            )
            week8_photos.append(photo_id)

        # Verify 6 total photos
        assert tracker.get_photo_count() == 6

        # Compare front photos
        comparison = tracker.compare_photos(week1_photos[0], week8_photos[0])
        assert comparison.days_elapsed == 56  # 8 weeks
        assert comparison.weight_change_lbs == -10.0

        # Get all front photos
        front_photos = tracker.get_photos(angle="front")
        assert len(front_photos) == 2

        # Get latest photos by angle
        latest = tracker.get_latest_photos_by_angle()
        assert len(latest) == 3
        assert all(p.date == "2025-10-27" for p in latest.values())

        # Delete old photos
        for photo_id in week1_photos:
            deleted = tracker.delete_photo(photo_id)
            assert deleted is True

        # Verify only 3 photos remain
        assert tracker.get_photo_count() == 3

        # Cleanup
        os.remove(db_path)
        shutil.rmtree(photos_dir)
