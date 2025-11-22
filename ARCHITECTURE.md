# 📚 Documentação da Arquitetura do Sistema

## Criador de Planos de Treino de Corrida

**Versão:** 1.0
**Linguagem:** Python 3.7+
**Autor:** Sistema de IA Claude
**Última atualização:** Novembro 2025

---

## 🏗️ Visão Geral da Arquitetura

O sistema é organizado em módulos independentes que seguem o princípio de responsabilidade única:

```
DecisionMaking/
├── 📊 Camada de Dados (running_plan.py)
│   └── Classes: RunningPlan, Week, Workout, WorkoutSegment
│
├── 🎯 Camada de Lógica (plan_generator.py)
│   └── Classe: PlanGenerator
│
├── 📏 Camada de Cálculo (training_zones.py)
│   └── Classes: TrainingZones, RaceTime
│
├── 👤 Camada de Perfil (user_profile.py)
│   └── Classes: UserProfile, RaceGoal
│
├── 📈 Camada de Visualização (plot_utils.py)
│   └── Funções: plot_weekly_volume, plot_zone_distribution_stacked, print_zone_summary
│
├── 🎨 Camada de Interface (notebook_widgets.py)
│   └── Classe: PlanCreatorWidgets
│
├── 📄 Camada de Exportação (pdf_export.py)
│   └── Funções: export_plan_to_pdf, save_plan_as_pdf
│
└── 🖥️ Interface CLI (cli.py)
    └── Funções de interação com usuário
```

---

## 📊 Módulo: running_plan.py

### Responsabilidade
Definir as estruturas de dados fundamentais do sistema.

### Classes Principais

#### 1. `WorkoutSegment` (dataclass)
Representa um segmento de um treino (aquecimento, tiro, recuperação, desaquecimento).

**Atributos:**
```python
name: str                           # Nome do segmento (ex: "Aquecimento", "Tiro")
distance_km: Optional[float]        # Distância em km
duration_minutes: Optional[int]     # Duração em minutos
pace_per_km: Optional[str]          # Pace no formato "MM:SS"
repetitions: int                    # Número de repetições (padrão: 1)
description: str                    # Descrição do segmento
```

**Métodos Principais:**
```python
to_compact_str() -> str
    # Retorna representação compacta para saída visual
    # Ex: "1km aquec" ou "4x500m @ 4:20/km"
```

---

#### 2. `Workout` (dataclass)
Representa um treino completo de um dia específico.

**Atributos:**
```python
day: str                           # Dia da semana ("Monday", "Tuesday", etc.)
type: str                          # Tipo de treino ("Easy Run", "Interval Training", etc.)
distance_km: float                 # Distância total
duration_minutes: Optional[int]    # Duração em minutos
description: str                   # Descrição do treino
target_pace: Optional[str]         # Pace alvo
training_zone: Optional[str]       # Zona de treino
total_time_estimated: Optional[str] # Tempo estimado total
segments: List[WorkoutSegment]     # Lista de segmentos detalhados
```

**Métodos Principais:**
```python
has_detailed_structure() -> bool
    # Verifica se o treino tem estrutura detalhada (segmentos)

get_emoji() -> str
    # Retorna emoji correspondente ao tipo de treino
    # 🟢 Easy, 🟡 Tempo, 🟠 Interval, 🔵 Long, 😴 Rest

get_type_label() -> str
    # Retorna rótulo traduzido do tipo de treino

to_visual_str(date: Optional[datetime]) -> str
    # Retorna representação visual compacta com emojis
    # Ex: "📍 Segunda (06/01): 🟢 Fácil: 10km @ 6:00/km [1:00:00]"
```

---

#### 3. `Week` (dataclass)
Representa uma semana completa de treinos.

**Atributos:**
```python
week_number: int                   # Número da semana no plano
workouts: List[Workout]            # Lista de treinos da semana
total_distance_km: float           # Distância total da semana
notes: str                         # Notas/observações da semana
```

**Métodos Principais:**
```python
calculate_total_distance() -> float
    # Calcula e atualiza a distância total da semana

get_zone_distribution() -> Dict[str, float]
    # Retorna distribuição de km por zona de treino
    # Ex: {'easy': 30.0, 'threshold': 5.0, 'interval': 3.0}

to_visual_str(start_date: Optional[datetime]) -> str
    # Retorna representação visual da semana completa
```

