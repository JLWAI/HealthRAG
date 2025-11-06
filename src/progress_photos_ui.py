"""
Progress Photos UI Components for HealthRAG

Streamlit UI components for progress photo upload, comparison, and visualization.

Features:
- Photo upload interface with metadata
- Before/after comparison view with slider
- Photo timeline/gallery
- Photo management (delete, update notes)

Author: Claude (Anthropic)
Date: November 2025
"""

import streamlit as st
from datetime import date, datetime, timedelta
from progress_photos import ProgressPhotoTracker, ProgressPhoto, PhotoComparison
from profile import UserProfile
from adaptive_tdee import WeightTracker
from typing import Optional
import os


def render_photo_upload():
    """
    Render photo upload interface.

    Allows users to upload progress photos with metadata:
    - Date
    - Angle (front, side, back, other)
    - Weight
    - Phase
    - Notes
    """
    st.subheader("📸 Upload Progress Photo")
    st.caption("Track your visual progress with progress photos")

    # Initialize tracker
    tracker = ProgressPhotoTracker()

    # Get user profile for defaults
    profile = UserProfile()
    if not profile.exists():
        st.warning("⚠️ Create your profile first to upload progress photos")
        return

    info = profile.get_personal_info()
    goals = profile.get_goals()

    # Upload form
    with st.form("photo_upload_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            photo_date = st.date_input(
                "Photo Date *",
                value=date.today(),
                max_value=date.today(),
                help="When was this photo taken? (required)"
            )

            angle = st.selectbox(
                "Angle/Pose *",
                options=["front", "side", "back", "other"],
                help="What angle is this photo? For best comparison, use consistent angles (required)"
            )

        with col2:
            weight_lbs = st.number_input(
                "Weight (lbs)",
                min_value=50.0,
                max_value=500.0,
                value=float(info.weight_lbs) if info.weight_lbs else 150.0,
                step=0.1,
                help="Your weight on this date (optional - helps track correlation between weight and appearance)"
            )

            phase = st.selectbox(
                "Phase *",
                options=["cut", "bulk", "maintain", "recomp"],
                index=["cut", "bulk", "maintain", "recomp"].index(goals.phase) if goals.phase in ["cut", "bulk", "maintain", "recomp"] else 0,
                help="Your diet phase when this photo was taken (required)"
            )

        notes = st.text_area(
            "Notes (optional)",
            placeholder="How are you feeling? Any observations? Training changes?",
            help="Add context about this photo - energy levels, training changes, notable observations",
            max_chars=500
        )

        uploaded_file = st.file_uploader(
            "Choose a photo *",
            type=["jpg", "jpeg", "png"],
            help="Upload a progress photo (JPG or PNG, max 10MB) - required"
        )

        st.caption("* = Required field")

        submitted = st.form_submit_button("📸 Upload Photo", type="primary", use_container_width=True)

        if submitted:
            if uploaded_file is None:
                st.error("❌ Please select a photo to upload")
            else:
                try:
                    # Loading state for upload
                    with st.spinner("Uploading and processing your photo..."):
                        photo_id = tracker.save_photo(
                            photo_file=uploaded_file,
                            date_str=photo_date.isoformat(),
                            angle=angle,
                            weight_lbs=weight_lbs if weight_lbs else None,
                            phase=phase,
                            notes=notes if notes else None
                        )

                    # Success feedback with toast
                    st.success(f"✅ Photo uploaded successfully! (ID: {photo_id})")
                    st.toast("Progress photo uploaded!", icon="📸")
                    st.rerun()

                except ValueError as e:
                    st.error(f"❌ {str(e)}")
                except Exception as e:
                    st.error(
                        f"❌ **Upload failed**\n\n"
                        f"Error: {str(e)}\n\n"
                        f"💡 **Tips:**\n"
                        f"- Make sure the file is a valid JPG or PNG\n"
                        f"- Check that the file size is under 10MB\n"
                        f"- Try a different photo if the issue persists"
                    )


