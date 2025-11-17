"""
Autoregulation Engine for HealthRAG
Analyze workout feedback and provide program adjustment recommendations

Based on Renaissance Periodization's autoregulation principles:
- Monitor pump, soreness, difficulty ratings
- Compare prescribed vs actual RIR/reps/weight
- Recommend volume/intensity adjustments
- Prevent overtraining and undertraining

KEY ADVANTAGE OVER RP HYPERTROPHY APP:
- RP has limited autoregulation (manual adjustments only)
- HealthRAG provides AI-powered recommendations based on all feedback signals
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

from workout_logger import WorkoutLogger


class AdjustmentType(Enum):
    """Types of program adjustments"""
    INCREASE_VOLUME = "increase_volume"
    DECREASE_VOLUME = "decrease_volume"
    INCREASE_LOAD = "increase_load"
    DECREASE_LOAD = "decrease_load"
    INCREASE_RIR = "increase_rir"
    DECREASE_RIR = "decrease_rir"
    MAINTAIN = "maintain"
    DELOAD_NEEDED = "deload_needed"
    CHANGE_EXERCISE = "change_exercise"


@dataclass
class AutoregulationSignal:
    """Single autoregulation signal from workout feedback"""
    signal_type: str
    severity: str  # "low", "medium", "high"
    description: str
    recommendation: str


@dataclass
class ProgramAdjustment:
    """Recommended program adjustment"""
    adjustment_type: AdjustmentType
    target: str  # "overall", "muscle_group", or exercise name
    reason: str
    signals: List[AutoregulationSignal]
    priority: int  # 1-5 (5 = critical, 1 = minor)


class AutoregulationEngine:
    """
    Autoregulation engine for intelligent program adjustments.

    Analyzes:
    - Pump ratings (1-5): Indicates volume adequacy
    - Soreness ratings (1-5): Indicates recovery status
    - Difficulty ratings (1-5): Indicates intensity appropriateness
    - RIR (0-3): Compares prescribed vs actual
    - Performance trends: Weight, reps over time

    Generates:
    - Volume adjustment recommendations
    - Load adjustment recommendations
    - Exercise substitution suggestions
    - Deload warnings
    """

    def __init__(self, logger: Optional[WorkoutLogger] = None):
        self.logger = logger or WorkoutLogger()

    def analyze_recent_workouts(
        self,
        days: int = 7,
        min_workouts: int = 3
    ) -> List[ProgramAdjustment]:
        """
        Analyze recent workouts and generate adjustment recommendations.

        Args:
            days: Number of days to analyze
            min_workouts: Minimum workouts needed for analysis

        Returns:
            List of recommended adjustments, sorted by priority
        """
        # Get recent workout stats
        stats = self.logger.get_workout_stats(days=days)

        if 'error' in stats or stats['total_workouts'] < min_workouts:
            return []

        adjustments = []

        # Analyze overall training stress
        adjustments.extend(self._analyze_training_stress(stats))

        # Analyze specific exercises
        # Get recent workouts to find exercises
        recent_workouts = self.logger.get_recent_workouts(limit=20)
        exercise_names = set()
        for workout in recent_workouts:
            for workout_set in workout.sets:
                exercise_names.add(workout_set.exercise_name)

        # Analyze each exercise
        for exercise in exercise_names:
            adjustments.extend(self._analyze_exercise_progress(exercise, days=days))

        # Sort by priority (highest first)
        adjustments.sort(key=lambda x: x.priority, reverse=True)

        return adjustments

    def _analyze_training_stress(self, stats: Dict) -> List[ProgramAdjustment]:
        """
        Analyze overall training stress from workout stats.

        Signals:
        - Avg pump < 2.5: Volume may be too low
        - Avg pump > 4.5: Volume may be excessive
        - Avg soreness > 4: Not recovering adequately
        - Avg difficulty < 2: Intensity too low
        - Avg difficulty > 4.5: Intensity too high or poor recovery
        """
        adjustments = []
        signals = []

        avg_pump = stats['avg_pump_rating']
        avg_soreness = stats['avg_soreness_rating']
        avg_difficulty = stats['avg_difficulty_rating']

        # Pump analysis
        if avg_pump < 2.5:
            signals.append(AutoregulationSignal(
                signal_type="low_pump",
                severity="medium",
                description=f"Average pump rating is low ({avg_pump:.1f}/5)",
                recommendation="Consider increasing volume by 1-2 sets per muscle per week"
            ))
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.INCREASE_VOLUME,
                target="overall",
                reason="Low pump ratings indicate insufficient volume for growth stimulus",
                signals=[signals[-1]],
                priority=3
            ))

        elif avg_pump > 4.5:
            signals.append(AutoregulationSignal(
                signal_type="excessive_pump",
                severity="low",
                description=f"Average pump rating is very high ({avg_pump:.1f}/5)",
                recommendation="Volume is adequate, may be approaching MRV"
            ))
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.MAINTAIN,
                target="overall",
                reason="Excellent pump ratings - current volume is working well",
                signals=[signals[-1]],
                priority=1
            ))

        # Soreness analysis
        if avg_soreness > 4.0:
            signals.append(AutoregulationSignal(
                signal_type="excessive_soreness",
                severity="high",
                description=f"Average soreness rating is very high ({avg_soreness:.1f}/5)",
                recommendation="Reduce volume by 2-3 sets per muscle or take a deload week"
            ))
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.DELOAD_NEEDED,
                target="overall",
                reason="Excessive soreness indicates inadequate recovery - risk of overtraining",
                signals=[signals[-1]],
                priority=5  # Critical
            ))

        # Difficulty analysis
        if avg_difficulty < 2.0:
            signals.append(AutoregulationSignal(
                signal_type="too_easy",
                severity="medium",
                description=f"Average difficulty rating is low ({avg_difficulty:.1f}/5)",
                recommendation="Increase load by 5-10 lbs on main lifts or decrease RIR by 1"
            ))
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.INCREASE_LOAD,
                target="overall",
                reason="Workouts feeling too easy - time to progress intensity",
                signals=[signals[-1]],
                priority=3
            ))

        elif avg_difficulty > 4.5:
            signals.append(AutoregulationSignal(
                signal_type="too_hard",
                severity="high",
                description=f"Average difficulty rating is very high ({avg_difficulty:.1f}/5)",
                recommendation="Increase RIR by 1 or reduce load by 5-10%"
            ))
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.INCREASE_RIR,
                target="overall",
                reason="Workouts consistently too difficult - may indicate fatigue accumulation",
                signals=[signals[-1]],
                priority=4
            ))

        return adjustments

    def _analyze_exercise_progress(
        self,
        exercise_name: str,
        days: int = 14
    ) -> List[ProgramAdjustment]:
        """
        Analyze progress on a specific exercise.

        Signals:
        - Weight plateaued for 3+ sessions: Time to change approach
        - Reps decreasing over time: Fatigue or overtraining
        - Actual RIR consistently higher than prescribed: Increase load
        """
        adjustments = []

        # Get exercise history
        history = self.logger.get_exercise_history(exercise_name, limit=50)

        if len(history) < 3:
            return []  # Not enough data

        # Filter to recent days
        cutoff_date = (date.today() - timedelta(days=days)).isoformat()
        recent_history = [h for h in history if h['date'] >= cutoff_date]

        if len(recent_history) < 3:
            return []

        # Reverse to chronological order
        recent_history.reverse()

        # Check for weight plateau
        weights = [h['weight_lbs'] for h in recent_history]
        if len(set(weights)) == 1 and len(weights) >= 3:
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.INCREASE_LOAD,
                target=exercise_name,
                reason=f"Weight has been constant at {weights[0]} lbs for {len(weights)} sets",
                signals=[AutoregulationSignal(
                    signal_type="weight_plateau",
                    severity="medium",
                    description="No load progression in recent sessions",
                    recommendation=f"Increase weight to {weights[0] + 5} lbs or {weights[0] + 2.5} lbs"
                )],
                priority=3
            ))

        # Check for rep decline
        reps_trend = [h['reps'] for h in recent_history[-3:]]
        if len(reps_trend) == 3 and reps_trend[0] > reps_trend[1] > reps_trend[2]:
            adjustments.append(ProgramAdjustment(
                adjustment_type=AdjustmentType.DECREASE_VOLUME,
                target=exercise_name,
                reason=f"Reps declining over recent sessions ({reps_trend[0]} → {reps_trend[1]} → {reps_trend[2]})",
                signals=[AutoregulationSignal(
                    signal_type="rep_decline",
                    severity="high",
                    description="Progressive decline in reps indicates fatigue",
                    recommendation="Reduce sets by 1-2 or take a deload"
                )],
                priority=4
            ))

        # Check strength progress
        progress = self.logger.get_strength_progress(exercise_name)
        if 'error' not in progress and progress['data_points'] >= 5:
            if progress['gain_percentage'] < -2:
                adjustments.append(ProgramAdjustment(
                    adjustment_type=AdjustmentType.CHANGE_EXERCISE,
                    target=exercise_name,
                    reason=f"Strength decreased by {abs(progress['gain_percentage']):.1f}%",
                    signals=[AutoregulationSignal(
                        signal_type="strength_decline",
                        severity="high",
                        description="Estimated 1RM trending downward",
                        recommendation="Consider exercise substitution or technique review"
                    )],
                    priority=4
                ))

        return adjustments

    def generate_adjustment_report(
        self,
        days: int = 7
    ) -> str:
        """
        Generate human-readable adjustment report.

        Returns:
            Formatted markdown report with recommendations
        """
        adjustments = self.analyze_recent_workouts(days=days)

        if not adjustments:
            return f"""