---

#### 4. `RunningPlan` (dataclass)
Representa o plano de treino completo.

**Atributos:**
```python
name: str                          # Nome do plano
goal: str                          # Objetivo ("5K", "10K", "Half Marathon", "Marathon")
level: str                         # Nível ("beginner", "intermediate", "advanced")
weeks: int                         # Número de semanas
days_per_week: int                 # Dias de treino por semana
schedule: List[Week]               # Lista de semanas do plano
start_date: Optional[datetime]     # Data de início
training_zones: Optional[TrainingZones] # Zonas de treino (se disponível)
```

**Métodos Principais:**
```python
set_start_date(date: datetime) -> None
    # Define data de início do plano

get_race_date() -> Optional[datetime]
    # Calcula e retorna data da prova

get_week(week_number: int) -> Optional[Week]
    # Retorna semana específica pelo número

save_to_file(filename: str) -> None
    # Salva plano em arquivo JSON

@staticmethod
load_from_file(filename: str) -> 'RunningPlan'
    # Carrega plano de arquivo JSON

to_visual_str(**kwargs) -> str
    # Retorna representação visual completa do plano

print_visual(**kwargs) -> None
    # Imprime representação visual do plano

get_weekly_volumes() -> List[float]
    # Retorna lista de volumes semanais (km)

get_zone_distributions() -> List[Dict[str, float]]
    # Retorna distribuição de zonas para cada semana
```

**Funções Auxiliares:**
```python
round_to_nearest_5km(distance_km: float) -> float
    # Arredonda distância para múltiplo de 5km

round_to_nearest_30min(minutes: float) -> int
    # Arredonda tempo para múltiplo de 30min
```

---

## 🎯 Módulo: plan_generator.py

### Responsabilidade
Gerar planos de treino baseados em parâmetros de entrada.

### Classe Principal

#### `PlanGenerator`
Classe estática (factory) para geração de planos.

**Método Principal:**
```python
@staticmethod
generate_plan(
    name: str,
    goal: str,
    level: str,
    weeks: Optional[int] = None,
    days_per_week: int = 4,
    training_zones: Optional[TrainingZones] = None,
    user_profile: Optional[UserProfile] = None
) -> RunningPlan
    # Gera um plano de treino completo
    # Se weeks=None, calcula automaticamente baseado no objetivo
    # Se training_zones fornecido, inclui paces personalizados
    # Se user_profile fornecido, aplica personalizações
```

**Constantes:**
```python
GOAL_TARGETS = {
    "5K": {"beginner": 20, "intermediate": 30, "advanced": 40},
    "10K": {"beginner": 30, "intermediate": 45, "advanced": 60},
    "Half Marathon": {"beginner": 40, "intermediate": 60, "advanced": 80},
    "Marathon": {"beginner": 50, "intermediate": 75, "advanced": 100}
}
# Quilometragem semanal base por objetivo e nível
```

**Métodos Privados de Geração:**
```python
@classmethod
_generate_week(cls, week_num, total_weeks, base_distance, days_per_week, goal, zones) -> Week
    # Gera uma semana específica do plano
    # Aplica progressão (build/peak/taper)

@classmethod
_generate_3_day_week(cls, day_distances, goal, zones) -> List[Workout]
    # Padrão: Fácil + Intervalado + Longão

@classmethod
_generate_4_day_week(cls, day_distances, goal, zones) -> List[Workout]
    # Padrão: Fácil + Tempo + Fácil + Longão

@classmethod
_generate_5_day_week(cls, day_distances, goal, zones) -> List[Workout]
    # Padrão: Fácil + Tempo + Fácil + Intervalado + Longão

@classmethod
_generate_6_day_week(cls, day_distances, goal, zones) -> List[Workout]
    # Padrão: Fácil + Tempo + Fácil + Intervalado + Fácil + Longão
```

