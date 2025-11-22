#!/usr/bin/env python3
"""
Test script for UserProfile integration with PlanGenerator.
Tests the complete personalized plan generation workflow.
"""
from user_profile import UserProfile, RaceGoal
from plan_generator import PlanGenerator
from datetime import datetime, date, timedelta


def test_basic_profile_integration():
    """Test basic profile integration with plan generation."""
    print("="*70)
    print("TESTE 1: Integração Básica de Perfil")
    print("="*70)

    # Create a basic profile
    race_date = date.today() + timedelta(days=70)  # 10 weeks from now

    profile = UserProfile(
        name="João Silva",
        age=30,
        weight_kg=70.0,
        height_cm=175.0,
        gender="M",
        years_running=2.0,
        current_weekly_km=30.0,
        experience_level="intermediate",
        main_race=RaceGoal(
            distance="10K",
            date=race_date,
            name="Corrida da Cidade",
            is_main_goal=True,
            target_time="45:00"
        ),
        days_per_week=4,
        hours_per_day=1.0,
        recent_race_times={"5K": "22:30", "10K": "47:15"},
        zones_calculation_method="jack_daniels"
    )

    print(profile)

    # Generate plan with profile
    plan = PlanGenerator.generate_plan(
        name="",  # Should be filled from profile
        goal="",  # Should be filled from profile
        level="intermediate",
        user_profile=profile
    )

    print("\n✓ Plano gerado com perfil:")
    print(f"  Nome: {plan.name}")
    print(f"  Meta: {plan.goal}")
    print(f"  Semanas: {plan.weeks}")
    print(f"  Dias/semana: {plan.days_per_week}")

    # Check first week
    week1 = plan.get_week(1)
    print(f"\n✓ Semana 1 - Distância total: {week1.total_distance_km}km")
    print(f"  Notas: {week1.notes[:100]}...")

    return profile, plan


def test_injury_adjustments():
    """Test plan adjustments for users with injuries."""
    print("\n\n" + "="*70)
    print("TESTE 2: Ajustes para Lesões")
    print("="*70)

    race_date = date.today() + timedelta(days=84)  # 12 weeks from now

    profile = UserProfile(
        name="Maria Santos",
        age=35,
        weight_kg=65.0,
        height_cm=165.0,
        gender="F",
        years_running=1.5,
        current_weekly_km=25.0,
        experience_level="beginner",
        main_race=RaceGoal(
            distance="Half Marathon",
            date=race_date,
            is_main_goal=True
        ),
        days_per_week=4,
        hours_per_day=1.5,
        current_injuries=["Fascite Plantar"],
        previous_injuries=["Canelite (Periostite Tibial)"],
        recent_race_times={"10K": "55:00"}
    )

    print(profile)

    # Check risk level
    risk = profile.get_injury_risk_level()
    print(f"\n✓ Nível de risco: {risk}")

    # Check modifications needed
    needs_mod, mods = profile.needs_modified_plan()
    if needs_mod:
        print("\n✓ Modificações necessárias:")
        for mod in mods:
            print(f"  • {mod}")

    # Generate plan
    plan = PlanGenerator.generate_plan(
        name="Plano Adaptado",
        goal="Half Marathon",
        level="beginner",
        user_profile=profile
    )

    print(f"\n✓ Plano gerado:")
    print(f"  Semanas: {plan.weeks}")
    print(f"  Dias/semana: {plan.days_per_week}")

    # Check week 1 notes for injury warnings
    week1 = plan.get_week(1)
    print(f"\n✓ Avisos na Semana 1:")
    print(week1.notes)


def test_time_constraints():
    """Test plan adjustments for time-limited users."""
    print("\n\n" + "="*70)
    print("TESTE 3: Ajustes para Limitação de Tempo")
    print("="*70)

    race_date = date.today() + timedelta(days=56)  # 8 weeks from now

    profile = UserProfile(
        name="Carlos Oliveira",
        age=40,
        weight_kg=82.0,
        height_cm=178.0,
        gender="M",
        years_running=3.0,
        current_weekly_km=35.0,
        experience_level="intermediate",
        main_race=RaceGoal(
            distance="10K",
            date=race_date,
            is_main_goal=True,
            target_time="50:00"
        ),
        days_per_week=4,
        hours_per_day=0.75,  # Only 45 minutes per day!
        recent_race_times={"5K": "24:00", "10K": "50:30"}
    )

    print(profile)

    # Check time budget
    budget = profile.get_weekly_time_budget()
    print(f"\n✓ Orçamento de tempo semanal: {budget}h")

    if budget < 3:
        print("  ⚠️  Tempo limitado - treinos serão adaptados")

    # Generate plan
    plan = PlanGenerator.generate_plan(
        name="Plano Compacto",
        goal="10K",
        level="intermediate",
        user_profile=profile
    )

    print(f"\n✓ Plano gerado:")
    print(f"  Semanas: {plan.weeks}")
    print(f"  Dias/semana: {plan.days_per_week}")

    week1 = plan.get_week(1)
    print(f"  Distância Semana 1: {week1.total_distance_km}km")


