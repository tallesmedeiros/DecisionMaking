from datetime import datetime

from running_plan import RunningPlan


def test_event_and_performance_context_is_persisted(tmp_path):
    plan = RunningPlan("Context Plan", "10K", "intermediate", 8, 4)

    event_date = datetime(2025, 5, 20)
    plan.set_event_info("10K", event_date)
    plan.set_performance_targets(
        personal_best="00:50:00", goal_time="00:48:00", distance_label="10K"
    )
    plan.update_training_context(
        motivation="Correr com amigos",
        logistics=["Treinos em parque", "Sem longões domingo"],
    )

    file_path = tmp_path / "context_plan.json"
    plan.save_to_file(file_path)

    loaded = RunningPlan.load_from_file(file_path)

    assert loaded.event.distance == "10K"
    assert loaded.event.date == event_date
    assert loaded.performance.goal_pace_per_km == "04:48"
    assert loaded.performance.gap_vs_pb.startswith("-00:12")
    assert loaded.training_context.motivation == "Correr com amigos"
    assert "parque" in loaded.training_context.logistics[0].lower()
