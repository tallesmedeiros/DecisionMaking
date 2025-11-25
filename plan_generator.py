"""
Plan Generator module for creating training schedules.
Generates running plans based on goal, level, and duration.
"""
from running_plan import RunningPlan, Week, Workout, WorkoutSegment, round_to_nearest_5km, round_to_nearest_30min
from training_zones import TrainingZones, RaceTime
from typing import List, Optional, Tuple, TYPE_CHECKING
from datetime import timedelta

if TYPE_CHECKING:
    from user_profile import UserProfile

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
        training_zones: Optional[TrainingZones] = None,
        user_profile: Optional['UserProfile'] = None
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
            user_profile: Optional UserProfile for personalized adjustments

        Returns:
            A complete RunningPlan object
        """
        # If user_profile is provided, extract data from it
        if user_profile:
            # Build training zones from profile if not provided
            if training_zones is None and user_profile.recent_race_times:
                training_zones = cls._build_zones_from_profile(user_profile)

            # Override days_per_week with profile's recommended value if safer
            recommended_days = user_profile.get_recommended_days_per_week()
            if recommended_days < days_per_week:
                days_per_week = recommended_days

            # Use main race goal if not specified
            if user_profile.main_race:
                if not name or name == "":
                    name = f"Plano {user_profile.main_race.distance}"
                if not goal or goal == "":
                    goal = user_profile.main_race.distance

        # Set default weeks based on goal if not provided
        if weeks is None:
            weeks = cls._get_default_weeks(goal)

        # Adjust weeks if user_profile has race date
        if user_profile and user_profile.main_race:
            from datetime import datetime
            today = datetime.now().date()
            weeks_until_race = (user_profile.main_race.date - today).days // 7
            if weeks_until_race > 0 and weeks_until_race < weeks:
                weeks = weeks_until_race

        plan = RunningPlan(name, goal, level, weeks, days_per_week)

        # Calculate profile-based adjustments
        profile_adjustments = cls._calculate_profile_adjustments(user_profile) if user_profile else {}

        # Generate weekly schedule
        for week_num in range(1, weeks + 1):
            week = cls._generate_week(
                week_num, goal, level, weeks, days_per_week,
                training_zones, user_profile, profile_adjustments
            )
            plan.add_week(week)

        return plan

    @classmethod
    def _build_zones_from_profile(cls, user_profile: 'UserProfile') -> Optional[TrainingZones]:
        """Build TrainingZones from UserProfile race times."""
        if not user_profile.recent_race_times:
            return None

        zones = TrainingZones(method=user_profile.zones_calculation_method)

        # Add race times from profile
        for distance_str, time_str in user_profile.recent_race_times.items():
            # Parse distance (e.g., "5K" -> 5.0, "10K" -> 10.0, "21K" -> 21.0975, "42K" -> 42.195)
            distance_map = {
                "5K": 5.0,
                "10K": 10.0,
                "15K": 15.0,
                "Half Marathon": 21.0975,
                "21K": 21.0975,
                "Marathon": 42.195,
                "42K": 42.195
            }
            distance_km = distance_map.get(distance_str, 0)

            if distance_km > 0:
                race_time = RaceTime.from_time_string(distance_km, time_str)
                zones.add_race_time(distance_str, race_time)

        zones.calculate_zones()
        return zones

    @classmethod
    def _calculate_profile_adjustments(cls, user_profile: 'UserProfile') -> dict:
        """
        Calculate training adjustments based on user profile.

        Returns:
            Dictionary with adjustment factors and modifications
        """
        adjustments = {
            'volume_factor': 1.0,  # Multiplier for weekly distance
            'progression_factor': 1.0,  # Multiplier for weekly progression
            'max_workout_minutes': None,  # Maximum workout duration
            'injury_modifications': [],  # List of injury-based modifications
            'rest_day_recommendations': [],  # Recommended rest days
        }

        if not user_profile:
            return adjustments

        # Adjust based on time availability
        if user_profile.hours_per_day > 0:
            # Convert hours to minutes
            adjustments['max_workout_minutes'] = int(user_profile.hours_per_day * 60)

        # Adjust volume based on current weekly km vs target
        # If current volume is much lower than target, reduce initial volume
        if user_profile.current_weekly_km > 0:
            # Start at current volume or slightly higher
            adjustments['starting_volume_km'] = user_profile.current_weekly_km * 1.1

        # Adjust for injury risk
        injury_risk = user_profile.get_injury_risk_level()
        if injury_risk == "Alto":
            adjustments['volume_factor'] = 0.75  # Reduce volume by 25%
            adjustments['progression_factor'] = 0.8  # Slower progression
        elif injury_risk == "Moderado":
            adjustments['volume_factor'] = 0.9  # Reduce volume by 10%
            adjustments['progression_factor'] = 0.9

        # Adjust for BMI
        bmi = user_profile.calculate_bmi()
        if bmi > 28:
            adjustments['volume_factor'] *= 0.85  # Further reduce volume
            adjustments['progression_factor'] *= 0.85

        # Specific injury modifications
        if "Fascite Plantar" in user_profile.current_injuries:
            adjustments['injury_modifications'].append("Evitar intervalos curtos e rápidos")
            adjustments['injury_modifications'].append("Priorizar corridas fáceis")

        if "Canelite (Periostite Tibial)" in user_profile.current_injuries:
            adjustments['injury_modifications'].append("Reduzir volume de corrida em superfícies duras")
            adjustments['injury_modifications'].append("Considerar treino cruzado (natação, ciclismo)")

        if "Síndrome da Banda Iliotibial" in user_profile.current_injuries:
            adjustments['injury_modifications'].append("Evitar descidas íngremes")
            adjustments['injury_modifications'].append("Fortalecer glúteos e core")

        if "Tendinite de Aquiles" in user_profile.current_injuries:
            adjustments['injury_modifications'].append("Evitar trabalho de velocidade intenso")
            adjustments['injury_modifications'].append("Fortalecer panturrilha gradualmente")

        # Recommend rest days for high-risk profiles
        if user_profile.get_injury_risk_level() == "Alto":
            adjustments['rest_day_recommendations'].append("Considere adicionar um dia de descanso extra")
            adjustments['rest_day_recommendations'].append("Substitua 1-2 corridas por treino cruzado")

        # Adjust for experience level
        if user_profile.years_running < 1:
            adjustments['volume_factor'] *= 0.8
            adjustments['progression_factor'] *= 0.85

        return adjustments

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
    def _determine_block_lengths(cls, total_weeks: int) -> dict:
        """Allocate 4–6 week blocks for Base, Specific and a shorter Taper."""
        taper_weeks = max(2, min(3, int(round(total_weeks * 0.15))))
        remaining = max(total_weeks - taper_weeks, 0)

        base_weeks = min(6, max(4, remaining // 2)) if remaining else 0
        specific_weeks = remaining - base_weeks

        # Guarantee specific block also fits the 4–6 window
        if specific_weeks < 4 and base_weeks > 4:
            transfer = min(base_weeks - 4, 4 - specific_weeks)
            base_weeks -= transfer
            specific_weeks += transfer

        specific_weeks = min(6, max(4, specific_weeks)) if remaining else 0
        # Re-adjust base weeks if specific was clamped to 6
        base_weeks = max(4, min(6, total_weeks - taper_weeks - specific_weeks)) if remaining else 0

        # If plan is very short, divide remaining weeks evenly between base and specific
        if base_weeks + specific_weeks + taper_weeks < total_weeks:
            leftover = total_weeks - (base_weeks + specific_weeks + taper_weeks)
            base_weeks += leftover // 2
            specific_weeks += leftover - (leftover // 2)

        return {"base": base_weeks, "specific": specific_weeks, "taper": taper_weeks}

    @classmethod
    def _get_phase_for_week(cls, week_number: int, block_lengths: dict) -> Tuple[str, int]:
        """Return current phase (base/specific/taper) and week within that block."""
        base_end = block_lengths["base"]
        specific_end = base_end + block_lengths["specific"]

        if week_number <= base_end:
            return "base", week_number
        if week_number <= specific_end:
            return "specific", week_number - base_end
        return "taper", week_number - specific_end

    @classmethod
    def _generate_week(
        cls,
        week_number: int,
        goal: str,
        level: str,
        total_weeks: int,
        days_per_week: int,
        training_zones: Optional[TrainingZones] = None,
        user_profile: Optional['UserProfile'] = None,
        profile_adjustments: dict = None
    ) -> Week:
        """Generate a single week of training."""
        workouts = []

        if profile_adjustments is None:
            profile_adjustments = {}

        # Calculate weekly distance based on progression
        target_distance = cls.GOAL_TARGETS.get(goal, {}).get(level, 30)

        block_lengths = cls._determine_block_lengths(total_weeks)
        phase, week_in_phase = cls._get_phase_for_week(week_number, block_lengths)

        # Apply volume adjustment from profile
        volume_factor = profile_adjustments.get('volume_factor', 1.0)
        target_distance *= volume_factor

        # Use starting volume if specified
        if 'starting_volume_km' in profile_adjustments and week_number == 1:
            weekly_distance = profile_adjustments['starting_volume_km']
        else:
            progression_factor = profile_adjustments.get('progression_factor', 1.0)
            base_peak = target_distance * 0.9

            if phase == "base":
                progress = week_in_phase / max(block_lengths['base'], 1)
                weekly_distance = base_peak * progress * progression_factor
            elif phase == "specific":
                progress = week_in_phase / max(block_lengths['specific'], 1)
                weekly_distance = (base_peak + (target_distance - base_peak) * progress) * progression_factor
            else:  # taper
                taper_weeks = max(block_lengths['taper'], 1)
                taper_progress = week_in_phase / taper_weeks
                # Glide from 70% down towards 50% across taper block
                taper_start = 0.7
                taper_end = 0.5
                taper_factor = taper_start - (taper_start - taper_end) * taper_progress
                weekly_distance = target_distance * taper_factor

        # IMPROVEMENT 1: Apply recovery week reduction (25% reduction every 4 weeks)
        # Skip recovery reduction during taper phase (last 2 weeks)
        is_recovery_week = (week_number % 4 == 0) and (week_number < total_weeks - 2)
        if is_recovery_week:
            weekly_distance *= 0.75  # Reduce by 25% for recovery

        # IMPROVEMENT 2: Apply 10% progression rule (prevent injury from rapid volume increase)
        if week_number > 1:
            # Calculate what previous week's distance was
            # We need to replicate the logic for week_number - 1
            prev_week_num = week_number - 1
            if 'starting_volume_km' in profile_adjustments and prev_week_num == 1:
                prev_weekly_distance = profile_adjustments['starting_volume_km']
            else:
                prev_phase, prev_week_in_phase = cls._get_phase_for_week(prev_week_num, block_lengths)
                if prev_phase == "base":
                    prev_progress = prev_week_in_phase / max(block_lengths['base'], 1)
                    prev_weekly_distance = target_distance * 0.9 * prev_progress * progression_factor
                elif prev_phase == "specific":
                    prev_progress = prev_week_in_phase / max(block_lengths['specific'], 1)
                    prev_weekly_distance = (target_distance * 0.9 + (target_distance * 0.1) * prev_progress) * progression_factor
                else:
                    taper_weeks = max(block_lengths['taper'], 1)
                    taper_progress = prev_week_in_phase / taper_weeks
                    prev_taper_factor = 0.7 - (0.7 - 0.5) * taper_progress
                    prev_weekly_distance = target_distance * prev_taper_factor

                # Apply recovery week reduction if previous week was recovery
                if (prev_week_num % 4 == 0) and (prev_week_num < total_weeks - 2):
                    prev_weekly_distance *= 0.75

            # Round previous week's distance
            prev_weekly_distance = round_to_nearest_5km(prev_weekly_distance)

            # Limit current week to 10% increase from previous week
            # Exception: Allow decrease (for recovery weeks and taper)
            max_allowed_distance = prev_weekly_distance * 1.10
            if weekly_distance > max_allowed_distance:
                weekly_distance = max_allowed_distance

        # Round weekly distance to nearest 5km
        weekly_distance = round_to_nearest_5km(weekly_distance)

        # Distribute workouts across the week
        if days_per_week == 3:
            workouts = cls._generate_3_day_week(week_number, weekly_distance, level, total_weeks, training_zones, goal, phase)
        elif days_per_week == 4:
            workouts = cls._generate_4_day_week(week_number, weekly_distance, level, total_weeks, training_zones, goal, phase)
        elif days_per_week == 5:
            workouts = cls._generate_5_day_week(week_number, weekly_distance, level, total_weeks, training_zones, goal, phase)
        elif days_per_week == 6:
            workouts = cls._generate_6_day_week(week_number, weekly_distance, level, total_weeks, training_zones, goal, phase)
        else:
            raise ValueError(f"Unsupported days_per_week: {days_per_week}")

        # Add notes for special weeks
        phase_note = f"Fase: {phase.title()} (semana {week_in_phase}/{block_lengths[phase]})"
        notes = phase_note
        if week_number == 1:
            notes = phase_note + "\n" + "Welcome to your training plan! Start easy and focus on consistency."
            # Add profile-specific notes for first week
            if profile_adjustments.get('injury_modifications'):
                notes += "\n\n⚠️  ATENÇÃO - Modificações devido a lesões:"
                for mod in profile_adjustments['injury_modifications']:
                    notes += f"\n  • {mod}"
            if profile_adjustments.get('rest_day_recommendations'):
                notes += "\n\n💡 Recomendações de Descanso:"
                for rec in profile_adjustments['rest_day_recommendations']:
                    notes += f"\n  • {rec}"
        elif week_number == total_weeks:
            notes = "Race week! Keep runs short and easy. Trust your training!"
        elif week_number == total_weeks - 1:
            notes = "Taper week - reduce volume to arrive fresh for race day."
        elif week_number % 4 == 0 and week_number < total_weeks - 2:
            notes = "Recovery week - volume reduced by 25% to absorb training and prevent overtraining."

        # Add test race if in profile
        if user_profile and user_profile.test_races:
            for test_race in user_profile.test_races:
                # Check if test race falls in this week
                from datetime import datetime, timedelta
                if hasattr(user_profile.main_race, 'date'):
                    # Calculate approximate week for test race
                    # This is a simplified approach - would need start_date for exact calculation
                    pass  # Will be handled when plan has start_date set

        week = Week(week_number=week_number, workouts=workouts, notes=notes)
        week.calculate_total_distance()
        return week

    @classmethod
    def _limit_workout_by_time(cls, distance_km: float, max_minutes: Optional[int], training_zones: Optional[TrainingZones], zone: str = 'easy') -> float:
        """
        Limit workout distance based on maximum time available.

        Args:
            distance_km: Desired workout distance
            max_minutes: Maximum time available for workout
            training_zones: TrainingZones for pace estimation
            zone: Training zone to use for time estimation

        Returns:
            Adjusted distance that fits within time constraint
        """
        if max_minutes is None or training_zones is None:
            return distance_km

        # Estimate time for desired distance
        pace = training_zones.get_zone_pace(zone, 'middle')
        estimated_time = training_zones.get_time_for_distance(distance_km, pace) / 60  # Convert to minutes

        # If workout fits, return original distance
        if estimated_time <= max_minutes:
            return distance_km

        # Otherwise, calculate maximum distance that fits
        # time = distance * pace, so distance = time / pace
        max_distance = (max_minutes * 60) / pace  # pace is in seconds per km

        return round(max_distance, 1)

    @staticmethod
    def _clamp_distance_by_time(pace_seconds_per_km: float, desired_distance_km: float, min_minutes: int, max_minutes: int) -> float:
        """Clamp a distance so its duration stays within a target window."""
        min_distance = (min_minutes * 60) / pace_seconds_per_km
        max_distance = (max_minutes * 60) / pace_seconds_per_km
        return min(max_distance, max(min_distance, desired_distance_km))

    @classmethod
    def _create_easy_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create an easy run workout with optional pace details."""
        # Round to nearest 5km
        rounded_distance = round_to_nearest_5km(distance_km)
        workout = Workout(
            day=day,
            type="Easy Run",
            distance_km=rounded_distance,
            description="Ritmo confortável, esforço conversacional",
            training_zone="easy"
        )

        if training_zones:
            pace = training_zones.get_zone_pace_str('easy', 'middle')
            workout.target_pace = pace
            total_time = training_zones.get_time_for_distance(rounded_distance, training_zones.get_zone_pace('easy', 'middle'))
            total_time_rounded = round_to_nearest_30min(total_time / 60) * 60  # Convert to minutes, round, back to seconds
            workout.total_time_estimated = training_zones.get_time_str(total_time_rounded)

        return workout

    @classmethod
    def _create_long_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create a long run workout with optional pace details."""
        # Round to nearest 5km
        rounded_distance = round_to_nearest_5km(distance_km)
        workout = Workout(
            day=day,
            type="Long Run",
            distance_km=rounded_distance,
            description="Construir resistência em ritmo fácil",
            training_zone="easy"
        )

        if training_zones:
            pace = training_zones.get_zone_pace_str('easy', 'max')  # Slower end of easy
            workout.target_pace = pace
            total_time = training_zones.get_time_for_distance(rounded_distance, training_zones.get_zone_pace('easy', 'max'))
            total_time_rounded = round_to_nearest_30min(total_time / 60) * 60  # Convert to minutes, round, back to seconds
            workout.total_time_estimated = training_zones.get_time_str(total_time_rounded)

        return workout

    @classmethod
    def _create_tempo_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create a tempo run with detailed structure."""
        # Round to nearest 5km
        rounded_distance = round_to_nearest_5km(distance_km)
        workout = Workout(
            day=day,
            type="Tempo Run",
            distance_km=rounded_distance,
            description="Esforço sustentado em ritmo de limiar",
            training_zone="threshold"
        )

        if training_zones:
            # Warmup: 15-20% of distance
            warmup_km = round(rounded_distance * 0.18, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Tempo portion: 60% of distance
            tempo_km = round(rounded_distance * 0.60, 1)
            tempo_pace_seconds = training_zones.get_zone_pace('threshold', 'middle')
            tempo_pace = training_zones.get_zone_pace_str('threshold', 'middle')
            tempo_km = cls._clamp_distance_by_time(tempo_pace_seconds, tempo_km, 20, 40)
            max_tempo_km = max(0.0, rounded_distance - warmup_km - 0.5)
            tempo_km = min(tempo_km, max_tempo_km)
            tempo_time = training_zones.get_time_for_distance(tempo_km, tempo_pace_seconds) // 60

            # Cooldown: remaining distance
            cooldown_km = round(rounded_distance - warmup_km - tempo_km, 1)
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

            total_time = warmup_time + tempo_time + cooldown_time
            workout.total_time_estimated = training_zones.get_time_str(total_time * 60)

        return workout

    @classmethod
    def _create_interval_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None,
                            level: str = "intermediate", week_num: int = 1, total_weeks: int = 12) -> Workout:
        """
        Create an interval workout with detailed structure.

        IMPROVEMENT 3: Recovery time is proportional to athlete level
        IMPROVEMENT 4: Interval distance varies by phase of training
        """
        # Round to nearest 5km
        rounded_distance = round_to_nearest_5km(distance_km)

        # IMPROVEMENT 4: Periodization of intervals based on training phase
        # Early phase (0-30%): Short intervals (< 500m) for speed
        # Mid phase (30-70%): Medium intervals (600-1200m) for VO2max
        # Late phase (70%+): Long intervals (1600-3000m) for race pace
        training_progress = week_num / total_weeks

        if training_progress <= 0.30:
            # Early: Short, fast intervals for speed and technique
            base_interval_distance = 0.4  # 400m
            interval_description = "Intervalos curtos para velocidade e técnica"
        elif training_progress <= 0.70:
            # Middle: Classic VO2max intervals
            base_interval_distance = 1.0  # 1000m
            interval_description = "Intervalos médios para VO2max"
        else:
            # Late: Longer intervals for race-specific pace
            base_interval_distance = 1.6  # 1600m (milha)
            interval_description = "Intervalos longos para ritmo de prova"

        workout = Workout(
            day=day,
            type="Interval Training",
            distance_km=rounded_distance,
            description=f"Treino de velocidade: {interval_description}",
            training_zone="interval"
        )

        if training_zones:
            # Warmup: 20% of distance
            warmup_km = round(rounded_distance * 0.20, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Intervals: 60% of distance (divided into work + recovery)
            interval_total_km = rounded_distance * 0.60
            # Work intervals: distance varies by phase
            work_km = round(interval_total_km * 0.60, 1)  # 60% hard, 40% recovery
            recovery_km = round(interval_total_km * 0.40, 1)

            interval_pace_seconds = training_zones.get_zone_pace('interval', 'middle')
            interval_pace = training_zones.get_zone_pace_str('interval', 'middle')
            recovery_pace = training_zones.get_zone_pace_str('easy', 'middle')

            # Calculate number of repeats based on base interval distance
            base_interval_distance = cls._clamp_distance_by_time(interval_pace_seconds, base_interval_distance, 3, 5)
            num_repeats = max(4, min(10, int(work_km / base_interval_distance)))
            num_repeats = max(1, num_repeats)
            work_per_repeat = round(work_km / num_repeats, 2)
            work_per_repeat = cls._clamp_distance_by_time(interval_pace_seconds, work_per_repeat, 3, 5)

            work_time_per = training_zones.get_time_for_distance(work_per_repeat, interval_pace_seconds) // 60

            # IMPROVEMENT 3: Recovery time proportional to level
            # beginner: 1:1 (recovery = work time)
            # intermediate: 0.75:1 (recovery = 75% of work time)
            # advanced: 0.5:1 (recovery = 50% of work time)
            recovery_ratios = {
                'beginner': 1.0,
                'intermediate': 0.75,
                'advanced': 0.5
            }
            recovery_ratio = recovery_ratios.get(level, 0.75)  # Default to intermediate
            recovery_time_per = int(work_time_per * recovery_ratio)

            # Cooldown
            cooldown_km = round(rounded_distance - warmup_km - interval_total_km, 1)
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

            total_time = training_zones.get_time_for_distance(rounded_distance, training_zones.get_zone_pace('interval', 'middle'))
            total_time_rounded = round_to_nearest_30min(total_time / 60) * 60
            workout.total_time_estimated = training_zones.get_time_str(total_time_rounded)

        return workout

    @classmethod
    def _create_fartlek_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """Create a fartlek workout with structure."""
        # Round to nearest 5km
        rounded_distance = round_to_nearest_5km(distance_km)
        workout = Workout(
            day=day,
            type="Fartlek",
            distance_km=rounded_distance,
            description="Jogo de ritmos: alterne velocidades livremente",
            training_zone="threshold"
        )

        if training_zones:
            pace = training_zones.get_zone_pace_str('threshold', 'middle')
            workout.target_pace = f"{training_zones.get_zone_pace_str('easy')} - {training_zones.get_zone_pace_str('interval')}"

            # Structure for fartlek
            warmup_km = round(rounded_distance * 0.20, 1)
            fartlek_km = round(rounded_distance * 0.65, 1)
            cooldown_km = round(rounded_distance - warmup_km - fartlek_km, 1)

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

            total_time = training_zones.get_time_for_distance(rounded_distance, training_zones.get_zone_pace('easy', 'max'))
            total_time_rounded = round_to_nearest_30min(total_time / 60) * 60
            workout.total_time_estimated = training_zones.get_time_str(total_time_rounded)

        return workout

    @classmethod
    def _create_race_pace_intervals(cls, day: str, distance_km: float, goal: str, training_zones: Optional[TrainingZones] = None,
                                     level: str = "intermediate") -> Workout:
        """
        Create race-specific pace intervals for 5K and 10K.

        IMPROVEMENT 5: Race-specific workouts in final 4-6 weeks
        """
        rounded_distance = round_to_nearest_5km(distance_km)

        # Determine interval structure based on goal
        if goal == "5K":
            repeat_distance = 0.8  # 800m repeats
            num_repeats = 6
            pace_zone = 'interval'  # 5K pace
            workout_description = "Intervalos no ritmo de prova de 5K"
        elif goal == "10K":
            repeat_distance = 1.0  # 1000m repeats
            num_repeats = 8
            pace_zone = 'threshold'  # 10K pace (threshold)
            workout_description = "Intervalos no ritmo de prova de 10K"
        else:
            # Fallback to threshold intervals
            repeat_distance = 1.0
            num_repeats = 6
            pace_zone = 'threshold'
            workout_description = "Intervalos em ritmo de limiar"

        workout = Workout(
            day=day,
            type="Race Pace Intervals",
            distance_km=rounded_distance,
            description=workout_description,
            training_zone=pace_zone
        )

        if training_zones:
            # Warmup: 20% of distance
            warmup_km = round(rounded_distance * 0.20, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Work intervals at race pace
            race_pace_seconds = training_zones.get_zone_pace(pace_zone, 'middle')
            repeat_distance = cls._clamp_distance_by_time(race_pace_seconds, repeat_distance, 3, 5)
            race_pace = training_zones.get_zone_pace_str(pace_zone, 'middle')
            work_time_per = training_zones.get_time_for_distance(repeat_distance, race_pace_seconds) // 60

            # Recovery based on level
            recovery_ratios = {'beginner': 1.0, 'intermediate': 0.75, 'advanced': 0.5}
            recovery_ratio = recovery_ratios.get(level, 0.75)
            recovery_time_per = int(work_time_per * recovery_ratio)

            # Cooldown: remaining distance
            total_work_km = repeat_distance * num_repeats
            cooldown_km = round(rounded_distance - warmup_km - total_work_km, 1)
            cooldown_pace = training_zones.get_zone_pace_str('easy', 'middle')
            cooldown_time = training_zones.get_time_for_distance(cooldown_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            workout.target_pace = race_pace

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                duration_minutes=warmup_time,
                pace_per_km=warmup_pace,
                description="Preparação gradual"
            ))

            workout.add_segment(WorkoutSegment(
                name=f"Intervalos no Ritmo de {goal}",
                distance_km=repeat_distance,
                duration_minutes=work_time_per,
                pace_per_km=race_pace,
                repetitions=num_repeats,
                description=f"Ritmo de prova - {goal} pace"
            ))

            workout.add_segment(WorkoutSegment(
                name="Recuperação (trote)",
                duration_minutes=recovery_time_per,
                pace_per_km=training_zones.get_zone_pace_str('easy'),
                repetitions=num_repeats,
                description="Recuperação ativa entre intervalos"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                duration_minutes=cooldown_time,
                pace_per_km=cooldown_pace,
                description="Volta à calma"
            ))

            total_time = warmup_time + (work_time_per + recovery_time_per) * num_repeats + cooldown_time
            workout.total_time_estimated = training_zones.get_time_str(total_time * 60)

        return workout

    @classmethod
    def _create_short_interval_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None,
                                    level: str = "intermediate") -> Workout:
        """
        Create short interval workout (<500m) for speed and technique.

        NEW: Specific workout for intermediate/advanced 3-day/week plans
        """
        rounded_distance = round_to_nearest_5km(distance_km)

        workout = Workout(
            day=day,
            type="Short Intervals",
            distance_km=rounded_distance,
            description="Intervalos curtos para velocidade e técnica",
            training_zone="repetition"
        )

        if training_zones:
            # Warmup: 25% of distance
            warmup_km = round(rounded_distance * 0.25, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Short intervals: 400m repeats
            base_interval = 0.4  # 400m
            if level == "beginner":
                base_interval = 0.3
            base_interval = max(0.2, min(0.4, base_interval))
            interval_total_km = rounded_distance * 0.50
            work_km = round(interval_total_km * 0.60, 1)
            num_repeats = max(8, min(12, int(work_km / base_interval)))

            repetition_pace_seconds = training_zones.get_zone_pace('repetition', 'middle')
            interval_pace = training_zones.get_zone_pace_str('repetition', 'middle')
            work_time_per = training_zones.get_time_for_distance(base_interval, repetition_pace_seconds) // 60

            # Recovery based on level
            recovery_ratios = {'beginner': 1.0, 'intermediate': 0.75, 'advanced': 0.5}
            recovery_ratio = recovery_ratios.get(level, 0.75)
            recovery_time_per = int(work_time_per * recovery_ratio)

            # Cooldown
            cooldown_km = round(rounded_distance - warmup_km - (base_interval * num_repeats), 1)
            cooldown_pace = training_zones.get_zone_pace_str('easy', 'middle')
            cooldown_time = training_zones.get_time_for_distance(cooldown_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            workout.target_pace = interval_pace

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                duration_minutes=warmup_time,
                pace_per_km=warmup_pace,
                description="Preparação gradual"
            ))

            workout.add_segment(WorkoutSegment(
                name="Tiro Curto (400m)",
                distance_km=base_interval,
                duration_minutes=work_time_per,
                pace_per_km=interval_pace,
                repetitions=num_repeats,
                description="Velocidade máxima sustentável - técnica de corrida"
            ))

            workout.add_segment(WorkoutSegment(
                name="Recuperação (trote/caminhada)",
                duration_minutes=recovery_time_per,
                pace_per_km=training_zones.get_zone_pace_str('easy'),
                repetitions=num_repeats,
                description="Recuperação ativa"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                duration_minutes=cooldown_time,
                pace_per_km=cooldown_pace,
                description="Volta à calma"
            ))

            total_time = warmup_time + (work_time_per + recovery_time_per) * num_repeats + cooldown_time
            workout.total_time_estimated = training_zones.get_time_str(total_time * 60)

        return workout

    @classmethod
    def _create_long_interval_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None,
                                   level: str = "intermediate") -> Workout:
        """
        Create long interval workout (>800m) for VO2max and endurance.

        NEW: Specific workout for intermediate/advanced 3-day/week plans
        """
        rounded_distance = round_to_nearest_5km(distance_km)

        workout = Workout(
            day=day,
            type="Long Intervals",
            distance_km=rounded_distance,
            description="Intervalos longos para resistência aeróbica",
            training_zone="threshold"
        )

        if training_zones:
            # Warmup: 20% of distance
            warmup_km = round(rounded_distance * 0.20, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Long intervals: 800m-1200m repeats
            base_interval = 1.0  # 1000m
            interval_total_km = rounded_distance * 0.60
            work_km = round(interval_total_km * 0.65, 1)
            num_repeats = max(4, min(8, int(work_km / base_interval)))

            # Use threshold pace (slightly slower than interval pace)
            threshold_pace_seconds = training_zones.get_zone_pace('threshold', 'middle')
            base_interval = cls._clamp_distance_by_time(threshold_pace_seconds, base_interval, 3, 5)
            num_repeats = max(2, min(8, int(work_km / base_interval)))
            threshold_pace = training_zones.get_zone_pace_str('threshold', 'middle')
            work_time_per = training_zones.get_time_for_distance(base_interval, threshold_pace_seconds) // 60

            # Recovery based on level
            recovery_ratios = {'beginner': 1.0, 'intermediate': 0.75, 'advanced': 0.5}
            recovery_ratio = recovery_ratios.get(level, 0.75)
            recovery_time_per = int(work_time_per * recovery_ratio)

            # Cooldown
            cooldown_km = round(rounded_distance - warmup_km - (base_interval * num_repeats), 1)
            cooldown_pace = training_zones.get_zone_pace_str('easy', 'middle')
            cooldown_time = training_zones.get_time_for_distance(cooldown_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            workout.target_pace = threshold_pace

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                duration_minutes=warmup_time,
                pace_per_km=warmup_pace,
                description="Preparação"
            ))

            workout.add_segment(WorkoutSegment(
                name="Intervalo Longo (1000m)",
                distance_km=base_interval,
                duration_minutes=work_time_per,
                pace_per_km=threshold_pace,
                repetitions=num_repeats,
                description="Ritmo de limiar - resistência anaeróbica"
            ))

            workout.add_segment(WorkoutSegment(
                name="Recuperação (trote)",
                duration_minutes=recovery_time_per,
                pace_per_km=training_zones.get_zone_pace_str('easy'),
                repetitions=num_repeats,
                description="Recuperação ativa"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                duration_minutes=cooldown_time,
                pace_per_km=cooldown_pace,
                description="Volta à calma"
            ))

            total_time = warmup_time + (work_time_per + recovery_time_per) * num_repeats + cooldown_time
            workout.total_time_estimated = training_zones.get_time_str(total_time * 60)

        return workout

    @classmethod
    def _create_progressive_long_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """
        Create a progressive long run (finish faster than start).

        IMPROVEMENT 6: Long run variation - progressive build
        """
        rounded_distance = round_to_nearest_5km(distance_km)

        workout = Workout(
            day=day,
            type="Progressive Long Run",
            distance_km=rounded_distance,
            description="Longão progressivo: inicia fácil e termina em ritmo moderado",
            training_zone="easy"
        )

        if training_zones:
            # First 75%: Easy pace
            easy_km = round(rounded_distance * 0.75, 1)
            easy_pace = training_zones.get_zone_pace_str('easy', 'middle')
            easy_time = training_zones.get_time_for_distance(easy_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Final 25%: Threshold/Marathon pace
            fast_km = round(rounded_distance * 0.25, 1)
            fast_pace = training_zones.get_zone_pace_str('threshold', 'min')  # Faster than easy, slower than tempo
            fast_time = training_zones.get_time_for_distance(fast_km, training_zones.get_zone_pace('threshold', 'min')) // 60

            workout.target_pace = f"{easy_pace} → {fast_pace}"

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Início Fácil",
                distance_km=easy_km,
                duration_minutes=easy_time,
                pace_per_km=easy_pace,
                description="Começar em ritmo fácil e confortável"
            ))

            workout.add_segment(WorkoutSegment(
                name="Progressão Final",
                distance_km=fast_km,
                duration_minutes=fast_time,
                pace_per_km=fast_pace,
                description="Acelerar gradualmente nos últimos 25% para ritmo moderado"
            ))

            total_time = easy_time + fast_time
            workout.total_time_estimated = training_zones.get_time_str(total_time * 60)

        return workout

    @classmethod
    def _create_marathon_pace_run(cls, day: str, distance_km: float, training_zones: Optional[TrainingZones] = None) -> Workout:
        """
        Create a marathon pace run for marathon training.

        IMPROVEMENT 5: Marathon-specific long run at race pace
        """
        rounded_distance = round_to_nearest_5km(distance_km)

        workout = Workout(
            day=day,
            type="Marathon Pace Run",
            distance_km=rounded_distance,
            description="Longão no ritmo de prova de maratona",
            training_zone="marathon"
        )

        if training_zones:
            # Warmup: 10% of distance
            warmup_km = round(rounded_distance * 0.10, 1)
            warmup_pace = training_zones.get_zone_pace_str('easy', 'middle')
            warmup_time = training_zones.get_time_for_distance(warmup_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            # Marathon pace portion: 80% of distance
            mp_km = round(rounded_distance * 0.80, 1)
            # Marathon pace is between easy and threshold (approximately easy + 15-20 seconds)
            # We'll use the faster end of easy zone as approximation
            mp_pace = training_zones.get_zone_pace_str('easy', 'min')
            mp_time = training_zones.get_time_for_distance(mp_km, training_zones.get_zone_pace('easy', 'min')) // 60

            # Cooldown: remaining distance
            cooldown_km = round(rounded_distance - warmup_km - mp_km, 1)
            cooldown_pace = training_zones.get_zone_pace_str('easy', 'middle')
            cooldown_time = training_zones.get_time_for_distance(cooldown_km, training_zones.get_zone_pace('easy', 'middle')) // 60

            workout.target_pace = mp_pace

            # Add segments
            workout.add_segment(WorkoutSegment(
                name="Aquecimento",
                distance_km=warmup_km,
                duration_minutes=warmup_time,
                pace_per_km=warmup_pace,
                description="Começar devagar"
            ))

            workout.add_segment(WorkoutSegment(
                name="Marathon Pace",
                distance_km=mp_km,
                duration_minutes=mp_time,
                pace_per_km=mp_pace,
                description="Ritmo de prova da maratona - sustentável e controlado"
            ))

            workout.add_segment(WorkoutSegment(
                name="Desaquecimento",
                distance_km=cooldown_km,
                duration_minutes=cooldown_time,
                pace_per_km=cooldown_pace,
                description="Finalizar com calma"
            ))

            total_time = warmup_time + mp_time + cooldown_time
            workout.total_time_estimated = training_zones.get_time_str(total_time * 60)

        return workout

    @classmethod
    def _generate_3_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int,
                             training_zones: Optional[TrainingZones] = None, goal: str = "10K",
                             phase: str = "base") -> List[Workout]:
        """
        Generate workouts for a 3-day training week.

        NEW LOGIC for intermediate/advanced:
        - Day 1: Short intervals (<500m) - EXCEPT for Half/Marathon
        - Day 2: Tempo run OR Long intervals (>800m) - alternate
        - Day 3: Long run
        """
        workouts = []

        # Check if intermediate or advanced
        is_advanced_level = level in ["intermediate", "advanced"]
        is_endurance_race = goal in ["Half Marathon", "Marathon"]
        race_specific_phase = (week_num > total_weeks - 6) and (week_num <= total_weeks - 2)

        if is_advanced_level and training_zones:
            # NEW LOGIC: Specific structure for intermediate/advanced with 3 days

            # Distribution
            quality_1_distance = weekly_distance * 0.25
            quality_2_distance = weekly_distance * 0.30
            long_distance = weekly_distance * 0.45

            if phase == "base":
                quality_1_distance *= 0.9
                quality_2_distance *= 0.95
            elif phase == "taper":
                quality_1_distance *= 0.7
                quality_2_distance *= 0.7
                long_distance *= 0.9

            # DAY 1 (Tuesday): Short intervals OR Long intervals (if endurance race)
            if week_num <= 2:
                # First 2 weeks: easy runs for adaptation
                workouts.append(cls._create_easy_run("Tuesday", quality_1_distance, training_zones))
            elif is_endurance_race:
                # Half/Marathon: Use long intervals instead of short
                workouts.append(cls._create_long_interval_run("Tuesday", quality_1_distance, training_zones, level))
            else:
                # 5K/10K: Use short intervals for speed
                workouts.append(cls._create_short_interval_run("Tuesday", quality_1_distance, training_zones, level))

            # DAY 2 (Thursday): Tempo run OR Long intervals (alternate)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Thursday", quality_2_distance, training_zones))
            elif race_specific_phase and goal in ["5K", "10K"]:
                # Race-specific phase: use race pace intervals
                workouts.append(cls._create_race_pace_intervals("Thursday", quality_2_distance, goal, training_zones, level))
            elif week_num % 2 == 0:
                # Even weeks: Long intervals
                workouts.append(cls._create_long_interval_run("Thursday", quality_2_distance, training_zones, level))
            else:
                # Odd weeks: Tempo run
                workouts.append(cls._create_tempo_run("Thursday", quality_2_distance, training_zones))

            # DAY 3 (Saturday): Long run - with variations
            if race_specific_phase and goal == "Marathon":
                # Marathon specific: Marathon pace run
                workouts.append(cls._create_marathon_pace_run("Saturday", long_distance, training_zones))
            elif (week_num % 3 == 0) and (week_num > 3) and not race_specific_phase:
                # Every 3 weeks: Progressive long run for variety
                workouts.append(cls._create_progressive_long_run("Saturday", long_distance, training_zones))
            else:
                # Standard long run
                workouts.append(cls._create_long_run("Saturday", long_distance, training_zones))

        else:
            # BEGINNER LOGIC: Keep original simple structure
            easy_distance = weekly_distance * 0.3
            workouts.append(cls._create_easy_run("Tuesday", easy_distance, training_zones))

            # Tempo, race-specific, or easy
            quality_distance = weekly_distance * 0.25
            if week_num <= 3:
                workouts.append(cls._create_easy_run("Thursday", quality_distance, training_zones))
            elif race_specific_phase and training_zones and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Thursday", quality_distance, goal, training_zones, level))
            else:
                workouts.append(cls._create_tempo_run("Thursday", quality_distance, training_zones))

            # Long run - Marathon pace for Marathon goal
            long_distance = weekly_distance * 0.45
            if race_specific_phase and training_zones and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Saturday", long_distance, training_zones))
            else:
                workouts.append(cls._create_long_run("Saturday", long_distance, training_zones))

        # Add rest days
        for day in ["Monday", "Wednesday", "Friday", "Sunday"]:
            workouts.append(Workout(day=day, type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_4_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int,
                             training_zones: Optional[TrainingZones] = None, goal: str = "10K",
                             phase: str = "base") -> List[Workout]:
        """
        Generate workouts for a 4-day training week.

        NEW: For intermediate/advanced, keep 3 quality workouts + 1 easy run
        """
        workouts = []

        # Check if intermediate or advanced
        is_advanced_level = level in ["intermediate", "advanced"]
        is_endurance_race = goal in ["Half Marathon", "Marathon"]
        race_specific_phase = (week_num > total_weeks - 6) and (week_num <= total_weeks - 2)

        if is_advanced_level and training_zones:
            # NEW LOGIC: Same 3 quality workouts as 3-day + 1 easy run

            # Distribution: smaller percentages due to 4th day
            quality_1_distance = weekly_distance * 0.22
            quality_2_distance = weekly_distance * 0.26
            easy_distance = weekly_distance * 0.15  # 4th training day
            long_distance = weekly_distance * 0.37

            if phase == "base":
                quality_1_distance *= 0.9
                quality_2_distance *= 0.9
            elif phase == "taper":
                quality_1_distance *= 0.65
                quality_2_distance *= 0.65
                long_distance *= 0.9

            # DAY 1 (Tuesday): Short intervals OR Long intervals (if endurance race)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Tuesday", quality_1_distance, training_zones))
            elif is_endurance_race:
                workouts.append(cls._create_long_interval_run("Tuesday", quality_1_distance, training_zones, level))
            else:
                workouts.append(cls._create_short_interval_run("Tuesday", quality_1_distance, training_zones, level))

            # DAY 2 (Thursday): Tempo run OR Long intervals (alternate)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Thursday", quality_2_distance, training_zones))
            elif race_specific_phase and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Thursday", quality_2_distance, goal, training_zones, level))
            elif week_num % 2 == 0:
                workouts.append(cls._create_long_interval_run("Thursday", quality_2_distance, training_zones, level))
            else:
                workouts.append(cls._create_tempo_run("Thursday", quality_2_distance, training_zones))

            # DAY 3 (Friday): Easy run - EXTRA DAY with varied duration
            workouts.append(cls._create_easy_run("Friday", easy_distance, training_zones))

            # DAY 4 (Sunday): Long run - with variations
            if race_specific_phase and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Sunday", long_distance, training_zones))
            elif (week_num % 3 == 0) and (week_num > 3) and not race_specific_phase:
                workouts.append(cls._create_progressive_long_run("Sunday", long_distance, training_zones))
            else:
                workouts.append(cls._create_long_run("Sunday", long_distance, training_zones))

        else:
            # BEGINNER LOGIC: Keep original simple distribution
            easy_distance_1 = weekly_distance * 0.22
            workouts.append(cls._create_easy_run("Tuesday", easy_distance_1, training_zones))

            quality_distance = weekly_distance * 0.23
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Thursday", quality_distance, training_zones))
            elif race_specific_phase and training_zones and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Thursday", quality_distance, goal, training_zones, level))
            elif week_num % 2 == 0:
                workouts.append(cls._create_interval_run("Thursday", quality_distance, training_zones, level, week_num, total_weeks))
            else:
                workouts.append(cls._create_tempo_run("Thursday", quality_distance, training_zones))

            easy_distance_2 = weekly_distance * 0.20
            workouts.append(cls._create_easy_run("Friday", easy_distance_2, training_zones))

            long_distance = weekly_distance * 0.35
            use_progressive = (week_num % 3 == 0) and (week_num > 3) and not race_specific_phase and training_zones
            if race_specific_phase and training_zones and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Sunday", long_distance, training_zones))
            elif use_progressive:
                workouts.append(cls._create_progressive_long_run("Sunday", long_distance, training_zones))
            else:
                workouts.append(cls._create_long_run("Sunday", long_distance, training_zones))

        # Add rest days
        for day in ["Monday", "Wednesday", "Saturday"]:
            workouts.append(Workout(day=day, type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_5_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int,
                             training_zones: Optional[TrainingZones] = None, goal: str = "10K",
                             phase: str = "base") -> List[Workout]:
        """
        Generate workouts for a 5-day training week.

        NEW: For intermediate/advanced, keep 3 quality workouts + 2 easy runs
        """
        workouts = []

        # Check if intermediate or advanced
        is_advanced_level = level in ["intermediate", "advanced"]
        is_endurance_race = goal in ["Half Marathon", "Marathon"]
        race_specific_phase = (week_num > total_weeks - 6) and (week_num <= total_weeks - 2)

        if is_advanced_level and training_zones:
            # NEW LOGIC: Same 3 quality workouts as 3-day + 2 easy runs

            # Distribution
            easy_1_distance = weekly_distance * 0.17
            quality_1_distance = weekly_distance * 0.19
            quality_2_distance = weekly_distance * 0.23
            easy_2_distance = weekly_distance * 0.12  # 5th day
            long_distance = weekly_distance * 0.29

            if phase == "base":
                quality_1_distance *= 0.9
                quality_2_distance *= 0.9
            elif phase == "taper":
                quality_1_distance *= 0.65
                quality_2_distance *= 0.65
                long_distance *= 0.9

            # DAY 1 (Monday): Easy run - EXTRA DAY with shorter duration
            workouts.append(cls._create_easy_run("Monday", easy_1_distance, training_zones))

            # DAY 2 (Tuesday): Short intervals OR Long intervals (if endurance race)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Tuesday", quality_1_distance, training_zones))
            elif is_endurance_race:
                workouts.append(cls._create_long_interval_run("Tuesday", quality_1_distance, training_zones, level))
            else:
                workouts.append(cls._create_short_interval_run("Tuesday", quality_1_distance, training_zones, level))

            # DAY 3 (Thursday): Tempo run OR Long intervals (alternate)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Thursday", quality_2_distance, training_zones))
            elif race_specific_phase and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Thursday", quality_2_distance, goal, training_zones, level))
            elif week_num % 2 == 0:
                workouts.append(cls._create_long_interval_run("Thursday", quality_2_distance, training_zones, level))
            else:
                workouts.append(cls._create_tempo_run("Thursday", quality_2_distance, training_zones))

            # DAY 4 (Friday): Easy run - EXTRA DAY with varied duration
            workouts.append(cls._create_easy_run("Friday", easy_2_distance, training_zones))

            # DAY 5 (Sunday): Long run - with variations
            if race_specific_phase and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Sunday", long_distance, training_zones))
            elif (week_num % 3 == 0) and (week_num > 3) and not race_specific_phase:
                workouts.append(cls._create_progressive_long_run("Sunday", long_distance, training_zones))
            else:
                workouts.append(cls._create_long_run("Sunday", long_distance, training_zones))

        else:
            # BEGINNER LOGIC: Keep original simple distribution
            distances = {
                "easy1": weekly_distance * 0.20,
                "easy2": weekly_distance * 0.18,
                "easy3": weekly_distance * 0.15,
                "quality": weekly_distance * 0.20,
                "long": weekly_distance * 0.27
            }

            workouts.append(cls._create_easy_run("Monday", distances["easy1"], training_zones))
            workouts.append(cls._create_easy_run("Tuesday", distances["easy2"], training_zones))

            if week_num <= 2:
                workouts.append(cls._create_easy_run("Thursday", distances["quality"], training_zones))
            elif race_specific_phase and training_zones and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Thursday", distances["quality"], goal, training_zones, level))
            elif week_num % 2 == 0:
                workouts.append(cls._create_interval_run("Thursday", distances["quality"], training_zones, level, week_num, total_weeks))
            else:
                workouts.append(cls._create_tempo_run("Thursday", distances["quality"], training_zones))

            workouts.append(cls._create_easy_run("Friday", distances["easy3"], training_zones))

            if race_specific_phase and training_zones and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Sunday", distances["long"], training_zones))
            else:
                workouts.append(cls._create_long_run("Sunday", distances["long"], training_zones))

        # Rest days
        for day in ["Wednesday", "Saturday"]:
            workouts.append(Workout(day=day, type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))

    @classmethod
    def _generate_6_day_week(cls, week_num: int, weekly_distance: float, level: str, total_weeks: int,
                             training_zones: Optional[TrainingZones] = None, goal: str = "10K",
                             phase: str = "base") -> List[Workout]:
        """
        Generate workouts for a 6-day training week.

        NEW: For intermediate/advanced, keep 3 quality workouts + 3 easy runs
        """
        workouts = []

        # Check if intermediate or advanced
        is_advanced_level = level in ["intermediate", "advanced"]
        is_endurance_race = goal in ["Half Marathon", "Marathon"]
        race_specific_phase = (week_num > total_weeks - 6) and (week_num <= total_weeks - 2)

        if is_advanced_level and training_zones:
            # NEW LOGIC: Same 3 quality workouts as 3-day + 3 easy runs

            # Distribution
            easy_1_distance = weekly_distance * 0.15
            quality_1_distance = weekly_distance * 0.17
            easy_2_distance = weekly_distance * 0.13
            quality_2_distance = weekly_distance * 0.21
            easy_3_distance = weekly_distance * 0.11  # 6th day
            long_distance = weekly_distance * 0.23

            if phase == "base":
                quality_1_distance *= 0.9
                quality_2_distance *= 0.9
            elif phase == "taper":
                quality_1_distance *= 0.65
                quality_2_distance *= 0.65
                long_distance *= 0.9

            # DAY 1 (Monday): Easy run - EXTRA DAY
            workouts.append(cls._create_easy_run("Monday", easy_1_distance, training_zones))

            # DAY 2 (Tuesday): Short intervals OR Long intervals (if endurance race)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Tuesday", quality_1_distance, training_zones))
            elif is_endurance_race:
                workouts.append(cls._create_long_interval_run("Tuesday", quality_1_distance, training_zones, level))
            else:
                workouts.append(cls._create_short_interval_run("Tuesday", quality_1_distance, training_zones, level))

            # DAY 3 (Wednesday): Easy run - EXTRA DAY with varied duration
            workouts.append(cls._create_easy_run("Wednesday", easy_2_distance, training_zones))

            # DAY 4 (Thursday): Tempo run OR Long intervals (alternate)
            if week_num <= 2:
                workouts.append(cls._create_easy_run("Thursday", quality_2_distance, training_zones))
            elif race_specific_phase and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Thursday", quality_2_distance, goal, training_zones, level))
            elif week_num % 2 == 0:
                workouts.append(cls._create_long_interval_run("Thursday", quality_2_distance, training_zones, level))
            else:
                workouts.append(cls._create_tempo_run("Thursday", quality_2_distance, training_zones))

            # DAY 5 (Friday): Easy run - EXTRA DAY with shorter duration
            workouts.append(cls._create_easy_run("Friday", easy_3_distance, training_zones))

            # DAY 6 (Sunday): Long run - with variations
            if race_specific_phase and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Sunday", long_distance, training_zones))
            elif (week_num % 3 == 0) and (week_num > 3) and not race_specific_phase:
                workouts.append(cls._create_progressive_long_run("Sunday", long_distance, training_zones))
            else:
                workouts.append(cls._create_long_run("Sunday", long_distance, training_zones))

        else:
            # BEGINNER LOGIC: Keep original simple distribution
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

            if week_num <= 2:
                workouts.append(cls._create_easy_run("Wednesday", distances["quality"], training_zones))
            elif race_specific_phase and training_zones and goal in ["5K", "10K"]:
                workouts.append(cls._create_race_pace_intervals("Wednesday", distances["quality"], goal, training_zones, level))
            elif week_num % 3 == 0:
                workouts.append(cls._create_fartlek_run("Wednesday", distances["quality"], training_zones))
            elif week_num % 3 == 1:
                workouts.append(cls._create_interval_run("Wednesday", distances["quality"], training_zones, level, week_num, total_weeks))
            else:
                workouts.append(cls._create_tempo_run("Wednesday", distances["quality"], training_zones))

            workouts.append(cls._create_easy_run("Thursday", distances["easy3"], training_zones))
            workouts.append(cls._create_easy_run("Friday", distances["easy4"], training_zones))

            if race_specific_phase and training_zones and goal == "Marathon":
                workouts.append(cls._create_marathon_pace_run("Sunday", distances["long"], training_zones))
            else:
                workouts.append(cls._create_long_run("Sunday", distances["long"], training_zones))

        # One rest day
        workouts.append(Workout(day="Saturday", type="Rest", description="Dia de recuperação"))

        return sorted(workouts, key=lambda w: cls.DAYS_OF_WEEK.index(w.day))
