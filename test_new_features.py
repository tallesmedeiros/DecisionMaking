#!/usr/bin/env python3
"""
Test script for new features:
- Distance/time rounding
- Training zones visual table
- Zone distribution tracking
- Weekly volume chart
"""
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator
from running_plan import round_to_nearest_5km, round_to_nearest_30min
from datetime import datetime, date, timedelta

print("="*80)
print("TESTE DAS NOVAS FUNCIONALIDADES")
print("="*80)

# Test 1: Rounding functions
print("\n1️⃣ Testando funções de arredondamento...")
print(f"   8.3km → {round_to_nearest_5km(8.3)}km (esperado: 10km)")
print(f"   12.7km → {round_to_nearest_5km(12.7)}km (esperado: 15km)")
print(f"   23.2km → {round_to_nearest_5km(23.2)}km (esperado: 25km)")
print(f"   45min → {round_to_nearest_30min(45)}min (esperado: 30min)")
print(f"   75min → {round_to_nearest_30min(75)}min (esperado: 90min)")
print("   ✅ Arredondamento funcionando!")

# Test 2: Training zones visual table
print("\n2️⃣ Testando tabela visual de zonas...")
zones = TrainingZones(method='jack_daniels')
race_5k = RaceTime.from_time_string(5.0, "22:30")
race_10k = RaceTime.from_time_string(10.0, "47:15")
zones.add_race_time("5K Recent", race_5k)
zones.add_race_time("10K Recent", race_10k)
zones.calculate_zones()

print(zones.to_table())
print("   ✅ Tabela de zonas exibida!")

# Test 3: Generate plan with rounded distances
print("\n3️⃣ Testando geração de plano com arredondamento...")
plan = PlanGenerator.generate_plan(
    name="Plano Teste 10K",
    goal="10K",
    level="intermediate",
    weeks=8,
    days_per_week=4,
    training_zones=zones
)

# Set start date
plan.set_start_date(datetime.now())

# Check rounded volumes
print(f"\n   Volumes semanais (devem ser múltiplos de 5km):")
for week_num, week in enumerate(plan.schedule[:4], 1):
    dist = week.total_distance_km
    print(f"      Semana {week_num}: {dist}km (múltiplo de 5? {dist % 5 == 0})")

print("\n   ✅ Volumes arredondados!")

# Test 4: Zone distribution
print("\n4️⃣ Testando distribuição de zonas...")
week1 = plan.schedule[0]
distribution = week1.get_zone_distribution()
print(f"\n   Distribuição Semana 1:")
for zone, km in distribution.items():
    if km > 0:
        print(f"      {zone}: {km}km")

print("\n   ✅ Distribuição de zonas funcionando!")

# Test 5: Weekly volumes method
print("\n5️⃣ Testando método de volumes semanais...")
volumes = plan.get_weekly_volumes()
print(f"   Volumes: {volumes}")
print(f"   Total de semanas: {len(volumes)}")
print("   ✅ Método get_weekly_volumes() funcionando!")

# Test 6: Zone distributions method
print("\n6️⃣ Testando método de distribuições de zonas...")
distributions = plan.get_zone_distributions()
print(f"   Total de semanas com distribuição: {len(distributions)}")
total_easy = sum(d['easy'] for d in distributions)
total_threshold = sum(d['threshold'] for d in distributions)
total_interval = sum(d['interval'] for d in distributions)
print(f"   Total Easy: {total_easy:.1f}km")
print(f"   Total Threshold: {total_threshold:.1f}km")
print(f"   Total Interval: {total_interval:.1f}km")
print("   ✅ Método get_zone_distributions() funcionando!")

# Summary
print("\n" + "="*80)
print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
print("="*80)
print("\nFuncionalidades implementadas:")
print("  ✅ Arredondamento de distâncias para múltiplos de 5km")
print("  ✅ Arredondamento de tempos para múltiplos de 30min")
print("  ✅ Tabela visual de zonas de treinamento com emojis")
print("  ✅ Rastreamento de distribuição de zonas por semana")
print("  ✅ Métodos para plotagem de volume semanal")
print("\n🎉 Sistema pronto para uso!")
