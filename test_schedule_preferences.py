from datetime import date, timedelta

from plan_generator import PlanGenerator
from user_profile import RaceGoal, UserProfile


def test_time_blocks_and_rounding():
    race_date = date.today() + timedelta(days=60)
    profile = UserProfile(
        name="Test Runner",
        age=34,
        years_running=2,
        experience_level="intermediate",
        current_weekly_km=28.0,
        main_race=RaceGoal(distance="10K", date=race_date, is_main_goal=True),
        days_per_week=3,
        hours_per_day=1.0,
        weekly_schedule={
            "Tuesday": [
                {
                    "start": "06:00",
                    "end": "07:00",
                    "max_minutes": 50,
                    "surfaces": ["pista"],
                }
            ],
            "Thursday": [
                {
                    "start": "18:00",
                    "end": "19:00",
                    "max_minutes": 45,
                    "surfaces": ["esteira"],
                }
            ],
            "Saturday": [
                {
                    "start": "08:00",
                    "end": "09:30",
                    "max_minutes": 80,
                    "surfaces": ["trilha"],
                }
            ],
        },
        default_warmup_minutes=12,
        default_cooldown_minutes=8,
        commute_minutes=5,
        recent_race_times={"5K": "25:00"},
    )

    plan = PlanGenerator.generate_plan(
        name="Plano com horários",
        goal="10K",
        level="intermediate",
        days_per_week=3,
        training_zones=None,
        user_profile=profile,
    )

    week1 = plan.get_week(1)

    for workout in week1.workouts:
        if workout.type == "Rest":
            continue

        assert workout.total_minutes is not None
        assert workout.total_minutes % 5 == 0

        if workout.day == "Tuesday":
            assert workout.max_session_minutes == 50
            assert workout.total_minutes <= workout.max_session_minutes
            assert "pista" in workout.surface_options
            assert workout.warmup_minutes >= profile.default_warmup_minutes

        if workout.day == "Thursday":
            assert "esteira" in workout.surface_options

        if workout.day == "Saturday":
            assert "trilha" in workout.surface_options
