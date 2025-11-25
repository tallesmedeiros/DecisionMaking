"""
Core module for Running Plan management.
Defines the main classes and data structures for running plans.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from dataclasses import dataclass, asdict, field


def round_to_nearest_5km(distance_km: float) -> float:
    """Round distance to nearest 5km increment."""
    if distance_km == 0:
        return 0
    return max(5, round(distance_km / 5) * 5)


def round_to_nearest_30min(minutes: float) -> int:
    """Round time to nearest 30min increment."""
    if minutes == 0:
        return 0
    return max(30, round(minutes / 30) * 30)


def round_to_nearest_5min(minutes: float) -> int:
    """Round time to nearest 5-minute increment."""
    if minutes == 0:
        return 0
    return int(round(minutes / 5) * 5)


@dataclass
class WorkoutSegment:
    """Represents a segment of a workout (warmup, intervals, cooldown, etc)."""
    name: str  # e.g., "Warmup", "Work Interval", "Recovery", "Cooldown"
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    pace_per_km: Optional[str] = None  # Format: "MM:SS"
    repetitions: int = 1
    description: str = ""

    def to_compact_str(self) -> str:
        """Return compact string representation for visual output."""
        if "Aquecimento" in self.name or "Warmup" in self.name:
            if self.distance_km:
                return f"{self.distance_km}km aquec"
            return "aquec"
        elif "Desaquecimento" in self.name or "Cooldown" in self.name:
            if self.distance_km:
                return f"{self.distance_km}km volta calma"
            return "volta calma"
        elif "Recuperação" in self.name or "Recovery" in self.name:
            if self.duration_minutes:
                return f"{self.duration_minutes}min rec"
            return "rec"
        elif "Tiro" in self.name or "Interval" in self.name:
            result = ""
            if self.repetitions > 1:
                result = f"{self.repetitions}x"
            if self.distance_km:
                # Convert to meters if less than 1km
                if self.distance_km < 1:
                    meters = int(self.distance_km * 1000)
                    result += f"{meters}m"
                else:
                    result += f"{self.distance_km}km"
            if self.pace_per_km:
                result += f" @ {self.pace_per_km}/km"
            if self.duration_minutes and not self.pace_per_km:
                result += f" {self.duration_minutes}min"
            if self.repetitions > 1 and self.duration_minutes:
                result += f" c/ {self.duration_minutes}min rec"
            return result
        elif "Tempo" in self.name or "Limiar" in self.name:
            result = ""
            if self.distance_km:
                result += f"{self.distance_km}km"
            if self.pace_per_km:
                result += f" @ {self.pace_per_km}/km"
            return result
        elif "Fartlek" in self.name:
            if self.distance_km:
                return f"{self.distance_km}km fartlek"
            return "fartlek"
        else:
            # Generic format
            result = ""
            if self.distance_km:
                result += f"{self.distance_km}km"
            if self.pace_per_km:
                result += f" @ {self.pace_per_km}/km"
            return result if result else self.name

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
    total_minutes: Optional[int] = None

    # Session logistics
    warmup_minutes: int = 0
    cooldown_minutes: int = 0
    commute_minutes: int = 0
    max_session_minutes: Optional[int] = None
    surface_options: List[str] = field(default_factory=list)

    # Zone information
    training_zone: Optional[str] = None  # e.g., "easy", "threshold", "interval"

    def add_segment(self, segment: WorkoutSegment):
        """Add a segment to the workout."""
        self.segments.append(segment)

    def has_detailed_structure(self) -> bool:
        """Check if workout has detailed segment structure."""
        return len(self.segments) > 0

    def get_emoji(self) -> str:
        """Get emoji for workout type."""
        emoji_map = {
            "Easy Run": "🟢",
            "Long Run": "🟢",
            "Tempo Run": "🟠",
            "Interval Training": "🔴",
            "Fartlek": "🟡",
            "Rest": "😴",
            "Cross Training": "🔵"
        }
        return emoji_map.get(self.type, "⚪")

    def get_type_label(self) -> str:
        """Get short label for workout type."""
        label_map = {
            "Easy Run": "Fácil",
            "Long Run": "Longão",
            "Tempo Run": "Tempo",
            "Interval Training": "Intervalos",
            "Fartlek": "Fartlek",
            "Rest": "Descanso",
            "Cross Training": "Cross"
        }
        return label_map.get(self.type, self.type)

    def to_visual_str(self, date: Optional[datetime] = None) -> str:
        """Return compact visual representation with emojis."""
        if self.type == "Rest":
            if date:
                date_str = f"{self.day.capitalize()} ({date.strftime('%d/%m')})"
                return f"  📍 {date_str}: {self.get_emoji()} {self.get_type_label()}"
            return f"  📍 {self.day}: {self.get_emoji()} {self.get_type_label()}"

        # Build compact workout description
        parts = []

        if self.has_detailed_structure():
            # Compact format with segments
            for segment in self.segments:
                compact = segment.to_compact_str()
                if compact:
                    parts.append(compact)
            workout_desc = " + ".join(parts)
        else:
            # Simple format without segments
            if self.distance_km:
                workout_desc = f"{self.distance_km}km"
            elif self.duration_minutes:
                workout_desc = f"{self.duration_minutes}min"
            else:
                workout_desc = ""

            if self.target_pace:
                workout_desc += f" @ {self.target_pace}/km"

        # Format with date if provided
        if date:
            date_str = f"{self.day.capitalize()} ({date.strftime('%d/%m')})"
        else:
            date_str = self.day

        # Add time estimate if available
        time_str = ""
        if self.total_time_estimated:
            time_str = f" [{self.total_time_estimated}]"

        return f"  📍 {date_str}: {self.get_emoji()} {self.get_type_label()}: {workout_desc}{time_str}"

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

    def to_visual_str(self, start_date: Optional[datetime] = None) -> str:
        """Return compact visual representation of the week."""
        self.calculate_total_distance()

        # Calculate week start date if plan has a start date
        week_start = None
        if start_date:
            # Week starts on a Monday (assuming plan starts on Monday)
            days_offset = (self.week_number - 1) * 7
            week_start = start_date + timedelta(days=days_offset)

        # Header
        result = f"\n{'='*70}\n"
        result += f"📅 SEMANA {self.week_number}"
        if week_start:
            week_end = week_start + timedelta(days=6)
            result += f" ({week_start.strftime('%d/%m')} a {week_end.strftime('%d/%m')})"
        result += f" | 📏 {self.total_distance_km}km total\n"

        if self.notes:
            result += f"💡 {self.notes}\n"

        result += f"{'='*70}\n"

        # Workouts in visual format
        days_map = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
            "Friday": 4, "Saturday": 5, "Sunday": 6
        }

        for workout in self.workouts:
            workout_date = None
            if week_start and workout.day in days_map:
                workout_date = week_start + timedelta(days=days_map[workout.day])
            result += workout.to_visual_str(workout_date) + "\n"

        return result

    def get_zone_distribution(self) -> Dict[str, float]:
        """
        Get the distribution of training zones for this week.

        Returns:
            Dictionary mapping zone names to total km in that zone
        """
        distribution = {
            'easy': 0.0,
            'marathon': 0.0,
            'threshold': 0.0,
            'interval': 0.0,
            'repetition': 0.0,
            'rest': 0.0
        }

        for workout in self.workouts:
            if workout.type == "Rest" or not workout.distance_km:
                continue

            zone = workout.training_zone if workout.training_zone else 'easy'

            # Normalize zone names
            if zone in ['Easy Run', 'Long Run']:
                zone = 'easy'
            elif zone == 'Tempo Run':
                zone = 'threshold'
            elif zone == 'Interval Training':
                zone = 'interval'
            elif zone == 'Fartlek':
                zone = 'threshold'

            if zone in distribution:
                distribution[zone] += workout.distance_km

        return distribution

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

    def to_visual_str(self, show_all_weeks: bool = True, week_range: tuple = None) -> str:
        """
        Return visual representation of the plan.

        Args:
            show_all_weeks: If True, show all weeks. If False, show summary.
            week_range: Tuple (start, end) to show specific week range.
        """
        result = f"\n{'='*70}\n"
        result += f"🏃‍♂️ PLANO DE TREINO: {self.name}\n"
        result += f"{'='*70}\n"
        result += f"🎯 Meta: {self.goal}\n"
        result += f"📊 Nível: {self.level.capitalize()}\n"
        result += f"📅 Duração: {self.weeks} semanas\n"
        result += f"🗓️  Dias de treino: {self.days_per_week} dias/semana\n"

        if self.start_date:
            result += f"🚀 Início: {self.start_date.strftime('%d/%m/%Y (%A)')}\n"
            race_date = self.get_race_date()
            if race_date:
                result += f"🏁 Prova: {race_date.strftime('%d/%m/%Y (%A)')}\n"

        # Calculate total distance
        total_km = sum(w.total_distance_km for w in self.schedule)
        result += f"📏 Kilometragem total: {total_km:.1f}km\n"
        result += f"{'='*70}\n"

        # Determine which weeks to show
        if week_range:
            start_week, end_week = week_range
            weeks_to_show = [w for w in self.schedule if start_week <= w.week_number <= end_week]
        elif show_all_weeks:
            weeks_to_show = self.schedule
        else:
            # Show first 2, one from middle, and last 2 weeks as summary
            if len(self.schedule) <= 5:
                weeks_to_show = self.schedule
            else:
                middle_week = len(self.schedule) // 2
                weeks_to_show = (
                    self.schedule[:2] +
                    [self.schedule[middle_week]] +
                    self.schedule[-2:]
                )

        # Show weeks
        for week in weeks_to_show:
            result += week.to_visual_str(self.start_date)
            result += "\n"

        if not show_all_weeks and not week_range and len(self.schedule) > 5:
            result += f"\n💡 Use .to_visual_str(show_all_weeks=True) para ver todas as semanas\n"
            result += f"💡 Ou .to_visual_str(week_range=(3, 6)) para ver semanas específicas\n"

        return result

    def print_visual(self, **kwargs):
        """Print visual representation of the plan."""
        print(self.to_visual_str(**kwargs))

    def get_weekly_volumes(self) -> List[float]:
        """
        Get weekly volumes (total km) for all weeks in the plan.

        Returns:
            List of weekly distances in km
        """
        return [week.total_distance_km for week in self.schedule]

    def get_zone_distributions(self) -> List[Dict[str, float]]:
        """
        Get zone distribution for each week.

        Returns:
            List of dictionaries, each mapping zone names to km
        """
        return [week.get_zone_distribution() for week in self.schedule]

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
