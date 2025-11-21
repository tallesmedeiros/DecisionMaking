#!/usr/bin/env python3
"""
Exemplo simples de uso do Running Plan Creator com zonas de treinamento.
"""
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator
from datetime import datetime

# 1. Configurar suas zonas de treinamento baseadas em tempos recentes
print("Configurando zonas de treinamento...")
zones = TrainingZones(method='jack_daniels')  # ou 'critical_velocity'

# Adicionar seus tempos recentes de provas
# Formato: "MM:SS" para tempos abaixo de 1 hora, "HH:MM:SS" para tempos maiores
race_5k = RaceTime.from_time_string(5.0, "22:30")  # 5K em 22min30s
race_10k = RaceTime.from_time_string(10.0, "47:15")  # 10K em 47min15s

zones.add_race_time("5K Recente", race_5k)
zones.add_race_time("10K Recente", race_10k)

# Calcular as zonas
zones.calculate_zones()

# Mostrar suas zonas
print(zones)

# 2. Criar um plano de treino COM zonas de treinamento
print("\n\nGerando plano de treino personalizado...")
plan = PlanGenerator.generate_plan(
    name="Meu Plano de 10K",
    goal="10K",
    level="intermediate",
    weeks=10,
    days_per_week=4,
    training_zones=zones  # IMPORTANTE: passar as zonas aqui!
)

# Definir data de início
plan.set_start_date(datetime(2025, 1, 6))

# 3. Visualizar uma semana de treino
print("\n" + "="*70)
print("SEMANA 4 - Exemplo de Treinos Detalhados")
print("="*70)

week4 = plan.get_week(4)
for workout in week4.workouts:
    print(f"\n{workout}")

# 4. Salvar o plano
filename = "meu_plano_10k_com_zonas.json"
plan.save_to_file(filename)
print(f"\n\n✓ Plano salvo em: {filename}")
print(f"✓ Total de {plan.weeks} semanas")
print(f"✓ Prova em: {plan.get_race_date().strftime('%d/%m/%Y')}")