**Métodos de Criação de Treinos:**
```python
@classmethod
_create_easy_run(cls, day, distance_km, zones) -> Workout
    # Cria corrida fácil

@classmethod
_create_long_run(cls, day, distance_km, zones) -> Workout
    # Cria longão (long run)

@classmethod
_create_tempo_run(cls, day, distance_km, zones) -> Workout
    # Cria tempo run com segmentos detalhados

@classmethod
_create_interval_run(cls, day, distance_km, zones) -> Workout
    # Cria treino intervalado com tiros

@classmethod
_create_fartlek_run(cls, day, distance_km, zones) -> Workout
    # Cria treino fartlek
```

---

## 📏 Módulo: training_zones.py

### Responsabilidade
Calcular zonas de treino personalizadas baseadas em performances recentes.

### Classes Principais

#### 1. `RaceTime` (dataclass)
Representa o tempo de uma corrida.

**Atributos:**
```python
distance_km: float                 # Distância da corrida
time_seconds: int                  # Tempo em segundos
pace_per_km: float                 # Pace calculado (seg/km)
```

**Métodos:**
```python
@staticmethod
from_time_string(distance_km: float, time_str: str) -> 'RaceTime'
    # Cria RaceTime a partir de string "MM:SS" ou "HH:MM:SS"
    # Ex: RaceTime.from_time_string(5.0, "22:30")
```

---

#### 2. `TrainingZones`
Calcula e armazena zonas de treino personalizadas.

**Atributos:**
```python
method: str                        # "jack_daniels" ou "critical_velocity"
race_times: Dict[str, RaceTime]    # Dicionário de tempos de prova
zones: Dict[str, Tuple[float, float]] # Zonas calculadas (min_pace, max_pace)
vdot: Optional[float]              # VDOT calculado (Jack Daniels)
```

**Métodos Principais:**
```python
add_race_time(name: str, race_time: RaceTime) -> None
    # Adiciona tempo de prova ao cálculo

calculate_zones() -> None
    # Calcula as zonas baseado no método escolhido
    # Chama _calculate_jack_daniels_zones() ou _calculate_critical_velocity_zones()

get_zone_pace(zone_name: str, target: str = 'middle') -> float
    # Retorna pace para zona específica
    # target: 'min' (mais rápido), 'max' (mais lento), 'middle' (meio)

get_zone_pace_str(zone_name: str, target: str = 'middle') -> str
    # Retorna pace formatado como string "MM:SS"

get_zone_pace_range_str(zone_name: str) -> str
    # Retorna faixa de pace "MM:SS - MM:SS"

get_time_for_distance(distance_km: float, pace_sec_per_km: float) -> int
    # Calcula tempo total para distância e pace

to_table() -> str
    # Gera tabela visual com emojis das zonas de treino
```

**Métodos Privados:**
```python
_calculate_jack_daniels_zones() -> None
    # Método Jack Daniels:
    # 1. Calcula VDOT de cada corrida
    # 2. Usa o melhor VDOT
    # 3. Calcula zonas como % do VO2max

_calculate_critical_velocity_zones() -> None
    # Método Velocidade Crítica:
    # 1. Requer 2+ corridas
    # 2. Calcula CV = (D2-D1)/(T2-T1)
    # 3. Zonas como % da CV

_calculate_vdot_from_race(distance_km: float, time_seconds: int) -> float
    # Fórmula Jack Daniels para calcular VDOT

_velocity_at_vdot(vdot: float, percent_vo2max: float) -> float
    # Calcula velocidade em m/min para % de VO2max
```

**Zonas Definidas:**
```python
zones = {
    'easy': (min_pace, max_pace),       # 🟢 59-74% VO2max
    'marathon': (min_pace, max_pace),   # 🔵 75-84% VO2max
    'threshold': (min_pace, max_pace),  # 🟡 83-88% VO2max
    'interval': (min_pace, max_pace),   # 🟠 95-100% VO2max
    'repetition': (min_pace, max_pace)  # 🔴 105-120% VO2max
}
```

---

## 👤 Módulo: user_profile.py

### Responsabilidade
Gerenciar perfil do usuário e personalizações do plano.

### Classes Principais

#### 1. `RaceGoal` (dataclass)
Representa um objetivo de corrida.

**Atributos:**
```python
distance: str                      # Distância ("5K", "10K", etc.)
date: date                         # Data da prova
name: str                          # Nome da prova
location: str                      # Local da prova
is_main_goal: bool                 # Se é objetivo principal
target_time: Optional[str]         # Tempo meta
```

