"""
Plan Generator module for creating training schedules.
Generates running plans based on goal, level, and duration.
"""
from running_plan import RunningPlan, Week, Workout, WorkoutSegment
from training_zones import TrainingZones
from typing import List, Optional


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
        days_per_week: int = 4,
        training_zones: Optional[TrainingZones] = None
    ) -> RunningPlan:
        """
        Generate a complete running plan.

        Args:
            name: Name of the plan
            goal: Goal race (e.g., "5K", "10K", "Half Marathon", "Marathon")
            level: Training level ("beginner", "intermediate", "advanced")
            weeks: Number of weeks (default based on goal)
            days_per_week: Number of running days per week
            training_zones: Optional TrainingZones object for pace-based workouts

        Returns:
            A complete RunningPlan object
        """
        # Set default weeks based on goal if not provided
        if weeks is None:
            weeks = cls._get_default_weeks(goal)

        plan = RunningPlan(name, goal, level, weeks, days_per_week)

        # Generate weekly schedule
        for week_num in range(1, weeks + 1):
            week = cls._generate_week(week_num, goal, level, weeks, days_per_week, training_zones)
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
        days_per_week: int,
        training_zones: Optional[TrainingZones] = None
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
            workouts = cls._generate_3_day_week(week_number, weekly_distance, level, total_weeks, training_zones)
        elif days_per_week == 4:
            workouts = cls._generate_4_day_week(week_number, weekly_distance, level, total_weeks, training_zones)
        elif days_per_week == 5:
            workouts = cls._generate_5_day_week(week_number, weekly_distance, level, total_weeks, training_zones)
        elif days_per_week == 6:
            workouts = cls._generate_6_day_week(week_number, weekly_distance, level, total_weeks, training_zones)
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
    def _create_easy_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create an easy run workout with optional pace details."""
        workout = Workout(
            day=day,
            type="Easy Run",
            distance_km=round(distance_km, 1),
            description="Ritmo confortável, esforço conversacional",
            training_zone="easy"
        )

        if training_zones:
            pace = training_zones.get_zone_pace_str('easy', 'middle')
            workout.target_pace = pace
            total_time = training_zones.get_time_for_distance(distance_km, training_zones.get_zone_pace('easy', 'middle'))
            workout.total_time_estimated = training_zones.get_time_str(total_time)

        return workout

    @classmethod
    def _create_long_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create a long run workout with optional pace details."""
        workout = Workout(
            day=day,
            type="Long Run",
            distance_km=round(distance_km, 1),
            description="Construir resistência em ritmo fácil",
            training_zone="easy"
        )

        if training_zones:
            pace = training_zones.get_zone_pace_str('easy', 'max')  # Slower end of easy
            workout.target_pace = pace
            total_time = training_zones.get_time_for_distance(distance_km, training_zones.get_zone_pace('easy', 'max'))
            workout.total_time_estimated = training_zones.get_time_str(total_time)

        return workout

    @classmethod
    def _create_tempo_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create a tempo run with detailed structure."""
        workout = Workout(
            day=day,
            type="Tempo Run",
            distance_km=round(distance_km, 1),
            description="Esforço sustentado em ritmo de limiar",
            training_zone="threshold"
        )

        if training_zones:
            # Warmup: 15-20% of distance
            warmup_km = round(distance_km * 0.18, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Tempo portion: 60% of distance
            tempo_km = round(distance_km * 0.60, 1)
            tempo_pace = training_zones.get_zone_pace_str('threshold', 'middle')
            tempo_time = training_zones.get_time_for_distance(tempo_km, training_zones.get_zone_pace('threshold', 'middle')) // 60

            # Cooldown: remaining distance
            cooldown_km = round(distance_km - warmup_km - tempo_km, 1)
            cooldown_pace = training_zones.get_zone_pace_str('easy', 'middle')
            cooldown_time = training_zones.get_time_for_distance(cooldown_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            workout.target_pace = tempo_pace

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                duration_minutes=warmup_time,
                pace_per_km=warmup_pace,
                description="Ritmo fácil para preparar o corpo"
            ))

            workout.add_segment(WorkoutSegment(
                name="Tempo (Limiar)",
                distance_km=tempo_km,
                duration_minutes=tempo_time,
                pace_per_km=tempo_pace,
                description="Ritmo de limiar - esforço controlado e sustentado"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                duration_minutes=cooldown_time,
                pace_per_km=cooldown_pace,
                description="Ritmo fácil para recuperação"
            ))

            total_time = training_zones.get_time_for_distance(distance_km, training_zones.get_zone_pace('threshold', 'middle'))
            workout.total_time_estimated = training_zones.get_time_str(total_time)

        return workout

    @classmethod
    def _create_interval_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create an interval workout with detailed structure."""
        workout = Workout(
            day=day,
            type="Interval Training",
            distance_km=round(distance_km, 1),
            description="Treino de velocidade: tiros em ritmo de 5K",
            training_zone="interval"
        )

        if training_zones:
            # Warmup: 20% of distance
            warmup_km = round(distance_km * 0.20, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Intervals: 60% of distance (divided into work + recovery)
            interval_total_km = distance_km * 0.60
            # Work intervals: 400m-1000m repeats
            work_km = round(interval_total_km * 0.60, 1)  # 60% hard, 40% recovery
            recovery_km = round(interval_total_km * 0.40, 1)

            interval_pace = training_zones.get_zone_pace_str('interval', 'middle')
            recovery_pace = training_zones.get_zone_pace_str('easy', 'middle')

            # Estimate 4-6 repeats
            num_repeats = max(4, min(8, int(work_km / 0.8)))
            work_per_repeat = round(work_km / num_repeats, 2)

            work_time_per = training_zones.get_time_for_distance(work_per_repeat, training_zones.get_zone_pace('interval', 'middle')) // 60
            recovery_time_per = 2  # 2 minutes recovery

            # Cooldown
            cooldown_km = round(distance_km - warmup_km - interval_total_km, 1)
            cooldown_pace = training_zones.get_zone_pace_str('easy', 'middle')
            cooldown_time = training_zones.get_time_for_distance(cooldown_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            workout.target_pace = interval_pace

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                duration_minutes=warmup_time,
                pace_per_km=warmup_pace,
                description="Preparação com ritmo fácil"
            ))

            workout.add_segment(WorkoutSegment(
                name="Tiro (Intervalo Rápido)",
                distance_km=work_per_repeat,
                duration_minutes=work_time_per,
                pace_per_km=interval_pace,
                repetitions=num_repeats,
                description="Ritmo de 5K - esforço intenso"
            ))

            workout.add_segment(WorkoutSegment(
                name="Recuperação (trote/caminhada)",
                duration_minutes=recovery_time_per,
                pace_per_km=recovery_pace,
                repetitions=num_repeats,
                description="Recuperação ativa entre tiros"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                duration_minutes=cooldown_time,
                pace_per_km=cooldown_pace,
                description="Volta à calma"
            ))

            total_time = training_zones.get_time_for_distance(distance_km, training_zones.get_zone_pace('interval', 'middle'))
            workout.total_time_estimated = training_zones.get_time_str(total_time)

        return workout

    @classmethod
    def _create_fartlek_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create a fartlek workout with structure."""
        workout = Workout(
            day=day,
            type="Fartlek",
            distance_km=round(distance_km, 1),
            description="Jogo de ritmos: alterne velocidades livremente",
            training_zone="threshold"
        )

        if training_zones:
            pace = training_zones.get_zone_pace_str('threshold', 'middle')
            workout.target_pace = f"{training_zones.get_zone_pace_str('easy')} - {training_zones.get_zone_pace_str('interval')}"

            # Structure for fartlek
            warmup_km = round(distance_km * 0.20, 1)
            fartlek_km = round(distance_km * 0.65, 1)
            cooldown_km = round(distance_km - warmup_km - fartlek_km, 1)

            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                pace_per_km=training_zones.get_zone_pace_str('easy'),
                description="Começar devagar"
            ))

            workout.add_segment(WorkoutSegment(
                name="Fartlek (variações de ritmo)",
                distance_km=fartlek_km,
                description=f"Alterne: 1-3 min rápido ({training_zones.get_zone_pace_str('interval')}) + 1-2 min fácil ({training_zones.get_zone_pace_str('easy')})"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                pace_per_km=training_zones.get_zone_pace_str('easy'),
                description="Finalizar com calma"
            ))

            total_time = training_zones.get_time_for_distance(distance_km, training_zones.get_zone_pace('easy', 'max'))
            workout.total_time_estimated = training_zones.get_time_str(total_time)

        return workout

    @classmethod
    def _generate_3_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int, training_zones: Optional[TrainingZones] = None) -> List[Workout]:
        """Generate workouts for a 3-day training week."""
        workouts = []

        # Easy run
        easy_distance = weekly_distance * 0.3
        workouts.append(cls._create_easy_run("Tuesday", easy_distance, training_zones))

        # Tempo or interval
        quality_distance = weekly_distance * 0.25
        if week_num <= 3:
            workouts.append(cls._create_easy_run("Thursday", quality_distance, training_zones))
        else:
            workouts.append(cls._create_tempo_run("Thursday", quality_distance, training_zones))

        # Long run
        long_distance = weekly_distance * 0.45
        workouts.append(cls._create_long_run("Saturday", long_distance, training_zones))

        # Add rest days
        for day in ["Monday", "Wednesday", "Friday", "Sunday"]:
            workouts.append(Workout(day=day, type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_4_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int, training_zones: Optional[TrainingZones] = None) -> List[Workout]:
        """Generate workouts for a 4-day training week."""
        workouts = []

        # Easy run 1
        easy_distance_1 = weekly_distance * 0.25
        workouts.append(cls._create_easy_run("Tuesday", easy_distance_1, training_zones))

        # Tempo, intervals, or easy depending on week
        quality_distance = weekly_distance * 0.22
        if week_num <= 2:
            workouts.append(cls._create_easy_run("Thursday", quality_distance, training_zones))
        elif week_num % 2 == 0:
            workouts.append(cls._create_interval_run("Thursday", quality_distance, training_zones))
        else:
            workouts.append(cls._create_tempo_run("Thursday", quality_distance, training_zones))

        # Easy run 2
        easy_distance_2 = weekly_distance * 0.18
        workouts.append(cls._create_easy_run("Friday", easy_distance_2, training_zones))

        # Long run
        long_distance = weekly_distance * 0.35
        workouts.append(cls._create_long_run("Sunday", long_distance, training_zones))

        # Add rest days
        for day in ["Monday", "Wednesday", "Saturday"]:
            workouts.append(Workout(day=day, type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_5_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int, training_zones: Optional[TrainingZones] = None) -> List[Workout]:
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

        workouts.append(cls._create_easy_run("Monday", distances["easy1"], training_zones))
        workouts.append(cls._create_easy_run("Tuesday", distances["easy2"], training_zones))

        # Quality workout
        if week_num <= 2:
            workouts.append(cls._create_easy_run("Thursday", distances["quality"], training_zones))
        elif week_num % 2 == 0:
            workouts.append(cls._create_interval_run("Thursday", distances["quality"], training_zones))
        else:
            workouts.append(cls._create_tempo_run("Thursday", distances["quality"], training_zones))

        workouts.append(cls._create_easy_run("Friday", distances["easy3"], training_zones))
        workouts.append(cls._create_long_run("Sunday", distances["long"], training_zones))

        # Rest days
        for day in ["Wednesday", "Saturday"]:
            workouts.append(Workout(day=day, type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_6_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int, training_zones: Optional[TrainingZones] = None) -> List[Workout]:
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

        workouts.append(cls._create_easy_run("Monday", distances["easy1"], training_zones))
        workouts.append(cls._create_easy_run("Tuesday", distances["easy2"], training_zones))

        # Quality workout
        if week_num <= 2:
            workouts.append(cls._create_easy_run("Wednesday", distances["quality"], training_zones))
        elif week_num % 3 == 0:
            workouts.append(cls._create_fartlek_run("Wednesday", distances["quality"], training_zones))
        elif week_num % 3 == 1:
            workouts.append(cls._create_interval_run("Wednesday", distances["quality"], training_zones))
        else:
            workouts.append(cls._create_tempo_run("Wednesday", distances["quality"], training_zones))

        workouts.append(cls._create_easy_run("Thursday", distances["easy3"], training_zones))
        workouts.append(cls._create_easy_run("Friday", distances["easy4"], training_zones))
        workouts.append(cls._create_long_run("Sunday", distances["long"], training_zones))

        # One rest day
        workouts.append(Workout(day="Saturday", type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))
