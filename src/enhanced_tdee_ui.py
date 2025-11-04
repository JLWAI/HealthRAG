"""
Enhanced TDEE UI Components

Integrates all advanced TDEE analytics features into the Streamlit UI:
- Historical TDEE tracking with charts
- Body measurements tracking
- Water weight spike detection
- Goal predictions
- Weekly/monthly comparisons
- Export functionality
- Notification system

This module enhances the existing render_adaptive_tdee() function with
all the new analytics capabilities.
"""

import streamlit as st
from datetime import date, datetime, timedelta
import tempfile
from pathlib import Path

from adaptive_tdee import (
    WeightTracker, calculate_trend_weight, get_adaptive_tdee_insight,
    AdaptiveTDEEInsight
)
from tdee_analytics import (
    TDEEHistoricalTracker, TDEESnapshot,
    create_tdee_trend_chart, create_weight_progress_chart,
    detect_water_weight_spikes, predict_goal_date,
    export_tdee_data_csv, export_tdee_data_json,
    generate_weekly_comparison
)
from body_measurements import (
    BodyMeasurementTracker, BodyMeasurement
)
from progress_reports import (
    generate_monthly_progress_report,
    create_monthly_report_visualization
)
from food_logger import FoodLogger
from workout_database import WorkoutDatabase
from profile import UserProfile


def render_tdee_trend_visualization(tdee_tracker: TDEEHistoricalTracker, days: int = 30):
    """
    Render TDEE trend chart.

    Args:
        tdee_tracker: TDEEHistoricalTracker instance
        days: Number of days to display (default 30)
    """
    st.subheader("📈 TDEE Trend Analysis")

    start_date = (date.today() - timedelta(days=days)).isoformat()
    snapshots = tdee_tracker.get_snapshots(start_date=start_date)
    snapshots.reverse()  # Chronological order

    if len(snapshots) < 2:
        st.info(f"Need at least 2 TDEE snapshots to show trend. Keep logging!")
        return

    # Create and display chart
    fig = create_tdee_trend_chart(snapshots)
    st.plotly_chart(fig, use_container_width=True)

    # Summary stats
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_adaptive = sum(s.adaptive_tdee for s in snapshots if s.adaptive_tdee) / len([s for s in snapshots if s.adaptive_tdee])
        st.metric("Avg Adaptive TDEE", f"{avg_adaptive:.0f} cal")

    with col2:
        tdee_range = max(s.adaptive_tdee for s in snapshots if s.adaptive_tdee) - min(s.adaptive_tdee for s in snapshots if s.adaptive_tdee)
        st.metric("TDEE Range", f"±{tdee_range} cal")

    with col3:
        latest_delta = snapshots[-1].tdee_delta if snapshots[-1].tdee_delta else 0
        st.metric("Current vs Formula", f"{latest_delta:+d} cal")


def render_weight_progress_chart(weight_tracker: WeightTracker, days: int = 30):
    """
    Render weight progress chart with water weight alerts.

    Args:
        weight_tracker: WeightTracker instance
        days: Number of days to display
    """
    st.subheader("⚖️ Weight Progress & Water Weight Alerts")

    start_date = (date.today() - timedelta(days=days)).isoformat()
    weight_entries = weight_tracker.get_weights(start_date=start_date)
    weight_entries.reverse()  # Chronological order

    if not weight_entries:
        st.info("Start logging your daily weight to see progress!")
        return

    # Calculate trend weights
    weights = [e.weight_lbs for e in weight_entries]
    trend_weights = calculate_trend_weight(weights, alpha=0.3)

    # Prepare data for chart
    chart_data = [
        (e.date, e.weight_lbs, trend_weights[i])
        for i, e in enumerate(weight_entries)
    ]

    # Create and display chart
    fig = create_weight_progress_chart(chart_data)
    st.plotly_chart(fig, use_container_width=True)

    # Water weight spike detection
    alerts = detect_water_weight_spikes(chart_data, threshold_lbs=2.0)

    if alerts:
        st.warning(f"⚠️ {len(alerts)} water weight fluctuation(s) detected in last {days} days")

        # Show most recent alert
        latest_alert = alerts[0]

        with st.expander(f"💧 Latest Alert: {latest_alert.date} ({'+' if latest_alert.is_spike else ''}{latest_alert.deviation_lbs:.1f} lbs)", expanded=True):
            st.markdown(f"**Actual Weight:** {latest_alert.weight_lbs:.1f} lbs")
            st.markdown(f"**Trend Weight:** {latest_alert.trend_weight_lbs:.1f} lbs")
            st.markdown(f"**Deviation:** {'+' if latest_alert.is_spike else ''}{latest_alert.deviation_lbs:.1f} lbs")

            st.markdown("**Likely Causes:**")
            for cause in latest_alert.likely_causes[:3]:
                st.markdown(f"- {cause}")

            st.info(latest_alert.recommendation)