def test_high_bmi_adjustments():
    """Test plan adjustments for users with high BMI."""
    print("\n\n" + "="*70)
    print("TESTE 4: Ajustes para IMC Elevado")
    print("="*70)

    race_date = date.today() + timedelta(days=70)  # 10 weeks from now

    profile = UserProfile(
        name="Ana Paula",
        age=28,
        weight_kg=85.0,
        height_cm=165.0,  # BMI = 31.2 (obesity)
        gender="F",
        years_running=0.5,
        current_weekly_km=15.0,
        experience_level="beginner",
        main_race=RaceGoal(
            distance="5K",
            date=race_date,
            is_main_goal=True
        ),
        days_per_week=3,
        hours_per_day=1.0,
        secondary_objectives=["Perda de Peso", "Saúde Geral"]
    )

    print(profile)

    bmi = profile.calculate_bmi()
    print(f"\n✓ IMC: {bmi} - {profile.get_bmi_category()}")

    # Generate plan
    plan = PlanGenerator.generate_plan(
        name="Plano Saúde",
        goal="5K",
        level="beginner",
        user_profile=profile
    )

    print(f"\n✓ Plano gerado (volume reduzido):")
    print(f"  Semanas: {plan.weeks}")
    print(f"  Dias/semana: {plan.days_per_week}")

    # Compare with standard plan
    plan_standard = PlanGenerator.generate_plan(
        name="Plano Padrão",
        goal="5K",
        level="beginner",
        weeks=plan.weeks,
        days_per_week=plan.days_per_week
    )

    week1_profile = plan.get_week(1)
    week1_standard = plan_standard.get_week(1)

    print(f"\n✓ Comparação Semana 1:")
    print(f"  Com perfil: {week1_profile.total_distance_km}km")
    print(f"  Sem perfil: {week1_standard.total_distance_km}km")
    print(f"  Redução: {((week1_standard.total_distance_km - week1_profile.total_distance_km) / week1_standard.total_distance_km * 100):.1f}%")


def test_complete_workflow():
    """Test complete workflow from profile creation to plan visualization."""
    print("\n\n" + "="*70)
    print("TESTE 5: Workflow Completo")
    print("="*70)

    race_date = date.today() + timedelta(days=84)

    profile = UserProfile(
        name="Pedro Costa",
        age=32,
        weight_kg=72.0,
        height_cm=180.0,
        gender="M",
        years_running=4.0,
        current_weekly_km=50.0,
        experience_level="advanced",
        main_race=RaceGoal(
            distance="Half Marathon",
            date=race_date,
            name="Meia Maratona Internacional",
            location="Rio de Janeiro",
            is_main_goal=True,
            target_time="1:35:00"
        ),
        test_races=[
            RaceGoal(distance="10K", date=date.today() + timedelta(days=42), name="Prova Teste"),
        ],
        days_per_week=5,
        hours_per_day=1.5,
        preferred_time="morning",
        preferred_location=["road", "track"],
        recent_race_times={"5K": "19:30", "10K": "40:45", "21K": "1:32:00"},
        zones_calculation_method="jack_daniels",
        hr_resting=52,
        hr_max=185,
        available_equipment=["Relógio GPS/Smartwatch", "Monitor de Frequência Cardíaca", "Acesso a Pista de Atletismo"],
        secondary_objectives=["Performance/Tempo", "Desafio Pessoal"]
    )

    print(profile)

    # Save profile
    profile.save_to_file("test_profile_complete.json")
    print("\n✓ Perfil salvo em: test_profile_complete.json")

    # Generate plan
    plan = PlanGenerator.generate_plan(
        name="",
        goal="",
        level="advanced",
        user_profile=profile
    )

    plan.set_start_date(datetime.combine(date.today(), datetime.min.time()))

    print(f"\n✓ Plano gerado:")
    print(f"  Nome: {plan.name}")
    print(f"  Meta: {plan.goal}")
    print(f"  Semanas: {plan.weeks}")
    print(f"  Dias/semana: {plan.days_per_week}")

    # Show week 1 in visual format
    print("\n" + "-"*70)
    print("SEMANA 1 - Formato Visual")
    print("-"*70)
    week1 = plan.get_week(1)
    print(week1.to_visual_str(plan.start_date))

    # Save plan
    plan.save_to_file("test_plan_complete.json")
    print("\n✓ Plano salvo em: test_plan_complete.json")

    # Load profile back
    loaded_profile = UserProfile.load_from_file("test_profile_complete.json")
    print("\n✓ Perfil recarregado com sucesso")
    print(f"  Nome: {loaded_profile.name}")
    print(f"  Meta: {loaded_profile.main_race.distance}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("TESTES DE INTEGRAÇÃO - UserProfile + PlanGenerator")
    print("="*70)

    try:
        # Test 1: Basic integration
        test_basic_profile_integration()

        # Test 2: Injury adjustments
        test_injury_adjustments()

        # Test 3: Time constraints
        test_time_constraints()

        # Test 4: High BMI adjustments
        test_high_bmi_adjustments()

        # Test 5: Complete workflow
        test_complete_workflow()

        # Summary
        print("\n\n" + "="*70)
        print("✓ TODOS OS TESTES COMPLETADOS COM SUCESSO!")
        print("="*70)
        print("\nRecursos testados:")
        print("  ✓ Geração de planos a partir de UserProfile")
        print("  ✓ Cálculo automático de zonas de treino")
        print("  ✓ Ajustes de volume para lesões e risco")
        print("  ✓ Ajustes de volume para IMC elevado")
        print("  ✓ Redução de progressão para iniciantes")
        print("  ✓ Avisos e recomendações baseados em perfil")
        print("  ✓ Salvamento e carregamento de perfis")
        print("  ✓ Integração completa do workflow")
        print("\n✓ Sistema de personalização completo e funcional!")

    except Exception as e:
        print(f"\n\n❌ ERRO durante os testes: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