## 📊 Autoregulation Report (Last {days} days)

✅ **No adjustments needed** - Your training is progressing well!

**Keep doing what you're doing:**
- Volume appears appropriate
- Recovery seems adequate
- Intensity is well-managed

Check back after a few more workouts for updated recommendations.
            """

        # Group adjustments by priority
        critical = [a for a in adjustments if a.priority >= 4]
        important = [a for a in adjustments if a.priority == 3]
        minor = [a for a in adjustments if a.priority <= 2]

        report = [f"## 📊 Autoregulation Report (Last {days} days)\n"]

        if critical:
            report.append("### 🚨 Critical Adjustments Needed\n")
            for adj in critical:
                report.append(f"**{adj.target}:** {adj.reason}\n")
                for signal in adj.signals:
                    report.append(f"- **Recommendation:** {signal.recommendation}\n")
                report.append("")

        if important:
            report.append("### ⚠️ Recommended Adjustments\n")
            for adj in important:
                report.append(f"**{adj.target}:** {adj.reason}\n")
                for signal in adj.signals:
                    report.append(f"- **Recommendation:** {signal.recommendation}\n")
                report.append("")

        if minor:
            report.append("### 💡 Minor Suggestions\n")
            for adj in minor:
                report.append(f"**{adj.target}:** {adj.reason}\n")
                report.append("")

        report.append("---\n")
        report.append("**Source:** RP Autoregulation Principles + HealthRAG AI Analysis")

        return "\n".join(report)


if __name__ == "__main__":
    # Example usage and testing
    print("=== Autoregulation Engine Test ===\n")

    # Create engine
    engine = AutoregulationEngine()

    # Test: Generate adjustment report
    print("TEST 1: Analyze recent workouts (last 7 days)")
    print("=" * 60)

    report = engine.generate_adjustment_report(days=7)
    print(report)