def render_goal_prediction(
    weight_tracker: WeightTracker,
    goal_weight_lbs: float,
    phase: str
):
    """
    Render goal date prediction.

    Args:
        weight_tracker: WeightTracker instance
        goal_weight_lbs: Target weight
        phase: Current phase (cut, bulk, maintain)
    """
    st.subheader("🎯 Goal Date Prediction")

    # Get recent weight data
    weight_entries = weight_tracker.get_weights(limit=14)
    weight_entries.reverse()

    if len(weight_entries) < 14:
        st.info(f"Need 14 days of data for accurate prediction. Current: {len(weight_entries)} days")
        return

    # Calculate trend weight and rate
    weights = [e.weight_lbs for e in weight_entries]
    trend_weights = calculate_trend_weight(weights, alpha=0.3)

    current_weight = trend_weights[-1]
    older_weight = trend_weights[0]
    days_elapsed = 14

    rate_lbs_week = ((current_weight - older_weight) / days_elapsed) * 7

    # Generate prediction
    prediction = predict_goal_date(
        current_weight_lbs=current_weight,
        goal_weight_lbs=goal_weight_lbs,
        current_rate_lbs_week=rate_lbs_week,
        data_days=len(weight_entries)
    )

    # Display prediction
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Weight", f"{prediction.current_weight_lbs:.1f} lbs")
        st.metric("Goal Weight", f"{prediction.goal_weight_lbs:.1f} lbs")

    with col2:
        st.metric("Weight to Go", f"{prediction.weight_to_go:.1f} lbs")
        st.metric("Current Rate", f"{prediction.current_rate_lbs_week:+.2f} lbs/week")

    with col3:
        st.metric("Predicted Date", prediction.predicted_date)
        st.metric("Confidence", prediction.confidence)

    # Scenarios
    st.markdown("#### 📊 Prediction Scenarios")

    scenarios_df = {
        'Scenario': ['Best Case (+20% rate)', 'Current Pace', 'Worst Case (-20% rate)'],
        'Weeks': [
            f"{prediction.best_case_weeks:.1f}",
            f"{prediction.predicted_weeks:.1f}",
            f"{prediction.worst_case_weeks:.1f}"
        ],
        'Date': [
            (date.today() + timedelta(weeks=prediction.best_case_weeks)).strftime("%Y-%m-%d"),
            prediction.predicted_date,
            (date.today() + timedelta(weeks=prediction.worst_case_weeks)).strftime("%Y-%m-%d")
        ]
    }

    st.table(scenarios_df)


def render_body_measurements():
    """
    Render body measurements tracking UI.
    """
    st.markdown("---")
    st.header("📏 Body Measurements")

    tracker = BodyMeasurementTracker(db_path="data/measurements.db")

    # Tabs for log vs. history
    tab1, tab2 = st.tabs(["📝 Log Measurements", "📊 Progress"])

    with tab1:
        st.markdown("### Log Today's Measurements")
        st.caption("Measure first thing in the morning for consistency. Not all measurements required.")

        measurement_date = st.date_input("Date", value=date.today())

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Upper Body (inches)**")
            neck = st.number_input("Neck", min_value=0.0, max_value=30.0, step=0.1, format="%.1f")
            chest = st.number_input("Chest", min_value=0.0, max_value=60.0, step=0.1, format="%.1f")
            shoulders = st.number_input("Shoulders", min_value=0.0, max_value=70.0, step=0.1, format="%.1f")

        with col2:
            st.markdown("**Arms & Core (inches)**")
            bicep_left = st.number_input("Bicep (Left)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")
            bicep_right = st.number_input("Bicep (Right)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")
            waist = st.number_input("Waist (at navel)", min_value=0.0, max_value=60.0, step=0.1, format="%.1f")
            hips = st.number_input("Hips", min_value=0.0, max_value=70.0, step=0.1, format="%.1f")

        with col3:
            st.markdown("**Lower Body (inches)**")
            thigh_left = st.number_input("Thigh (Left)", min_value=0.0, max_value=40.0, step=0.1, format="%.1f")
            thigh_right = st.number_input("Thigh (Right)", min_value=0.0, max_value=40.0, step=0.1, format="%.1f")
            calf_left = st.number_input("Calf (Left)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")
            calf_right = st.number_input("Calf (Right)", min_value=0.0, max_value=25.0, step=0.1, format="%.1f")

        notes = st.text_area("Notes (optional)")

        if st.button("💾 Save Measurements", type="primary", use_container_width=True):
            measurement = BodyMeasurement(
                measurement_id=None,
                date=measurement_date.isoformat(),
                neck_inches=neck if neck > 0 else None,
                chest_inches=chest if chest > 0 else None,
                shoulders_inches=shoulders if shoulders > 0 else None,
                bicep_left_inches=bicep_left if bicep_left > 0 else None,
                bicep_right_inches=bicep_right if bicep_right > 0 else None,
                waist_inches=waist if waist > 0 else None,
                hips_inches=hips if hips > 0 else None,
                thigh_left_inches=thigh_left if thigh_left > 0 else None,
                thigh_right_inches=thigh_right if thigh_right > 0 else None,
                calf_left_inches=calf_left if calf_left > 0 else None,
                calf_right_inches=calf_right if calf_right > 0 else None,
                notes=notes if notes else None
            )

            tracker.log_measurements(measurement)
            st.success(f"✅ Measurements saved for {measurement_date}")

            # Calculate waist-to-hip ratio if both present
            if waist > 0 and hips > 0:
                whr = tracker.calculate_waist_to_hip_ratio(measurement)
                st.info(f"📊 Waist-to-Hip Ratio: {whr:.3f}")

    with tab2:
        st.markdown("### Measurement Progress")

        measurements = tracker.get_measurements(limit=90)

        if len(measurements) < 2:
            st.info("Log measurements over time to see progress!")
        else:
            measurements.reverse()  # Chronological order

            # Compare first and last
            comparison = tracker.compare_measurements(
                measurements[-1].date,
                measurements[0].date
            )

            if comparison:
                st.markdown(f"#### Progress: {comparison.previous_date} → {comparison.current_date} ({comparison.days_between} days)")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Lost", f"{comparison.total_inches_lost:.1f} inches", delta=f"-{comparison.total_inches_lost:.1f}")

                with col2:
                    st.metric("Total Gained", f"{comparison.total_inches_gained:.1f} inches", delta=f"+{comparison.total_inches_gained:.1f}")

                with col3:
                    net_color = "off" if abs(comparison.net_change) < 0.5 else "normal"
                    st.metric("Net Change", f"{comparison.net_change:+.1f} inches", delta=f"{comparison.net_change:+.1f}")

                # Show detailed changes
                st.markdown("**Detailed Changes:**")
                changes_data = []
                for key, value in comparison.changes.items():
                    body_part = key.replace('_inches', '').replace('_', ' ').title()
                    changes_data.append({
                        'Body Part': body_part,
                        'Change (inches)': f"{value:+.1f}"
                    })

                st.table(changes_data)


