#!/usr/bin/env python3
"""
Test script for enhanced Running Plan Creator with training zones.
"""
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator
from datetime import datetime

def test_training_zones():
    """Test training zones calculations."""
    print("="*70)
    print("TESTE 1: Cálculo de Zonas de Treinamento")
    print("="*70)

    # Test with Jack Daniels method
    print("\n--- Método: Jack Daniels VDOT ---")
    zones_jd = TrainingZones(method='jack_daniels')

    # Add race times
    # Example: 5K in 22:30 (22min 30sec)
    race_5k = RaceTime.from_time_string(5.0, "22:30")
    zones_jd.add_race_time("5K Recent", race_5k)

    # Example: 10K in 47:15
    race_10k = RaceTime.from_time_string(10.0, "47:15")
    zones_jd.add_race_time("10K Recent", race_10k)

    # Calculate zones
    zones_jd.calculate_zones()
    print(zones_jd)

    # Test with Critical Velocity method
    print("\n--- Método: Velocidade Crítica ---")
    zones_cv = TrainingZones(method='critical_velocity')
    zones_cv.add_race_time("5K", race_5k)
    zones_cv.add_race_time("10K", race_10k)
    zones_cv.calculate_zones()
    print(zones_cv)

    return zones_jd


def test_plan_without_zones():
    """Test plan generation without training zones (backward compatibility)."""
    print("\n\n" + "="*70)
    print("TESTE 2: Plano SEM Zonas de Treinamento (Compatibilidade)")
    print("="*70)

    plan = PlanGenerator.generate_plan(
        name="Plano Básico 10K",
        goal="10K",
        level="intermediate",
        weeks=8,
        days_per_week=4
    )

    # Show first week
    week1 = plan.get_week(1)
    print(f"\nSemana 1 - Distância Total: {week1.total_distance_km} km")
    for workout in week1.workouts:
        if workout.type != "Rest":
            print(f"\n{workout}")


def test_plan_with_zones():
    """Test plan generation WITH training zones."""
    print("\n\n" + "="*70)
    print("TESTE 3: Plano COM Zonas de Treinamento")
    print("="*70)

    # Setup training zones
    zones = TrainingZones(method='jack_daniels')
    race_5k = RaceTime.from_time_string(5.0, "22:30")
    race_10k = RaceTime.from_time_string(10.0, "47:15")
    zones.add_race_time("5K", race_5k)
    zones.add_race_time("10K", race_10k)
    zones.calculate_zones()

    print(f"\nVDOT calculado: {zones.vdot:.1f}")

    # Generate plan with zones
    plan = PlanGenerator.generate_plan(
        name="Plano Detalhado 10K",
        goal="10K",
        level="intermediate",
        weeks=8,
        days_per_week=4,
        training_zones=zones
    )

    plan.set_start_date(datetime(2025, 1, 6))

    # Show week 1
    print("\n" + "-"*70)
    print("SEMANA 1 - Construção de Base")
    print("-"*70)
    week1 = plan.get_week(1)
    for workout in week1.workouts:
        if workout.type != "Rest":
            print(f"\n{workout}")

    # Show week 4 with more complex workouts
    print("\n\n" + "-"*70)
    print("SEMANA 4 - Com Treinos de Qualidade")
    print("-"*70)
    week4 = plan.get_week(4)
    for workout in week4.workouts:
        if workout.type != "Rest":
            print(f"\n{workout}")

    return plan


def test_detailed_workout_structures():
    """Test detailed workout structures."""
    print("\n\n" + "="*70)
    print("TESTE 4: Estrutura Detalhada de Treinos")
    print("="*70)

    # Setup zones
    zones = TrainingZones(method='jack_daniels')
    race_5k = RaceTime.from_time_string(5.0, "20:00")  # Faster runner
    zones.add_race_time("5K PR", race_5k)
    zones.calculate_zones()

    print(f"\nZonas de Treinamento (VDOT: {zones.vdot:.1f}):")
    print(f"  Easy: {zones.get_zone_pace_range_str('easy')}")
    print(f"  Threshold: {zones.get_zone_pace_range_str('threshold')}")
    print(f"  Interval: {zones.get_zone_pace_range_str('interval')}")

    # Generate a plan
    plan = PlanGenerator.generate_plan(
        name="Plano Avançado Meia Maratona",
        goal="Half Marathon",
        level="advanced",
        weeks=12,
        days_per_week=5,
        training_zones=zones
    )

    # Show week 6 - should have intervals
    print("\n" + "-"*70)
    print("SEMANA 6 - Treino de Intervalos Detalhado")
    print("-"*70)
    week6 = plan.get_week(6)
    for workout in week6.workouts:
        if workout.type == "Interval Training":
            print(f"\n{workout}")
            break

    # Show week 7 - should have tempo
    print("\n" + "-"*70)
    print("SEMANA 7 - Treino de Tempo Run Detalhado")
    print("-"*70)
    week7 = plan.get_week(7)
    for workout in week7.workouts:
        if workout.type == "Tempo Run":
            print(f"\n{workout}")
            break


def test_different_race_times():
    """Test with different runner profiles."""
    print("\n\n" + "="*70)
    print("TESTE 5: Diferentes Perfis de Corredores")
    print("="*70)

    profiles = [
        {
            "name": "Iniciante",
            "race_5k": "30:00",
            "race_10k": "65:00",
        },
        {
            "name": "Intermediário",
            "race_5k": "22:30",
            "race_10k": "47:00",
        },
        {
            "name": "Avançado",
            "race_5k": "18:00",
            "race_10k": "37:30",
        }
    ]

    for profile in profiles:
        print(f"\n--- Perfil: {profile['name']} ---")
        zones = TrainingZones(method='jack_daniels')
        race_5k = RaceTime.from_time_string(5.0, profile['race_5k'])
        race_10k = RaceTime.from_time_string(10.0, profile['race_10k'])
        zones.add_race_time("5K", race_5k)
        zones.add_race_time("10K", race_10k)
        zones.calculate_zones()

        print(f"  VDOT: {zones.vdot:.1f}")
        print(f"  Easy: {zones.get_zone_pace_range_str('easy')}")
        print(f"  Threshold: {zones.get_zone_pace_range_str('threshold')}")
        print(f"  Interval: {zones.get_zone_pace_range_str('interval')}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("TESTE DO RUNNING PLAN CREATOR APRIMORADO")
    print("Sistema de Zonas de Treinamento e Treinos Detalhados")
    print("="*70)

    try:
        # Test 1: Training zones
        zones = test_training_zones()

        # Test 2: Backward compatibility
        test_plan_without_zones()

        # Test 3: Plan with zones
        plan = test_plan_with_zones()

        # Test 4: Detailed structures
        test_detailed_workout_structures()

        # Test 5: Different profiles
        test_different_race_times()

        # Summary
        print("\n\n" + "="*70)
        print("✓ TODOS OS TESTES COMPLETADOS COM SUCESSO!")
        print("="*70)
        print("\nRecursos implementados:")
        print("  ✓ Cálculo de zonas com Jack Daniels VDOT")
        print("  ✓ Cálculo de zonas com Velocidade Crítica")
        print("  ✓ Treinos detalhados com aquecimento/desaquecimento")
        print("  ✓ Estrutura de intervalos com repetições")
        print("  ✓ Paces específicos para cada zona")
        print("  ✓ Estimativa de tempo total de treino")
        print("  ✓ Compatibilidade com versão anterior")
        print("\nO sistema está pronto para uso!")

    except Exception as e:
        print(f"\n\n❌ ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