---

#### 2. `UserProfile` (dataclass)
Perfil completo do usuário com personalizações.

**Atributos Pessoais:**
```python
name: str                          # Nome
age: int                           # Idade
weight_kg: float                   # Peso em kg
height_cm: float                   # Altura em cm
gender: str                        # "M", "F" ou ""
```

**Atributos de Experiência:**
```python
years_running: float               # Anos correndo
current_weekly_km: float           # Km semanal atual
experience_level: str              # "beginner", "intermediate", "advanced"
```

**Atributos de Objetivos:**
```python
main_race: Optional[RaceGoal]      # Prova principal
test_races: List[RaceGoal]         # Provas teste
secondary_objectives: List[str]    # Objetivos secundários
```

**Atributos de Disponibilidade:**
```python
days_per_week: int                 # Dias disponíveis por semana
hours_per_day: float               # Horas por dia
preferred_time: str                # "morning", "afternoon", "evening"
preferred_location: List[str]      # ["road", "track", "trail", "treadmill"]
```

**Atributos de Saúde:**
```python
current_injuries: List[str]        # Lesões atuais
previous_injuries: List[str]       # Lesões prévias
hr_resting: Optional[int]          # FC repouso
hr_max: Optional[int]              # FC máxima
```

**Atributos de Zonas:**
```python
recent_race_times: Dict[str, str]  # Tempos recentes {"5K": "22:30", ...}
zones_calculation_method: str      # "jack_daniels" ou "critical_velocity"
```

**Métodos Principais:**
```python
calculate_bmi() -> float
    # Calcula IMC (BMI)

get_bmi_category() -> str
    # Retorna categoria do IMC

estimate_hr_max() -> int
    # Estima FC máxima (220 - idade)

get_weekly_time_budget() -> float
    # Retorna horas semanais disponíveis

get_injury_risk_level() -> str
    # Retorna "Baixo", "Moderado" ou "Alto"

needs_modified_plan() -> Tuple[bool, List[str]]
    # Verifica se precisa modificações
    # Retorna (True/False, lista de razões)

save_to_file(filename: str) -> None
    # Salva perfil em JSON

@staticmethod
load_from_file(filename: str) -> 'UserProfile'
    # Carrega perfil de JSON
```

**Constantes:**
```python
COMMON_INJURIES = [
    "Fascite Plantar",
    "Canelite (Periostite Tibial)",
    "Tendinite de Aquiles",
    # ... (15 lesões comuns)
]
```

---

## 📈 Módulo: plot_utils.py

### Responsabilidade
Gerar visualizações gráficas dos planos de treino.

### Funções Principais

```python
def plot_weekly_volume(plan: RunningPlan, figsize=(12, 6)) -> Tuple[Figure, Axes]
    # Gera gráfico de barras do volume semanal
    # Cores em gradiente: azul (baixo) → vermelho (alto volume)
    # Retorna: (fig, ax) do matplotlib

def plot_zone_distribution_stacked(plan: RunningPlan, figsize=(14, 7)) -> Tuple[Figure, Axes]
    # Gera gráfico de barras empilhadas por zona
    # Cores: 🟢 verde, 🔵 azul, 🟡 amarelo, 🟠 laranja, 🔴 vermelho
    # Retorna: (fig, ax) do matplotlib

def print_zone_summary(plan: RunningPlan) -> None
    # Imprime resumo textual da distribuição de zonas
    # Mostra km e % por zona no plano completo
```

**Paleta de Cores:**
```python
zone_colors = {
    'easy': '#90EE90',       # Verde claro
    'marathon': '#4169E1',   # Azul royal
    'threshold': '#FFD700',  # Dourado
    'interval': '#FF8C00',   # Laranja escuro
    'repetition': '#DC143C'  # Vermelho carmesim
}
```

---

## 🎨 Módulo: notebook_widgets.py

### Responsabilidade
Fornecer interface visual interativa para notebooks Jupyter.

### Classe Principal

#### `PlanCreatorWidgets`
Gerencia widgets ipywidgets para entrada de dados.

