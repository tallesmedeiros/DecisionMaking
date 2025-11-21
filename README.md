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

### Creating a Custom Plan

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

### Using Python API

You can also use the modules directly in your own Python scripts:

```python
from plan_generator import PlanGenerator
from datetime import datetime

# Generate a plan
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
├── cli.py              # Command-line interface
├── running_plan.py     # Core classes (RunningPlan, Week, Workout)
├── plan_generator.py   # Training plan generation logic
└── README.md           # This file
```

## Example Output

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