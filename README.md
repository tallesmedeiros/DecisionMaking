# Running Plan Creator

A comprehensive Python-based software for creating personalized running training plans. Whether you're training for a 5K, 10K, Half Marathon, or Marathon, this tool generates structured training schedules tailored to your experience level and goals.

## Features

- **Multiple Race Distances**: Support for 5K, 10K, Half Marathon, and Marathon training
- **Three Experience Levels**: Beginner, Intermediate, and Advanced plans
- **Flexible Training Schedule**: 3 to 6 training days per week
- **Progressive Training**: Intelligent build-up, peak, and taper phases
- **Variety of Workouts**: Easy runs, tempo runs, intervals, fartlek, and long runs
- **Plan Persistence**: Save and load training plans as JSON files
- **Interactive CLI**: User-friendly command-line interface
- **Date Planning**: Set start dates and calculate race dates

### 🆕 Advanced Features (NEW!)

- **Training Zones Calculator**: Personalized pace zones based on recent race times
  - Jack Daniels VDOT method (VO2max based)
  - Critical Velocity method
- **Detailed Workout Structure**: Each session includes:
  - Specific target pace for the workout
  - Estimated total time
  - Warmup segment with pace and duration
  - Main work intervals with repetitions
  - Recovery periods between intervals
  - Cooldown segment
- **5 Training Zones**: Easy, Marathon, Threshold, Interval, Repetition
- **Personalized Paces**: Based on your 5K, 10K, Half Marathon, or Marathon times
- **Backward Compatible**: Works with or without training zones

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd DecisionMaking
```

2. Ensure you have Python 3.7 or higher installed:
```bash
python --version
```

No additional dependencies required - uses only Python standard library!

## Quick Start

### 🌐 Google Colab (Easiest - No Installation Required!)

**Use o sistema direto no seu navegador sem instalar nada!**

1. **Abra o notebook interativo no Google Colab:**
   - [🚀 Clique aqui para abrir no Colab](https://colab.research.google.com/github/tallesmedeiros/DecisionMaking/blob/claude/build-basic-software-01X41XJpgLktdj8FhFWitNo3/create_plan_interactive.ipynb)

2. **Execute a primeira célula para clonar os arquivos:**
   ```python
   !git clone https://github.com/tallesmedeiros/DecisionMaking.git
   %cd DecisionMaking
   ```

3. **Preencha suas informações nas 12 seções interativas**

4. **Receba seu plano personalizado!**

📖 **[Ver guia completo em Português](GUIA_GOOGLE_COLAB.md)**

**O que você recebe:**
- ✅ Plano personalizado com base em seus dados (idade, peso, lesões, tempo disponível)
- ✅ Zonas de treino calculadas automaticamente dos seus tempos de prova
- ✅ Ajustes inteligentes para lesões e risco de lesão
- ✅ Treinos limitados ao tempo que você tem disponível
- ✅ Avisos e recomendações específicas para seu perfil

---

### Jupyter Notebook (Recommended for Learning)
For an interactive, educational experience with examples and visualizations:
```bash
jupyter notebook running_plan_creator.ipynb
```

The notebook includes:
- 17 interactive sections with examples
- Step-by-step tutorials in Portuguese
- Visualization of training progression
- Personalization guide
- Training tips and best practices

### Interactive Mode
Run the CLI in interactive mode for a guided experience:
```bash
python cli.py
```

### Quick Plan Creation
Generate a plan with smart defaults:
```bash
python cli.py quick
```

### View Existing Plan
View a saved training plan:
```bash
python cli.py view my_plan.json
```

## Usage Examples

### Basic Plan Creation

```bash
python cli.py
```

Then follow the prompts:
- Choose "Create new plan (detailed)"
- Enter plan name
- Select race goal (5K, 10K, Half Marathon, Marathon)
- Choose experience level (beginner, intermediate, advanced)
- Set number of weeks
- Set training days per week
- Optionally set start date

### 🆕 Advanced: Plan with Training Zones

Create a personalized plan with pace-based workouts:

```bash
python example_with_zones.py
```

Or use the Python API:

```python
from training_zones import TrainingZones, RaceTime
from plan_generator import PlanGenerator
from datetime import datetime

# 1. Setup training zones based on recent race times
zones = TrainingZones(method='jack_daniels')  # or 'critical_velocity'

# Add your recent race times (format: "MM:SS" or "HH:MM:SS")
race_5k = RaceTime.from_time_string(5.0, "22:30")   # 5K in 22:30
race_10k = RaceTime.from_time_string(10.0, "47:15")  # 10K in 47:15

zones.add_race_time("5K Recent", race_5k)
zones.add_race_time("10K Recent", race_10k)
zones.calculate_zones()

# View your training zones
print(zones)  # Shows VDOT and pace ranges for each zone

# 2. Generate plan WITH training zones
plan = PlanGenerator.generate_plan(
    name="My 10K Plan with Zones",
    goal="10K",
    level="intermediate",
    weeks=10,
    days_per_week=4,
    training_zones=zones  # Pass zones here!
)

plan.set_start_date(datetime(2025, 1, 6))

# 3. View detailed workout
week4 = plan.get_week(4)
for workout in week4.workouts:
    print(workout)  # Shows pace, time, and detailed structure

# 4. Save the plan
plan.save_to_file("my_plan_with_zones.json")
```

### Basic API Usage (Without Zones)

```python
from plan_generator import PlanGenerator
from datetime import datetime

# Generate a basic plan
plan = PlanGenerator.generate_plan(
    name="My Marathon Training",
    goal="Marathon",
    level="intermediate",
    weeks=16,
    days_per_week=5
)