**Atributos (Widgets):**
```python
# Informações pessoais
nome_widget: widgets.Text
idade_widget: widgets.IntSlider
peso_widget: widgets.FloatSlider
altura_widget: widgets.IntSlider
sexo_widget: widgets.Dropdown

# Experiência
anos_correndo_widget: widgets.FloatSlider
km_semanal_widget: widgets.FloatSlider
nivel_widget: widgets.Dropdown

# Objetivo
distancia_widget: widgets.Dropdown
data_prova_widget: widgets.DatePicker
nome_prova_widget: widgets.Text
local_prova_widget: widgets.Text
tempo_meta_widget: widgets.Text

# Disponibilidade
dias_semana_widget: widgets.IntSlider
horas_dia_widget: widgets.FloatSlider
horario_widget: widgets.Dropdown

# Zonas de treino
tempo_5k_widget: widgets.Text
tempo_10k_widget: widgets.Text
tempo_21k_widget: widgets.Text
tempo_42k_widget: widgets.Text
metodo_zonas_widget: widgets.Dropdown

# Lesões
lesoes_atuais_widget: widgets.SelectMultiple
lesoes_previas_widget: widgets.SelectMultiple

# Saída
output: widgets.Output
```

**Métodos Principais:**
```python
show_personal_info() -> None
    # Exibe widgets de informações pessoais

show_experience() -> None
    # Exibe widgets de experiência

show_goal() -> None
    # Exibe widgets de objetivo

show_availability() -> None
    # Exibe widgets de disponibilidade

show_training_zones() -> None
    # Exibe widgets de zonas de treino

show_injuries() -> None
    # Exibe widgets de lesões

create_profile() -> UserProfile
    # Cria perfil baseado nos valores dos widgets

generate_plan() -> RunningPlan
    # Gera plano baseado no perfil criado

show_all_simple() -> None
    # Exibe interface simplificada (informações básicas)

show_all_complete() -> None
    # Exibe interface completa (todas as opções)
```

### Funções Helper

```python
def create_simple_plan_widgets() -> PlanCreatorWidgets
    # Cria e exibe widgets em modo simples

def create_complete_plan_widgets() -> PlanCreatorWidgets
    # Cria e exibe widgets em modo completo
```

---

## 📄 Módulo: pdf_export.py

### Responsabilidade
Exportar planos de treino em formato PDF profissional.

### Funções Principais

```python
def export_plan_to_pdf(
    plan: RunningPlan,
    filename: Optional[str] = None,
    include_graphs: bool = True
) -> Optional[str]
    # Exporta plano completo em PDF
    # Inclui:
    #   - Cabeçalho com informações do plano
    #   - Tabela de zonas de treino (se disponível)
    #   - Gráficos de volume e distribuição (se include_graphs=True)
    #   - Plano detalhado semana a semana
    #   - Dicas de treino
    # Retorna: caminho do arquivo gerado ou None se falhar

def export_plan_simple_pdf(
    plan: RunningPlan,
    filename: Optional[str] = None
) -> Optional[str]
    # Exporta PDF sem gráficos (mais leve)
    # Retorna: caminho do arquivo gerado

def save_plan_as_pdf(
    plan: RunningPlan,
    filename: Optional[str] = None,
    include_graphs: bool = True
) -> Optional[str]
    # Versão amigável para notebooks
    # Mostra mensagens de progresso
    # Retorna: caminho do arquivo gerado
```

**Estrutura do PDF:**
```
1. Cabeçalho
   - Título do plano
   - Informações (meta, nível, duração, volume total)

2. Zonas de Treino (se disponível)
   - VDOT
   - Tabela com 5 zonas (pace, %FC, uso)

3. Gráficos (se include_graphs=True)
   - Volume semanal (gradiente de cores)
   - Distribuição de zonas (empilhado)

4. Plano Detalhado Semana a Semana
   Para cada semana:
     - Título: "Semana X - Ykm (dd/mm)"
     - Notas da semana
     Para cada treino:
       - Linha principal: dia, emoji, tipo, descrição compacta
       - Descrição do treino
       - Segmentos detalhados (aquecimento, tiros, recuperação, desaquecimento)

5. Rodapé
   - Dicas de treino
   - Data/hora de geração
```

**Estilos Usados:**
```python
# Títulos
title_style: fontSize=24, alignment=CENTER

# Subtítulos
subtitle_style: fontSize=16, color=#333333

# Treinos
workout_style: fontSize=9, leftIndent=10

# Segmentos
segment_style: fontSize=8, leftIndent=25, color=#555555
```

