from running_plan import RunningPlan


def test_environmental_preparation_is_persisted_and_displayed(tmp_path):
    plan = RunningPlan("Heat Plan", "Half Marathon", "intermediate", 12, 4)

    plan.set_environmental_conditions(
        heat_humidity=True, altitude=True, hilly_course=True, technical_course=True
    )

    tips = plan.environmental_preparation.get_recommendations()

    assert any("Calor/Umidade" in tip for tip in tips)
    assert any("Altitude" in tip for tip in tips)
    assert any("Colinas" in tip for tip in tips)
    assert any("Terreno técnico" in tip for tip in tips)

    file_path = tmp_path / "env_plan.json"
    plan.save_to_file(file_path)

    loaded = RunningPlan.load_from_file(file_path)

    assert loaded.environmental_preparation.altitude is True
    assert loaded.environmental_preparation.hilly_course is True
    assert len(loaded.environmental_preparation.get_recommendations()) == 4

    visual = loaded.to_visual_str(show_all_weeks=False)

    assert "Calor/Umidade" in visual
    assert "Altitude" in visual
