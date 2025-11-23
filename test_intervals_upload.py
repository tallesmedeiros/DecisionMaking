"""
Script de teste para demonstrar upload de plano para Intervals.icu.

Este script:
1. Testa a conexão com Intervals.icu
2. Cria um plano de treino de exemplo
3. Faz upload do plano para o calendário
"""

from datetime import datetime
from intervals_integration import IntervalsUploader
from plan_generator import PlanGenerator
from training_zones import TrainingZones, RaceTime

print("=" * 70)
print("🏃‍♂️ TESTE DE INTEGRAÇÃO COM INTERVALS.ICU")
print("=" * 70)

# ============================================================================
# PASSO 1: Testar Conexão
# ============================================================================
print("\n📡 PASSO 1: Testando conexão com Intervals.icu...")
print("-" * 70)

uploader = IntervalsUploader()

if not uploader.config.is_configured():
    print("❌ Erro: Configuração não encontrada!")
    print("Certifique-se de que o arquivo intervals_config.json existe.")
    exit(1)

# Testar conexão
connection_ok = uploader.test_connection()

if not connection_ok:
    print("\n❌ Falha na conexão. Verifique suas credenciais.")
    exit(1)

print("\n✅ Conexão estabelecida com sucesso!")

# ============================================================================
# PASSO 2: Criar Plano de Treino de Exemplo
# ============================================================================
print("\n" + "=" * 70)
print("📋 PASSO 2: Criando plano de treino de exemplo...")
print("-" * 70)

# Configurar zonas de treino (opcional, mas melhora os treinos no Intervals.icu)
zones = TrainingZones(method='jack_daniels')
zones.add_race_time("10K Recente", RaceTime.from_time_string(10.0, "45:00"))
zones.calculate_zones()

print(f"✅ Zonas calculadas - VDOT: {zones.vdot:.1f}")

# Criar plano de 10K com 8 semanas
plan = PlanGenerator.generate_plan(
    name="Plano 10K - Teste Intervals.icu",
    goal="10K",
    level="intermediate",
    weeks=8,
    days_per_week=4,
    training_zones=zones
)

# Definir data de início (próxima segunda-feira)
plan.set_start_date(datetime(2025, 11, 24))  # Ajuste conforme necessário

print(f"✅ Plano criado: {plan.name}")
print(f"   📅 Início: {plan.start_date.strftime('%d/%m/%Y')}")
print(f"   🏁 Prova: {plan.get_race_date().strftime('%d/%m/%Y')}")
print(f"   📊 {plan.weeks} semanas, {plan.days_per_week} dias/semana")

# Calcular total de treinos
total_workouts = sum(len(week.workouts) for week in plan.schedule)
# Subtrair dias de descanso
rest_days = sum(1 for week in plan.schedule for w in week.workouts if w.type == "Rest")
active_workouts = total_workouts - rest_days

print(f"   🏃 {active_workouts} treinos ativos ({rest_days} dias de descanso)")

# ============================================================================
# PASSO 3: Mostrar Preview do Plano
# ============================================================================
print("\n" + "=" * 70)
print("👀 PREVIEW - Primeiras 2 semanas do plano:")
print("-" * 70)

plan.print_visual(week_range=(1, 2))

# ============================================================================
# PASSO 4: Confirmar Upload
# ============================================================================
print("\n" + "=" * 70)
print("⚠️  ATENÇÃO: Você está prestes a fazer upload deste plano!")
print("=" * 70)
print(f"\n📤 Upload para: https://intervals.icu/athletes/{uploader.config.athlete_id}")
print(f"📋 Plano: {plan.name}")
print(f"📊 {active_workouts} treinos serão adicionados ao seu calendário")
print(f"📅 De {plan.start_date.strftime('%d/%m/%Y')} até {plan.get_race_date().strftime('%d/%m/%Y')}")

# Prompt de confirmação (comentado para teste automático)
# confirma = input("\n🤔 Deseja continuar? (s/n): ").lower()
# if confirma != 's':
#     print("❌ Upload cancelado pelo usuário.")
#     exit(0)

# Para teste automático, vamos pedir confirmação
print("\n🤔 Deseja continuar com o upload?")
print("   Digite 's' para confirmar ou 'n' para cancelar: ", end="")

# Você pode rodar o script interativamente ou comentar esta linha
# confirma = input().lower()

# Para demonstração, vou comentar o upload real
# Descomente as linhas abaixo para fazer upload de verdade:

"""
# ============================================================================
# PASSO 5: Fazer Upload
# ============================================================================
print("\n" + "=" * 70)
print("🚀 PASSO 5: Fazendo upload para Intervals.icu...")
print("-" * 70)

success = uploader.upload_plan(plan)

if success:
    print("\n" + "=" * 70)
    print("✅ UPLOAD CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    print(f"\n🎉 Todos os {active_workouts} treinos foram adicionados ao seu calendário!")
    print(f"\n📱 Acesse agora:")
    print(f"   🌐 Web: https://intervals.icu/athletes/{uploader.config.athlete_id}/calendar")
    print(f"   📱 App: Intervals.icu (disponível na App Store / Play Store)")
    print("\n💡 Dicas:")
    print("   - Sincronize seu relógio (Garmin/Polar/Wahoo) com Intervals.icu")
    print("   - Configure notificações para ver treinos do dia")
    print("   - Compare planejado vs executado após cada treino")
    print("\n🏃 Bons treinos!")
else:
    print("\n❌ Erro no upload. Verifique os logs acima.")
"""

# ============================================================================
# MODO DEMONSTRAÇÃO
# ============================================================================
print("\n" + "=" * 70)
print("ℹ️  MODO DEMONSTRAÇÃO")
print("=" * 70)
print("\n📝 Este script está em modo demonstração.")
print("\n✅ O que foi verificado:")
print("   ✓ Conexão com Intervals.icu")
print("   ✓ Plano de treino criado com sucesso")
print("   ✓ Estrutura de dados preparada para upload")

print("\n🚀 Para fazer upload REAL:")
print("   1. Abra este arquivo: test_intervals_upload.py")
print("   2. Vá até a linha ~110 (PASSO 5)")
print("   3. Descomente o código de upload")
print("   4. Execute novamente: python test_intervals_upload.py")

print("\n💡 OU use nos notebooks:")
print("   - create_plan_interactive.ipynb")
print("   - running_plan_creator.ipynb")
print("   (Células de upload já estão prontas)")

print("\n" + "=" * 70)
print("✅ Teste concluído! Sistema pronto para uso.")
print("=" * 70)