---

## 🖥️ Módulo: cli.py

### Responsabilidade
Interface de linha de comando para interação com o usuário.

### Funções Principais

```python
def main() -> None
    # Função principal do CLI
    # Menu interativo com opções:
    #   1. Criar novo plano (detalhado)
    #   2. Criar plano rápido
    #   3. Ver plano existente
    #   4. Sair

def create_detailed_plan() -> None
    # Cria plano interativo perguntando detalhes

def create_quick_plan() -> None
    # Cria plano com valores padrão

def view_plan(filename: str) -> None
    # Carrega e exibe plano salvo
```

---

## 🔄 Fluxo de Dados

### 1. Criação de Plano Básico

```
Usuário
  ↓
CLI/Widgets (entrada de parâmetros)
  ↓
PlanGenerator.generate_plan()
  ↓
  ├─→ _generate_week() (para cada semana)
  │     ├─→ _generate_X_day_week()
  │     │     ├─→ _create_easy_run()
  │     │     ├─→ _create_tempo_run()
  │     │     ├─→ _create_interval_run()
  │     │     └─→ _create_long_run()
  │     └─→ Week (criada)
  └─→ RunningPlan (completo)
        ↓
      Saída (print, PDF, JSON)
```

### 2. Criação de Plano com Zonas

```
Usuário (fornece tempos de prova)
  ↓
TrainingZones.add_race_time()
  ↓
TrainingZones.calculate_zones()
  ├─→ Jack Daniels: _calculate_jack_daniels_zones()
  │     ├─→ _calculate_vdot_from_race()
  │     └─→ _velocity_at_vdot()
  └─→ Critical Velocity: _calculate_critical_velocity_zones()
        └─→ CV = (D2-D1)/(T2-T1)
  ↓
TrainingZones (completo com zonas)
  ↓
PlanGenerator.generate_plan(training_zones=zones)
  ↓
  (cada treino recebe paces personalizados)
  ↓
RunningPlan (com zonas)
```

### 3. Criação de Plano com Perfil

```
Usuário (preenche widgets ou CLI)
  ↓
UserProfile (criado)
  ├─→ Informações pessoais
  ├─→ Experiência
  ├─→ Objetivos
  ├─→ Disponibilidade
  ├─→ Lesões
  └─→ Tempos de prova
        ↓
      PlanGenerator.generate_plan(user_profile=profile)
        ├─→ Calcula zonas automaticamente
        ├─→ Ajusta volume por lesões/IMC
        ├─→ Limita duração por tempo disponível
        └─→ Adiciona avisos
              ↓
            RunningPlan (personalizado)
```

### 4. Visualização e Exportação

```
RunningPlan
  ↓
  ├─→ print_visual() → Saída console
  ├─→ plot_weekly_volume() → Gráfico matplotlib
  ├─→ plot_zone_distribution_stacked() → Gráfico matplotlib
  ├─→ save_to_file() → JSON
  └─→ export_plan_to_pdf() → PDF
        ├─→ Gera elementos reportlab
        ├─→ Inclui gráficos (matplotlib → PNG → PDF)
        └─→ Constrói documento final
```

---

## 🎯 Casos de Uso

### Caso 1: Usuário Iniciante sem Conhecimento Técnico

```python
# Via Notebook com Widgets
from notebook_widgets import create_simple_plan_widgets

widgets = create_simple_plan_widgets()
# Usuário preenche interface visual
# Clica em "Gerar Plano"
# Sistema cria e exibe plano automaticamente
```

### Caso 2: Usuário Avançado com Tempos de Prova

```python
# Via código Python
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator

# Configurar zonas
zones = TrainingZones(method='jack_daniels')
zones.add_race_time("5K", RaceTime.from_time_string(5.0, "22:30"))
zones.add_race_time("10K", RaceTime.from_time_string(10.0, "47:15"))
zones.calculate_zones()

# Gerar plano
plan = PlanGenerator.generate_plan(
    name="Plano 10K",
    goal="10K",
    level="intermediate",
    weeks=10,
    days_per_week=4,
    training_zones=zones
)

# Exportar
plan.save_to_file("plano.json")
from pdf_export import save_plan_as_pdf
save_plan_as_pdf(plan)
```