def render_photo_gallery():
    """
    Render photo gallery/timeline view.

    Shows all progress photos in chronological order with:
    - Thumbnail images
    - Date, weight, phase
    - Delete option
    """
    st.subheader("🖼️ Photo Gallery")

    # Initialize tracker
    tracker = ProgressPhotoTracker()

    # Loading state
    with st.spinner("Loading your photo gallery..."):
        # Get all photos
        photos = tracker.get_photos()

    # Empty state with CTA
    if not photos:
        st.info(
            "📷 **No progress photos yet**\n\n"
            "Visual progress tracking is one of the most powerful tools for staying motivated!\n\n"
            "**Why take progress photos?**\n"
            "- See changes the scale doesn't show\n"
            "- Track body recomposition\n"
            "- Celebrate your transformation\n\n"
            "💡 **Tip:** Take photos in consistent lighting, clothing, and poses for best comparison."
        )

        # CTA button
        if st.button("📸 Upload Your First Photo", use_container_width=True, type="primary"):
            st.info("👆 Use the 'Upload' tab above to add your first progress photo!")
        return

    # Stats
    photo_count = len(photos)
    date_range = tracker.get_date_range()
    st.caption(f"📊 {photo_count} photos | {date_range[0]} to {date_range[1]}")

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        angle_filter = st.selectbox(
            "Filter by Angle",
            options=["All", "front", "side", "back", "other"],
            key="gallery_angle_filter"
        )

    with col2:
        phase_filter = st.selectbox(
            "Filter by Phase",
            options=["All", "cut", "bulk", "maintain", "recomp"],
            key="gallery_phase_filter"
        )

    # Apply filters
    if angle_filter != "All":
        photos = [p for p in photos if p.angle == angle_filter]

    if phase_filter != "All":
        photos = [p for p in photos if p.phase == phase_filter]

    if not photos:
        st.info("No photos match your filters")
        return

    st.markdown("---")

    # Display photos in grid (3 columns)
    cols_per_row = 3
    for i in range(0, len(photos), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            if i + j < len(photos):
                photo = photos[i + j]

                with col:
                    # Display image
                    if os.path.exists(photo.file_path):
                        st.image(photo.file_path, use_container_width=True)
                    else:
                        st.error("Image not found")

                    # Metadata
                    st.caption(f"**{photo.date}** ({photo.angle})")
                    if photo.weight_lbs:
                        st.caption(f"⚖️ {photo.weight_lbs} lbs")
                    if photo.phase:
                        st.caption(f"🎯 {photo.phase.capitalize()}")
                    if photo.notes:
                        with st.expander("📝 Notes", expanded=False):
                            st.write(photo.notes)

                    # Delete button with confirmation
                    delete_key = f"delete_{photo.photo_id}"
                    confirm_key = f"confirm_delete_{photo.photo_id}"

                    # Use session state for confirmation
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False

                    if not st.session_state[confirm_key]:
                        if st.button(f"🗑️ Delete", key=delete_key, use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()
                    else:
                        st.warning("⚠️ Are you sure?")
                        col_yes, col_no = st.columns(2)

                        with col_yes:
                            if st.button("✅ Yes, delete", key=f"yes_{photo.photo_id}", use_container_width=True):
                                with st.spinner("Deleting photo..."):
                                    if tracker.delete_photo(photo.photo_id):
                                        st.success("✅ Photo deleted")
                                        st.toast("Photo deleted", icon="🗑️")
                                        st.session_state[confirm_key] = False
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete photo")
                                        st.session_state[confirm_key] = False

                        with col_no:
                            if st.button("❌ Cancel", key=f"no_{photo.photo_id}", use_container_width=True):
                                st.session_state[confirm_key] = False
                                st.rerun()


def render_photo_comparison():
    """
    Render before/after photo comparison interface.

    Features:
    - Select two photos to compare
    - Side-by-side view
    - Comparison stats (days elapsed, weight change, phase transition)
    - Image slider widget (optional)
    """
    st.subheader("⚖️ Before/After Comparison")
    st.caption("Compare two progress photos to see your transformation")

    # Initialize tracker
    tracker = ProgressPhotoTracker()

    # Loading state
    with st.spinner("Loading photos..."):
        # Get all photos
        photos = tracker.get_photos()

    # Empty state with CTA
    if len(photos) < 2:
        st.info(
            "📷 **Need at least 2 photos to compare**\n\n"
            f"Current photos: {len(photos)}/2\n\n"
            "Upload more progress photos to unlock before/after comparisons!\n\n"
            "💡 **Tip:** Take photos at the same angle (front, side, back) for best comparison."
        )

        if st.button("📸 Upload More Photos", use_container_width=True, type="primary"):
            st.info("👆 Use the 'Upload' tab above to add more progress photos!")
        return

    # Select photos
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📅 Before Photo")
        before_options = {f"{p.date} ({p.angle})": p.photo_id for p in photos}
        before_label = st.selectbox(
            "Select Before Photo",
            options=list(before_options.keys()),
            key="before_photo_select"
        )
        before_id = before_options[before_label]

    with col2:
        st.markdown("### 📅 After Photo")
        after_options = {f"{p.date} ({p.angle})": p.photo_id for p in photos}
        after_label = st.selectbox(
            "Select After Photo",
            options=list(after_options.keys()),
            key="after_photo_select"
        )
        after_id = after_options[after_label]

    # Compare button
    if st.button("🔍 Compare Photos", type="primary", use_container_width=True):
        # Loading state for comparison
        with st.spinner("Analyzing your transformation..."):
            comparison = tracker.compare_photos(before_id, after_id)

        if not comparison:
            st.error(
                "❌ **Could not load photos**\n\n"
                "Please make sure both photos are still available and try again."
            )
            return

        # Success toast
        st.toast("Comparison ready!", icon="🔍")

        st.markdown("---")

        # Comparison stats
        st.markdown("### 📊 Comparison Stats")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Days Elapsed",
                f"{comparison.days_elapsed} days",
                help="Time between photos"
            )

        with col2:
            if comparison.weight_change_lbs is not None:
                delta_color = "inverse" if comparison.after_photo.phase in ["cut"] else "normal"
                st.metric(
                    "Weight Change",
                    f"{comparison.after_photo.weight_lbs:.1f} lbs",
                    delta=f"{comparison.weight_change_lbs:+.1f} lbs",
                    delta_color=delta_color,
                    help="Weight difference"
                )
            else:
                st.metric("Weight Change", "N/A", help="Weight data not available")

        with col3:
            if comparison.phase_transition:
                st.metric(
                    "Phase",
                    comparison.phase_transition.split("→")[-1].strip() if "→" in comparison.phase_transition else comparison.phase_transition,
                    help="Diet phase transition"
                )
            else:
                st.metric("Phase", "N/A")

        st.markdown("---")

        # Side-by-side images
        st.markdown("### 📸 Visual Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Before** ({comparison.before_photo.date})")
            if os.path.exists(comparison.before_photo.file_path):
                st.image(comparison.before_photo.file_path, use_container_width=True)
            else:
                st.error("Before image not found")

            if comparison.before_photo.weight_lbs:
                st.caption(f"⚖️ {comparison.before_photo.weight_lbs} lbs")
            if comparison.before_photo.phase:
                st.caption(f"🎯 {comparison.before_photo.phase.capitalize()}")
            if comparison.before_photo.notes:
                st.caption(f"📝 {comparison.before_photo.notes}")

        with col2:
            st.markdown(f"**After** ({comparison.after_photo.date})")
            if os.path.exists(comparison.after_photo.file_path):
                st.image(comparison.after_photo.file_path, use_container_width=True)
            else:
                st.error("After image not found")

            if comparison.after_photo.weight_lbs:
                st.caption(f"⚖️ {comparison.after_photo.weight_lbs} lbs")
            if comparison.after_photo.phase:
                st.caption(f"🎯 {comparison.after_photo.phase.capitalize()}")
            if comparison.after_photo.notes:
                st.caption(f"📝 {comparison.after_photo.notes}")


def render_latest_photos():
    """
    Render compact view of latest photos for each angle.

    Shows the most recent front/side/back photos in a row.
    Useful for dashboard/overview pages.
    """
    st.subheader("📸 Latest Progress Photos")

    # Initialize tracker
    tracker = ProgressPhotoTracker()

    # Loading state
    with st.spinner("Loading latest photos..."):
        # Get latest photos by angle
        latest_photos = tracker.get_latest_photos_by_angle()

    # Empty state
    if not latest_photos:
        st.info(
            "📷 **No progress photos yet**\n\n"
            "Upload your first photo to start tracking visual progress!"
        )
        return

    # Display in columns
    angles_order = ["front", "side", "back", "other"]
    available_angles = [a for a in angles_order if a in latest_photos]

    if not available_angles:
        st.info("📷 No progress photos available")
        return

    cols = st.columns(len(available_angles))

    for i, angle in enumerate(available_angles):
        photo = latest_photos[angle]

        with cols[i]:
            st.markdown(f"**{angle.capitalize()}**")

            if os.path.exists(photo.file_path):
                st.image(photo.file_path, use_container_width=True)
            else:
                st.error("Image not found")

            st.caption(f"📅 {photo.date}")
            if photo.weight_lbs:
                st.caption(f"⚖️ {photo.weight_lbs} lbs")


def render_progress_photos_full():
    """
    Full progress photos interface with all features.

    Combines upload, gallery, and comparison into a single tabbed interface.
    """
    st.markdown("---")
    st.header("📸 Progress Photos")
    st.caption("Track your visual transformation over time")

    tabs = st.tabs(["📤 Upload", "🖼️ Gallery", "⚖️ Compare"])

    with tabs[0]:
        render_photo_upload()

    with tabs[1]:
        render_photo_gallery()

    with tabs[2]:
        render_photo_comparison()
