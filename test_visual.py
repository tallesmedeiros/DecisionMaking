#!/usr/bin/env python3
"""
Test visual output improvements for Running Plan Creator.
"""
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator
from datetime import datetime

print("="*70)
print("TESTE DO FORMATO VISUAL MELHORADO")
print("="*70)

# Setup training zones
zones = TrainingZones(method='jack_daniels')
race_5k = RaceTime.from_time_string(5.0, "22:30")
race_10k = RaceTime.from_time_string(10.0, "47:15")
zones.add_race_time("5K", race_5k)
zones.add_race_time("10K", race_10k)
zones.calculate_zones()

print("\n✓ Zonas calculadas:")
print(f"  VDOT: {zones.vdot:.1f}")
print(f"  Easy: {zones.get_zone_pace_range_str('easy')}")
print(f"  Threshold: {zones.get_zone_pace_range_str('threshold')}")
print(f"  Interval: {zones.get_zone_pace_range_str('interval')}")

# Generate plan with zones
plan = PlanGenerator.generate_plan(
    name="Plano 10K Visual",
    goal="10K",
    level="intermediate",
    weeks=10,
    days_per_week=4,
    training_zones=zones
)

plan.set_start_date(datetime(2025, 1, 6))  # Segunda-feira

print("\n" + "="*70)
print("FORMATO VISUAL COMPLETO DO PLANO")
print("="*70)

# Show visual format
print(plan.to_visual_str())

print("\n" + "="*70)
print("TODAS AS SEMANAS (formato visual)")
print("="*70)

# Show all weeks in visual format
print(plan.to_visual_str(show_all_weeks=True))

print("\n" + "="*70)
print("SEMANAS ESPECÍFICAS (4-6)")
print("="*70)

# Show specific week range
print(plan.to_visual_str(week_range=(4, 6)))

print("\n" + "="*70)
print("COMPARAÇÃO: SEMANA 4 - Formato Normal vs Visual")
print("="*70)

week4 = plan.get_week(4)

print("\nFORMATO NORMAL:")
print("-" * 70)
print(week4)

print("\nFORMATO VISUAL:")
print("-" * 70)
print(week4.to_visual_str(plan.start_date))

print("\n✓ Teste completo!")
print("="*70)