### Caso 3: Personalização Total com Perfil

```python
# Via widgets completos
from notebook_widgets import create_complete_plan_widgets

widgets = create_complete_plan_widgets()
# Usuário preenche:
#   - Informações pessoais
#   - Experiência
#   - Objetivos
#   - Disponibilidade
#   - Tempos de prova
#   - Lesões
# Sistema gera plano totalmente personalizado
```

---

## 📦 Dependências

### Obrigatórias
- Python 3.7+
- Biblioteca padrão: `json`, `datetime`, `dataclasses`, `typing`, `math`

### Opcionais (para funcionalidades extras)
- `matplotlib` - Gráficos de visualização
- `reportlab` - Exportação PDF
- `ipywidgets` - Interface interativa em notebooks
- `IPython` - Display em notebooks

### Instalação no Google Colab
```python
!pip install ipywidgets reportlab matplotlib
```

---

## 🔧 Extensibilidade

### Adicionar Novo Tipo de Treino

1. Adicionar método em `PlanGenerator`:
```python
@classmethod
def _create_hill_run(cls, day, distance_km, zones):
    # Implementar treino de subida
    return Workout(...)
```

2. Adicionar emoji em `Workout.get_emoji()`:
```python
elif self.type == "Hill Run":
    return "⛰️"
```

3. Usar em `_generate_X_day_week()`:
```python
workouts.append(cls._create_hill_run("Wednesday", distances[2], zones))
```

### Adicionar Novo Método de Cálculo de Zonas

1. Adicionar método em `TrainingZones`:
```python
def _calculate_custom_zones(self):
    # Implementar novo método
    self.zones = {...}
```

2. Adicionar condição em `calculate_zones()`:
```python
elif self.method == 'custom':
    self._calculate_custom_zones()
```

### Adicionar Nova Visualização

1. Criar função em `plot_utils.py`:
```python
def plot_training_distribution(plan, figsize=(12, 6)):
    # Implementar nova visualização
    return fig, ax
```

2. Usar em notebooks ou PDF export

---

## 🧪 Testes

### Estrutura de Testes

```
test_example.py          # Testes básicos
test_enhanced.py         # Testes de zonas de treino
test_new_features.py     # Testes de arredondamento e visualizações
```

### Executar Testes

```bash
python test_new_features.py
```

---

## 📝 Convenções de Código

### Nomenclatura
- **Classes**: PascalCase (`RunningPlan`, `PlanGenerator`)
- **Funções/Métodos**: snake_case (`generate_plan`, `calculate_zones`)
- **Constantes**: UPPER_SNAKE_CASE (`GOAL_TARGETS`, `COMMON_INJURIES`)
- **Variáveis**: snake_case (`distance_km`, `total_weeks`)

### Docstrings
- Todas as classes e métodos públicos têm docstrings
- Formato: descrição breve + parâmetros + retorno

### Type Hints
- Usado extensivamente para clareza
- Importações: `from typing import List, Dict, Optional, Tuple`

### Dataclasses
- Classes de dados usam `@dataclass` decorator
- Facilita serialização JSON e reduz boilerplate

---

## 🚀 Performance

### Otimizações Implementadas
- Cálculo de VDOT usa método iterativo (Newton) - 10 iterações
- Zonas são calculadas uma vez e reutilizadas
- Gráficos usam backend 'Agg' (sem display) para velocidade
- PDF usa cache temporário para imagens

### Limitações Conhecidas
- Emojis podem não renderizar em alguns PDFs (warning ignorável)
- matplotlib requer ambiente com libfreetype

---

## 📖 Glossário

- **VDOT**: VO2max ajustado (Jack Daniels)
- **CV**: Critical Velocity (Velocidade Crítica)
- **Pace**: Ritmo em minutos por km
- **Taper**: Redução de volume pré-prova
- **Threshold**: Limiar anaeróbico
- **VO2max**: Consumo máximo de oxigênio
- **FC**: Frequência cardíaca
- **IMC/BMI**: Índice de Massa Corporal

---

**Fim da Documentação**

Para dúvidas ou contribuições, consulte o README.md ou abra uma issue no repositório.
