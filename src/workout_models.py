"""
Workout Data Models for HealthRAG

Handles workout sessions, exercise sets, and progress tracking.
Supports adaptive coaching with RIR (Reps In Reserve) tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from enum import Enum


class ExerciseProtocol(Enum):
    """Training protocols for different exercise types"""
    COMPOUND_STRENGTH = "compound_strength"  # 3-4 sets × 6-10 reps @ 1-2 RIR
    COMPOUND_HYPERTROPHY = "compound_hypertrophy"  # 3-4 sets × 8-12 reps @ 1-2 RIR
    ISOLATION = "isolation"  # 3-4 sets × 10-15 reps @ 2-3 RIR
    ACCESSORY = "accessory"  # 2-3 sets × 12-20 reps @ 2-4 RIR


@dataclass
class ExerciseProtocolSpec:
    """Specification for an exercise protocol"""
    sets_min: int
    sets_max: int
    reps_min: int
    reps_max: int
    rir_min: int
    rir_max: int

    def format(self) -> str:
        """Format as string for display"""
        sets = f"{self.sets_min}-{self.sets_max}" if self.sets_min != self.sets_max else str(self.sets_min)
        reps = f"{self.reps_min}-{self.reps_max}"
        rir = f"{self.rir_min}-{self.rir_max}" if self.rir_min != self.rir_max else str(self.rir_min)
        return f"{sets} sets × {reps} reps @ {rir} RIR"


# Protocol specifications (based on Jeff Nippard's recommendations)
PROTOCOL_SPECS = {
    ExerciseProtocol.COMPOUND_STRENGTH: ExerciseProtocolSpec(
        sets_min=3, sets_max=4, reps_min=6, reps_max=10, rir_min=1, rir_max=2
    ),
    ExerciseProtocol.COMPOUND_HYPERTROPHY: ExerciseProtocolSpec(
        sets_min=3, sets_max=4, reps_min=8, reps_max=12, rir_min=1, rir_max=2
    ),
    ExerciseProtocol.ISOLATION: ExerciseProtocolSpec(
        sets_min=3, sets_max=4, reps_min=10, reps_max=15, rir_min=2, rir_max=3
    ),
    ExerciseProtocol.ACCESSORY: ExerciseProtocolSpec(
        sets_min=2, sets_max=3, reps_min=12, reps_max=20, rir_min=2, rir_max=4
    ),
}


@dataclass
class WorkoutSet:
    """
    Single set of an exercise.

    Attributes:
        set_number: Set number within the exercise (1, 2, 3, etc.)
        weight_lbs: Weight used in pounds
        reps_completed: Number of reps completed
        rir: Reps In Reserve (how many more reps could have been done)
        timestamp: When this set was completed
        set_id: Database ID (optional, assigned after save)
    """
    set_number: int
    weight_lbs: float
    reps_completed: int
    rir: int
    timestamp: datetime = field(default_factory=datetime.now)
    set_id: Optional[int] = None
    exercise_name: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'set_number': self.set_number,
            'weight_lbs': self.weight_lbs,
            'reps_completed': self.reps_completed,
            'rir': self.rir,
            'timestamp': self.timestamp.isoformat(),
            'set_id': self.set_id,
            'exercise_name': self.exercise_name,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkoutSet':
        """Create from dictionary"""
        data = data.copy()
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class ExerciseLog:
    """
    Log of an exercise within a workout session.

    Attributes:
        exercise_name: Name of exercise (matches exercise_database.py)
        target_sets: Target number of sets
        target_reps_min: Minimum target reps
        target_reps_max: Maximum target reps
        target_rir: Target RIR (Reps In Reserve)
        sets: List of completed sets
        notes: Optional notes about exercise execution
        log_id: Database ID (optional, assigned after save)
    """
    exercise_name: str
    target_sets: int
    target_reps_min: int
    target_reps_max: int
    target_rir: int
    sets: List[WorkoutSet] = field(default_factory=list)
    notes: Optional[str] = None
    log_id: Optional[int] = None

    def add_set(self, weight_lbs: float, reps_completed: int, rir: int) -> WorkoutSet:
        """Add a set to this exercise"""
        set_number = len(self.sets) + 1
        new_set = WorkoutSet(
            set_number=set_number,
            weight_lbs=weight_lbs,
            reps_completed=reps_completed,
            rir=rir
        )
        self.sets.append(new_set)
        return new_set

    def is_complete(self) -> bool:
        """Check if target sets are completed"""
        return len(self.sets) >= self.target_sets

    def get_average_rir(self) -> float:
        """Calculate average RIR across all sets"""
        if not self.sets:
            return 0.0
        return sum(s.rir for s in self.sets) / len(self.sets)

    def get_total_volume(self) -> float:
        """Calculate total volume (sets × reps × weight)"""
        return sum(s.weight_lbs * s.reps_completed for s in self.sets)

    def get_total_sets(self) -> int:
        """Total number of sets logged."""
        return len(self.sets)

    def get_total_reps(self) -> int:
        """Total repetitions completed across all sets."""
        return sum(s.reps_completed for s in self.sets)

    def get_average_weight(self) -> float:
        """Average weight used across logged sets."""
        if not self.sets:
            return 0.0
        return sum(s.weight_lbs for s in self.sets) / len(self.sets)

    def get_average_reps(self) -> float:
        """Average repetitions performed."""
        if not self.sets:
            return 0.0
        return sum(s.reps_completed for s in self.sets) / len(self.sets)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'exercise_name': self.exercise_name,
            'target_sets': self.target_sets,
            'target_reps_min': self.target_reps_min,
            'target_reps_max': self.target_reps_max,
            'target_rir': self.target_rir,
            'sets': [s.to_dict() for s in self.sets],
            'notes': self.notes,
            'log_id': self.log_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExerciseLog':
        """Create from dictionary"""
        data = data.copy()
        if 'sets' in data:
            data['sets'] = [WorkoutSet.from_dict(s) for s in data['sets']]
        return cls(**data)


@dataclass
class WorkoutSession:
    """
    Complete workout session.

    Attributes:
        date: Date of workout
        muscle_group: Primary muscle group(s) trained (e.g., "Chest & Triceps")
        exercises: List of exercise logs
        duration_minutes: How long workout took
        completed: Whether workout was completed
        notes: Optional session notes
        session_id: Database ID (optional, assigned after save)
    """
    date: date
    muscle_group: str
    exercises: List[ExerciseLog] = field(default_factory=list)
    duration_minutes: Optional[int] = None
    completed: bool = False
    notes: Optional[str] = None
    session_id: Optional[int] = None

    def add_exercise(self,
                     exercise_name: str,
                     target_sets: int,
                     target_reps_min: int,
                     target_reps_max: int,
                     target_rir: int) -> ExerciseLog:
        """Add an exercise to this session"""
        exercise_log = ExerciseLog(
            exercise_name=exercise_name,
            target_sets=target_sets,
            target_reps_min=target_reps_min,
            target_reps_max=target_reps_max,
            target_rir=target_rir
        )
        self.exercises.append(exercise_log)
        return exercise_log

    def is_complete(self) -> bool:
        """Check if all exercises are complete"""
        if not self.exercises:
            return False
        return all(ex.is_complete() for ex in self.exercises)

    def get_total_sets(self) -> int:
        """Get total sets completed in session"""
        return sum(len(ex.sets) for ex in self.exercises)

    def get_total_volume(self) -> float:
        """Get total volume for session"""
        return sum(ex.get_total_volume() for ex in self.exercises)

    def get_exercise(self, exercise_name: str) -> Optional[ExerciseLog]:
        """Retrieve exercise log by name (case-insensitive)."""
        target = exercise_name.lower()
        for exercise in self.exercises:
            if exercise.exercise_name.lower() == target:
                return exercise
        return None

    def get_summary(self) -> str:
        """Generate human-readable session summary."""
        total_sets = self.get_total_sets()
        total_volume = self.get_total_volume()
        parts = [
            f"Session: {self.muscle_group}",
            f"Date: {self.date.isoformat()}",
            f"Completed Sets: {total_sets} sets",
            f"Total Volume: {total_volume:.0f} lbs"
        ]
        if self.duration_minutes:
            parts.append(f"Duration: {self.duration_minutes} min")
        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'date': self.date.isoformat(),
            'muscle_group': self.muscle_group,
            'exercises': [ex.to_dict() for ex in self.exercises],
            'duration_minutes': self.duration_minutes,
            'completed': self.completed,
            'notes': self.notes,
            'session_id': self.session_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkoutSession':
        """Create from dictionary"""
        data = data.copy()
        if 'date' in data and isinstance(data['date'], str):
            data['date'] = date.fromisoformat(data['date'])
        if 'exercises' in data:
            data['exercises'] = [ExerciseLog.from_dict(ex) for ex in data['exercises']]
        return cls(**data)


@dataclass
class ExerciseProgress:
    """
    Progress tracking for a specific exercise.

    Attributes:
        exercise_name: Name of exercise
        first_logged: Date first logged
        last_logged: Date last performed
        best_weight: Personal record weight
        best_reps_at_weight: Reps completed at best weight
        total_volume: Cumulative volume (all time)
        total_sets: Total sets performed (all time)
        avg_rir: Average RIR across all sets
    """
    exercise_name: str
    first_logged: date
    last_logged: date
    best_weight: float = 0.0
    best_reps_at_weight: int = 0
    total_volume: float = 0.0
    total_sets: int = 0
    avg_rir: float = 0.0
    total_rir: float = 0.0

    def update_from_log(self, exercise_log: ExerciseLog, session_date: date):
        """Update progress from a new exercise log"""
        self.last_logged = session_date

        # Update best weight
        for set_log in exercise_log.sets:
            if set_log.weight_lbs > self.best_weight:
                self.best_weight = set_log.weight_lbs
                self.best_reps_at_weight = set_log.reps_completed
            elif set_log.weight_lbs == self.best_weight and set_log.reps_completed > self.best_reps_at_weight:
                self.best_reps_at_weight = set_log.reps_completed

        # Update volume and sets
        self.total_volume += exercise_log.get_total_volume()
        self.total_sets += len(exercise_log.sets)

        # Update cumulative RIR and average
        self.total_rir += sum(s.rir for s in exercise_log.sets)
        self.avg_rir = self.total_rir / self.total_sets if self.total_sets > 0 else 0.0

    def days_since_first_logged(self, on_date: Optional[date] = None) -> int:
        """Days since the exercise was first logged."""
        reference = on_date or date.today()
        return (reference - self.first_logged).days

    def days_since_last_logged(self, on_date: Optional[date] = None) -> int:
        """Days since the exercise was last logged."""
        reference = on_date or date.today()
        return (reference - self.last_logged).days


if __name__ == "__main__":
    # Example usage and testing
    print("=== Workout Models Test ===\n")

    # Create a workout session
    session = WorkoutSession(
        date=date.today(),
        muscle_group="Chest & Triceps"
    )

    # Add exercise
    bench_press = session.add_exercise(
        exercise_name="barbell_bench_press",
        target_sets=4,
        target_reps_min=8,
        target_reps_max=12,
        target_rir=2
    )

    # Log sets
    bench_press.add_set(weight_lbs=225, reps_completed=12, rir=2)
    bench_press.add_set(weight_lbs=225, reps_completed=10, rir=2)
    bench_press.add_set(weight_lbs=225, reps_completed=9, rir=3)
    bench_press.add_set(weight_lbs=225, reps_completed=8, rir=3)

    print(f"Exercise: {bench_press.exercise_name}")
    print(f"Target: {bench_press.target_sets} sets × {bench_press.target_reps_min}-{bench_press.target_reps_max} @ {bench_press.target_rir} RIR")
    print(f"Completed: {len(bench_press.sets)} sets")
    print(f"Average RIR: {bench_press.get_average_rir():.1f}")
    print(f"Total Volume: {bench_press.get_total_volume():.0f} lbs")
    print(f"Complete: {bench_press.is_complete()}")

    print(f"\nSession complete: {session.is_complete()}")
    print(f"Total sets: {session.get_total_sets()}")
    print(f"Total volume: {session.get_total_volume():.0f} lbs")

    # Test serialization
    print("\n=== Serialization Test ===")
    session_dict = session.to_dict()
    restored_session = WorkoutSession.from_dict(session_dict)
    print(f"✅ Serialization works: {restored_session.muscle_group}")
