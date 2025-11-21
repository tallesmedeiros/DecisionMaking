"""
Core module for Running Plan management.
Defines the main classes and data structures for running plans.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from dataclasses import dataclass, asdict, field


@dataclass
class WorkoutSegment:
    """Represents a segment of a workout (warmup, intervals, cooldown, etc)."""
    name: str  # e.g., "Warmup", "Work Interval", "Recovery", "Cooldown"
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    pace_per_km: Optional[str] = None  # Format: "MM:SS"
    repetitions: int = 1
    description: str = ""

    def __str__(self):
        result = f"  • {self.name}"
        if self.repetitions > 1:
            result = f"  • {self.repetitions}x {self.name}"

        details = []
        if self.distance_km:
            details.append(f"{self.distance_km} km")
        if self.duration_minutes:
            details.append(f"{self.duration_minutes} min")
        if self.pace_per_km:
            details.append(f"@ {self.pace_per_km}/km")

        if details:
            result += f": {', '.join(details)}"

        if self.description:
            result += f"\n    {self.description}"

        return result


@dataclass
class Workout:
    """Represents a single workout session with detailed structure."""
    day: str
    type: str  # e.g., "Easy Run", "Long Run", "Interval", "Rest", "Cross Training"
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    description: str = ""

    # Enhanced fields for detailed workout structure
    target_pace: Optional[str] = None  # Target pace for main work (MM:SS/km)
    segments: List[WorkoutSegment] = field(default_factory=list)
    total_time_estimated: Optional[str] = None  # HH:MM:SS or MM:SS

    # Zone information
    training_zone: Optional[str] = None  # e.g., "easy", "threshold", "interval"

    def add_segment(self, segment: WorkoutSegment):
        """Add a segment to the workout."""
        self.segments.append(segment)

    def has_detailed_structure(self) -> bool:
        """Check if workout has detailed segment structure."""
        return len(self.segments) > 0

    def __str__(self):
        result = f"{self.day}: {self.type}"

        if self.distance_km:
            result += f" - {self.distance_km} km"
        if self.total_time_estimated:
            result += f" ({self.total_time_estimated})"
        elif self.duration_minutes:
            result += f" ({self.duration_minutes} min)"

        if self.target_pace:
            result += f" @ {self.target_pace}/km"

        if self.training_zone:
            result += f" [{self.training_zone.upper()}]"

        if self.description:
            result += f"\n  {self.description}"

        # Show detailed segments if available
        if self.has_detailed_structure():
            result += "\n  Estrutura do Treino:"
            for segment in self.segments:
                result += "\n" + str(segment)

        return result


@dataclass
class Week:
    """Represents a week of training."""
    week_number: int
    workouts: List[Workout]
    total_distance_km: float = 0.0
    notes: str = ""

    def calculate_total_distance(self):
        """Calculate total distance for the week."""
        self.total_distance_km = round(sum(
            w.distance_km for w in self.workouts if w.distance_km
        ), 1)
        return self.total_distance_km

    def __str__(self):
        self.calculate_total_distance()
        result = f"\n=== Week {self.week_number} ===\n"
        result += f"Total Distance: {self.total_distance_km} km\n"
        if self.notes:
            result += f"Notes: {self.notes}\n"
        result += "\n"
        for workout in self.workouts:
            result += str(workout) + "\n"
        return result


class RunningPlan:
    """Main class for managing a running plan."""

    def __init__(
        self,
        name: str,
        goal: str,
        level: str,
        weeks: int,
        days_per_week: int = 4
    ):
        """
        Initialize a running plan.

        Args:
            name: Name of the plan
            goal: Goal race (e.g., "5K", "10K", "Half Marathon", "Marathon")
            level: Training level ("beginner", "intermediate", "advanced")
            weeks: Number of weeks in the plan
            days_per_week: Number of running days per week
        """
        self.name = name
        self.goal = goal
        self.level = level.lower()
        self.weeks = weeks
        self.days_per_week = days_per_week
        self.schedule: List[Week] = []
        self.start_date: Optional[datetime] = None
        self.created_date = datetime.now()

    def add_week(self, week: Week):
        """Add a week to the training schedule."""
        self.schedule.append(week)

    def get_week(self, week_number: int) -> Optional[Week]:
        """Get a specific week from the schedule."""
        for week in self.schedule:
            if week.week_number == week_number:
                return week
        return None

    def set_start_date(self, date: datetime):
        """Set the start date for the plan."""
        self.start_date = date

    def get_race_date(self) -> Optional[datetime]:
        """Calculate the race date based on start date and plan duration."""
        if self.start_date:
            return self.start_date + timedelta(weeks=self.weeks)
        return None

    def to_dict(self) -> Dict:
        """Convert the plan to a dictionary for serialization."""
        return {
            "name": self.name,
            "goal": self.goal,
            "level": self.level,
            "weeks": self.weeks,
            "days_per_week": self.days_per_week,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "created_date": self.created_date.isoformat(),
            "schedule": [
                {
                    "week_number": week.week_number,
                    "total_distance_km": week.total_distance_km,
                    "notes": week.notes,
                    "workouts": [asdict(w) for w in week.workouts]
                }
                for week in self.schedule
            ]
        }

    def save_to_file(self, filename: str):
        """Save the plan to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_file(cls, filename: str) -> 'RunningPlan':
        """Load a plan from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        plan = cls(
            name=data["name"],
            goal=data["goal"],
            level=data["level"],
            weeks=data["weeks"],
            days_per_week=data["days_per_week"]
        )

        if data.get("start_date"):
            plan.start_date = datetime.fromisoformat(data["start_date"])

        plan.created_date = datetime.fromisoformat(data["created_date"])

        # Reconstruct schedule
        for week_data in data["schedule"]:
            workouts = []
            for w_data in week_data["workouts"]:
                # Handle segments if they exist
                segments_data = w_data.pop('segments', [])
                segments = [WorkoutSegment(**s) for s in segments_data]
                workout = Workout(**w_data)
                workout.segments = segments
                workouts.append(workout)

            week = Week(
                week_number=week_data["week_number"],
                workouts=workouts,
                total_distance_km=week_data["total_distance_km"],
                notes=week_data.get("notes", "")
            )
            plan.add_week(week)

        return plan

    def __str__(self):
        result = f"\n{'='*50}\n"
        result += f"Running Plan: {self.name}\n"
        result += f"Goal: {self.goal}\n"
        result += f"Level: {self.level.capitalize()}\n"
        result += f"Duration: {self.weeks} weeks\n"
        result += f"Training Days: {self.days_per_week} days/week\n"

        if self.start_date:
            result += f"Start Date: {self.start_date.strftime('%Y-%m-%d')}\n"
            race_date = self.get_race_date()
            if race_date:
                result += f"Race Date: {race_date.strftime('%Y-%m-%d')}\n"

        result += f"{'='*50}\n"

        for week in self.schedule:
            result += str(week)

        return result
