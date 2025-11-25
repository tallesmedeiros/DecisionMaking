from datetime import datetime

from running_plan import RunningPlan


def test_environment_strategy_persistence(tmp_path):
    plan = RunningPlan("Env Plan", "Half Marathon", "intermediate", 12, 4)
    plan.set_event_info("Half Marathon", datetime(2025, 4, 10))
    plan.update_environment_strategy(
        hotter_or_more_humid=True,
        more_gain_or_descents=True,
        colder_or_windier=False,
    )

    file_path = tmp_path / "env_plan.json"
    plan.save_to_file(file_path)

    loaded = RunningPlan.load_from_file(file_path)

    assert loaded.environment_strategy.hotter_or_more_humid is True
    assert loaded.environment_strategy.more_gain_or_descents is True
    assert loaded.environment_strategy.colder_or_windier is False

    recommendations = loaded.environment_strategy.recommendations()
    assert any("calor" in item for item in recommendations)
    assert any("colinas" in item for item in recommendations)
    assert recommendations[-1].startswith("Registre RPE")


def test_environment_strategy_in_visual_output():
    plan = RunningPlan("Env Visual", "10K", "beginner", 8, 3)
    plan.set_event_info("10K", datetime(2025, 9, 14))
    plan.update_environment_strategy(colder_or_windier=True)

    visual = plan.to_visual_str(show_all_weeks=False)

    assert "Ajustes para condições da prova" in visual
    assert "mais fria/ventosa" in visual
    assert "RPE e frequência cardíaca" in visual