# Set start date
plan.set_start_date(datetime(2025, 1, 1))

# Save to file
plan.save_to_file("my_marathon_plan.json")

# Display the plan
print(plan)

# Load from file
from running_plan import RunningPlan
loaded_plan = RunningPlan.load_from_file("my_marathon_plan.json")
```

## Training Plan Structure

### Workout Types

- **Easy Run**: Comfortable pace, conversational effort
- **Tempo Run**: Sustained effort at comfortably hard pace
- **Interval Training**: Speed work with fast/recovery segments
- **Fartlek**: Play with pace, alternating speeds
- **Long Run**: Endurance building at easy pace
- **Rest**: Recovery day

### Training Phases

1. **Build Phase** (70% of plan): Gradual increase in weekly mileage
2. **Maintenance Phase**: Peak training load
3. **Taper Phase** (last 2 weeks): Reduced volume for recovery

### Weekly Distance Targets

Base weekly mileage varies by goal and level:

| Goal | Beginner | Intermediate | Advanced |
|------|----------|--------------|----------|
| 5K | 20 km | 30 km | 40 km |
| 10K | 30 km | 45 km | 60 km |
| Half Marathon | 40 km | 60 km | 80 km |
| Marathon | 50 km | 75 km | 100 km |

## File Structure

```
DecisionMaking/
├── cli.py                        # Command-line interface
├── running_plan.py               # Core classes (RunningPlan, Week, Workout, WorkoutSegment)
├── plan_generator.py             # Training plan generation logic
├── training_zones.py             # Training zones calculator (VDOT & Critical Velocity)
├── running_plan_creator.ipynb    # Jupyter Notebook (interactive tutorial)
├── test_example.py               # Basic test and demonstration script
├── test_enhanced.py              # Advanced features test script
├── example_with_zones.py         # Example usage with training zones
└── README.md                     # This file
```

## Example Output

### Basic Plan (Without Zones)

```
==================================================
Running Plan: My Marathon Training
Goal: Marathon
Level: Intermediate
Duration: 16 weeks
Training Days: 5 days/week
Start Date: 2025-01-01
Race Date: 2025-04-30
==================================================

=== Week 1 ===
Total Distance: 26.8 km
Notes: Welcome to your training plan! Start easy and focus on consistency.

Monday: Easy Run - 5.4 km
  Start week with comfortable pace
Tuesday: Easy Run - 4.8 km
  Recovery pace
Wednesday: Rest
  Recovery day
Thursday: Easy Run - 5.4 km
  Build aerobic base
Friday: Easy Run - 4.0 km
  Short recovery run
Saturday: Rest
  Recovery day
Sunday: Long Run - 7.2 km
  Build endurance at conversational pace
```

### 🆕 Advanced Plan (With Training Zones)

```
Training Zones (Method: jack_daniels)
============================================================
VDOT: 43.4

Recent Race Times:
  5K Recent: 5.0km in 22:30 (4:30/km)
  10K Recent: 10.0km in 47:15 (4:43/km)

Training Zones (pace per km):
  Easy/Recovery       : 5:28 - 6:33
  Marathon Pace       : 4:57 - 5:25
  Threshold/Tempo     : 4:46 - 5:00
  Interval/5K         : 4:18 - 4:29
  Repetition/Fast     : 3:42 - 4:08

----------------------------------------------------------------------
SEMANA 4 - Com Treinos de Qualidade
----------------------------------------------------------------------

Tuesday: Easy Run - 8.0 km (48:23) @ 6:01/km [EASY]
  Ritmo confortável, esforço conversacional

Thursday: Interval Training - 7.1 km (31:04) @ 4:23/km [INTERVAL]
  Treino de velocidade: tiros em ritmo de 5K
  Estrutura do Treino:
  • Aquecimento: 1.4 km, 8 min, @ 6:01/km
    Preparação com ritmo fácil
  • 4x Tiro (Intervalo Rápido): 0.62 km, 2 min, @ 4:23/km
    Ritmo de 5K - esforço intenso
  • 4x Recuperação (trote/caminhada): 2 min, @ 6:01/km
    Recuperação ativa entre tiros
  • Desaquecimento: 1.4 km, 8 min, @ 6:01/km
    Volta à calma

Friday: Easy Run - 5.8 km (34:50) @ 6:01/km [EASY]
  Ritmo confortável, esforço conversacional

Sunday: Long Run - 11.2 km (1:13:48) @ 6:33/km [EASY]
  Construir resistência em ritmo fácil
```

## Tips for Success

1. **Start Conservative**: Better to undertrain slightly than risk injury
2. **Listen to Your Body**: Take extra rest days if needed
3. **Consistency is Key**: Regular training is more important than individual workouts
4. **Recovery Matters**: Rest days are when your body adapts and gets stronger
5. **Cross-Training**: Consider swimming, cycling, or strength training on rest days
6. **Nutrition & Hydration**: Fuel your training properly
7. **Trust the Plan**: Especially during taper - resist the urge to do more

## Customization

The plan generator uses intelligent defaults, but you can customize:
- Modify `GOAL_TARGETS` in `plan_generator.py` to adjust weekly mileage
- Edit workout distributions in the `_generate_X_day_week` methods
- Adjust build/taper percentages in `_generate_week` method

## Contributing

Feel free to submit issues, feature requests, or pull requests!

## License

This project is open source and available under the MIT License.

## Disclaimer

This software generates general training plans. Always consult with a healthcare provider before starting a new exercise program. Listen to your body and adjust the plan as needed to prevent injury.