def render_monthly_report(month: int, year: int):
    """
    Render monthly progress report.

    Args:
        month: Month number (1-12)
        year: Year
    """
    st.markdown("---")
    st.header("📊 Monthly Progress Report")

    # Initialize all trackers
    weight_tracker = WeightTracker(db_path="data/weights.db")
    tdee_tracker = TDEEHistoricalTracker(db_path="data/tdee_history.db")
    measurement_tracker = BodyMeasurementTracker(db_path="data/measurements.db")
    food_logger = FoodLogger(db_path="data/food_log.db")
    workout_db = WorkoutDatabase(db_path="data/workouts.db")

    # Get user profile for phase
    profile = UserProfile()
    phase = profile.get_goals().phase if profile.exists() else "maintain"

    # Generate report
    try:
        report = generate_monthly_progress_report(
            month=month,
            year=year,
            weight_tracker=weight_tracker,
            tdee_tracker=tdee_tracker,
            measurement_tracker=measurement_tracker,
            food_logger=food_logger,
            workout_db=workout_db,
            phase=phase
        )

        # Display report
        st.markdown(f"### {date(year, month, 1).strftime('%B %Y')} Summary")

        st.markdown(f"**Overall Rating:** {report.overall_rating}")
        st.markdown(f"*{report.summary}*")

        # Visualize
        fig = create_monthly_report_visualization(report)
        st.plotly_chart(fig, use_container_width=True)

        # Achievements
        if report.achievements:
            st.success("🏆 **Achievements:**")
            for achievement in report.achievements:
                st.markdown(f"- {achievement}")

        # Areas for improvement
        if report.areas_for_improvement:
            st.warning("⚠️ **Areas for Improvement:**")
            for area in report.areas_for_improvement:
                st.markdown(f"- {area}")

        # Recommendations
        if report.recommendations:
            st.info("💡 **Recommendations for Next Month:**")
            for rec in report.recommendations:
                st.markdown(f"- {rec}")

    except Exception as e:
        st.error(f"Could not generate report: {e}")


def render_export_options(tdee_tracker: TDEEHistoricalTracker):
    """
    Render data export options.

    Args:
        tdee_tracker: TDEEHistoricalTracker instance
    """
    st.markdown("---")
    st.subheader("📤 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        days_to_export = st.number_input("Days of history", min_value=7, max_value=365, value=30, step=7)

    with col2:
        export_format = st.selectbox("Format", ["CSV", "JSON"])

    if st.button("⬇️ Export TDEE Data", use_container_width=True):
        start_date = (date.today() - timedelta(days=days_to_export)).isoformat()
        snapshots = tdee_tracker.get_snapshots(start_date=start_date)
        snapshots.reverse()  # Chronological order

        if not snapshots:
            st.warning("No data to export!")
        else:
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{export_format.lower()}') as f:
                if export_format == "CSV":
                    export_tdee_data_csv(snapshots, f.name)
                else:
                    export_tdee_data_json(snapshots, f.name)

                temp_path = f.name

            # Read and offer download
            with open(temp_path, 'r') as f:
                data = f.read()

            st.download_button(
                label=f"📥 Download {export_format}",
                data=data,
                file_name=f"tdee_export_{date.today().isoformat()}.{export_format.lower()}",
                mime='text/csv' if export_format == 'CSV' else 'application/json',
                use_container_width=True
            )

            # Clean up
            Path(temp_path).unlink()

            st.success(f"✅ Exported {len(snapshots)} TDEE snapshots!")
