"""
Plan Generator module for creating training schedules.
Generates running plans based on goal, level, and duration.
"""
from running_plan import RunningPlan, Week, Workout
from typing import List


class PlanGenerator:
    """Generates running training plans based on user preferences."""

    # Base weekly mileage targets (km) for different goals and levels
    GOAL_TARGETS = {
        "5K": {"beginner": 20, "intermediate": 30, "advanced": 40},
        "10K": {"beginner": 30, "intermediate": 45, "advanced": 60},
        "Half Marathon": {"beginner": 40, "intermediate": 60, "advanced": 80},
        "Marathon": {"beginner": 50, "intermediate": 75, "advanced": 100},
    }

    DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    @classmethod
    def generate_plan(
        cls,
        name: str,
        goal: str,
        level: str,
        weeks: int = None,
        days_per_week: int = 4
    ) -> RunningPlan:
        """
        Generate a complete running plan.

        Args:
            name: Name of the plan
            goal: Goal race (e.g., "5K", "10K", "Half Marathon", "Marathon")
            level: Training level ("beginner", "intermediate", "advanced")
            weeks: Number of weeks (default based on goal)
            days_per_week: Number of running days per week

        Returns:
            A complete RunningPlan object
        """
        # Set default weeks based on goal if not provided
        if weeks is None:
            weeks = cls._get_default_weeks(goal)

        plan = RunningPlan(name, goal, level, weeks, days_per_week)

        # Generate weekly schedule
        for week_num in range(1, weeks + 1):
            week = cls._generate_week(week_num, goal, level, weeks, days_per_week)
            plan.add_week(week)

        return plan

    @classmethod
    def _get_default_weeks(cls, goal: str) -> int:
        """Get default plan duration based on goal."""
        defaults = {
            "5K": 8,
            "10K": 10,
            "Half Marathon": 12,
            "Marathon": 16,
        }
        return defaults.get(goal, 12)

    @classmethod
    def _generate_week(
        cls,
        week_number: int,
        goal: str,
        level: str,
        total_weeks: int,
        days_per_week: int
    ) -> Week:
        """Generate a single week of training."""
        workouts = []

        # Calculate weekly distance based on progression
        target_distance = cls.GOAL_TARGETS.get(goal, {}).get(level, 30)

        # Progressive build: gradually increase to peak, then taper
        if week_number <= total_weeks * 0.7:  # Build phase
            weekly_distance = target_distance * (week_number / (total_weeks * 0.7))
        elif week_number <= total_weeks - 2:  # Maintenance phase
            weekly_distance = target_distance
        else:  # Taper phase
            taper_factor = 0.7 if week_number == total_weeks - 1 else 0.5
            weekly_distance = target_distance * taper_factor

        # Distribute workouts across the week
        if days_per_week == 3:
            workouts = cls._generate_3_day_week(week_number, weekly_distance, level, total_weeks)
        elif days_per_week == 4:
            workouts = cls._generate_4_day_week(week_number, weekly_distance, level, total_weeks)
        elif days_per_week == 5:
            workouts = cls._generate_5_day_week(week_number, weekly_distance, level, total_weeks)
        elif days_per_week == 6:
            workouts = cls._generate_6_day_week(week_number, weekly_distance, level, total_weeks)
        else:
            raise ValueError(f"Unsupported days_per_week: {days_per_week}")

        # Add notes for special weeks
        notes = ""
        if week_number == 1:
            notes = "Welcome to your training plan! Start easy and focus on consistency."
        elif week_number == total_weeks:
            notes = "Race week! Keep runs short and easy. Trust your training!"
        elif week_number == total_weeks - 1:
            notes = "Taper week - reduce volume to arrive fresh for race day."
        elif week_number % 4 == 0 and week_number < total_weeks - 2:
            notes = "Recovery week - slightly reduced volume to absorb training."

        week = Week(week_number=week_number, workouts=workouts, notes=notes)
        week.calculate_total_distance()
        return week

    @classmethod
    def _generate_3_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int) -> List[Workout]:
        """Generate workouts for a 3-day training week."""
        workouts = []

        # Easy run
        easy_distance = weekly_distance * 0.3
        workouts.append(Workout(
            day="Tuesday",
            type="Easy Run",
            distance_km=round(easy_distance, 1),
            description="Comfortable pace, conversational effort"
        ))

        # Tempo or interval
        quality_distance = weekly_distance * 0.25
        if week_num <= 3:
            workouts.append(Workout(
                day="Thursday",
                type="Easy Run",
                distance_km=round(quality_distance, 1),
                description="Build your aerobic base"
            ))
        else:
            workouts.append(Workout(
                day="Thursday",
                type="Tempo Run",
                distance_km=round(quality_distance, 1),
                description="Comfortably hard pace for middle miles"
            ))

        # Long run
        long_distance = weekly_distance * 0.45
        workouts.append(Workout(
            day="Saturday",
            type="Long Run",
            distance_km=round(long_distance, 1),
            description="Build endurance at easy pace"
        ))

        # Add rest days
        for day in ["Monday", "Wednesday", "Friday", "Sunday"]:
            workouts.append(Workout(day=day, type="Rest", description="Recovery day"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_4_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int) -> List[Workout]:
        """Generate workouts for a 4-day training week."""
        workouts = []

        # Easy run 1
        easy_distance_1 = weekly_distance * 0.25
        workouts.append(Workout(
            day="Tuesday",
            type="Easy Run",
            distance_km=round(easy_distance_1, 1),
            description="Comfortable pace, conversational effort"
        ))

        # Tempo, intervals, or easy depending on week
        quality_distance = weekly_distance * 0.22
        if week_num <= 2:
            workouts.append(Workout(
                day="Thursday",
                type="Easy Run",
                distance_km=round(quality_distance, 1),
                description="Build your aerobic base"
            ))
        elif week_num % 2 == 0:
            workouts.append(Workout(
                day="Thursday",
                type="Interval Training",
                distance_km=round(quality_distance, 1),
                description="Speed work: warm up, intervals at 5K pace, cool down"
            ))
        else:
            workouts.append(Workout(
                day="Thursday",
                type="Tempo Run",
                distance_km=round(quality_distance, 1),
                description="Sustained effort at comfortably hard pace"
            ))

        # Easy run 2
        easy_distance_2 = weekly_distance * 0.18
        workouts.append(Workout(
            day="Friday",
            type="Easy Run",
            distance_km=round(easy_distance_2, 1),
            description="Short recovery run at easy pace"
        ))

        # Long run
        long_distance = weekly_distance * 0.35
        workouts.append(Workout(
            day="Sunday",
            type="Long Run",
            distance_km=round(long_distance, 1),
            description="Build endurance at easy pace"
        ))

        # Add rest days
        for day in ["Monday", "Wednesday", "Saturday"]:
            workouts.append(Workout(day=day, type="Rest", description="Recovery day"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_5_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int) -> List[Workout]:
        """Generate workouts for a 5-day training week."""
        workouts = []

        # Distribution for 5-day week
        distances = {
            "easy1": weekly_distance * 0.20,
            "easy2": weekly_distance * 0.18,
            "easy3": weekly_distance * 0.15,
            "quality": weekly_distance * 0.20,
            "long": weekly_distance * 0.27
        }

        workouts.append(Workout(
            day="Monday",
            type="Easy Run",
            distance_km=round(distances["easy1"], 1),
            description="Start week with comfortable pace"
        ))

        workouts.append(Workout(
            day="Tuesday",
            type="Easy Run",
            distance_km=round(distances["easy2"], 1),
            description="Recovery pace"
        ))

        # Quality workout
        if week_num <= 2:
            workout_type = "Easy Run"
            description = "Build aerobic base"
        elif week_num % 2 == 0:
            workout_type = "Interval Training"
            description = "Speed work: 400m-800m repeats at 5K pace"
        else:
            workout_type = "Tempo Run"
            description = "Sustained effort at threshold pace"

        workouts.append(Workout(
            day="Thursday",
            type=workout_type,
            distance_km=round(distances["quality"], 1),
            description=description
        ))

        workouts.append(Workout(
            day="Friday",
            type="Easy Run",
            distance_km=round(distances["easy3"], 1),
            description="Short recovery run"
        ))

        workouts.append(Workout(
            day="Sunday",
            type="Long Run",
            distance_km=round(distances["long"], 1),
            description="Build endurance at conversational pace"
        ))

        # Rest days
        for day in ["Wednesday", "Saturday"]:
            workouts.append(Workout(day=day, type="Rest", description="Recovery day"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_6_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int) -> List[Workout]:
        """Generate workouts for a 6-day training week."""
        workouts = []

        # Distribution for 6-day week
        distances = {
            "easy1": weekly_distance * 0.18,
            "easy2": weekly_distance * 0.16,
            "easy3": weekly_distance * 0.14,
            "easy4": weekly_distance * 0.12,
            "quality": weekly_distance * 0.18,
            "long": weekly_distance * 0.22
        }

        workouts.append(Workout(
            day="Monday",
            type="Easy Run",
            distance_km=round(distances["easy1"], 1),
            description="Start week at comfortable pace"
        ))

        workouts.append(Workout(
            day="Tuesday",
            type="Easy Run",
            distance_km=round(distances["easy2"], 1),
            description="Easy aerobic pace"
        ))

        # Quality workout
        if week_num <= 2:
            workout_type = "Easy Run"
            description = "Building base fitness"
        elif week_num % 3 == 0:
            workout_type = "Fartlek"
            description = "Play with pace: alternate fast/easy segments"
        elif week_num % 3 == 1:
            workout_type = "Interval Training"
            description = "Track work: 400m-1000m repeats at 5K pace"
        else:
            workout_type = "Tempo Run"
            description = "Sustained threshold effort"

        workouts.append(Workout(
            day="Wednesday",
            type=workout_type,
            distance_km=round(distances["quality"], 1),
            description=description
        ))

        workouts.append(Workout(
            day="Thursday",
            type="Easy Run",
            distance_km=round(distances["easy3"], 1),
            description="Recovery run"
        ))

        workouts.append(Workout(
            day="Friday",
            type="Easy Run",
            distance_km=round(distances["easy4"], 1),
            description="Short easy run"
        ))

        workouts.append(Workout(
            day="Sunday",
            type="Long Run",
            distance_km=round(distances["long"], 1),
            description="Long endurance run at easy pace"
        ))

        # One rest day
        workouts.append(Workout(day="Saturday", type="Rest", description="Recovery day"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))
