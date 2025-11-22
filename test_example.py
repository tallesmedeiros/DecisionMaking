#!/usr/bin/env python3
"""
Test script to demonstrate the Running Plan Creator functionality.
"""
from plan_generator import PlanGenerator
from running_plan import RunningPlan
from datetime import datetime

def test_plan_generation():
    """Test generating different types of plans."""
    print("="*60)
    print("Testing Running Plan Creator")
    print("="*60)

    # Test 1: Generate a beginner 5K plan
    print("\n1. Generating Beginner 5K Plan...")
    plan_5k = PlanGenerator.generate_plan(
        name="Beginner 5K Training",
        goal="5K",
        level="beginner",
        weeks=8,
        days_per_week=3
    )
    plan_5k.set_start_date(datetime(2025, 1, 1))
    print(f"✓ Created {plan_5k.weeks}-week plan with {len(plan_5k.schedule)} weeks")
    print(f"  Total workouts: {sum(len(w.workouts) for w in plan_5k.schedule)}")

    # Test 2: Generate an intermediate 10K plan
    print("\n2. Generating Intermediate 10K Plan...")
    plan_10k = PlanGenerator.generate_plan(
        name="Intermediate 10K Training",
        goal="10K",
        level="intermediate",
        weeks=10,
        days_per_week=4
    )
    plan_10k.set_start_date(datetime(2025, 2, 1))
    print(f"✓ Created {plan_10k.weeks}-week plan with {len(plan_10k.schedule)} weeks")

    # Test 3: Generate an advanced Half Marathon plan
    print("\n3. Generating Advanced Half Marathon Plan...")
    plan_half = PlanGenerator.generate_plan(
        name="Advanced Half Marathon Training",
        goal="Half Marathon",
        level="advanced",
        weeks=12,
        days_per_week=5
    )
    plan_half.set_start_date(datetime(2025, 3, 1))
    print(f"✓ Created {plan_half.weeks}-week plan with {len(plan_half.schedule)} weeks")

    # Test 4: Generate a Marathon plan
    print("\n4. Generating Marathon Plan...")
    plan_marathon = PlanGenerator.generate_plan(
        name="Marathon Training",
        goal="Marathon",
        level="intermediate",
        weeks=16,
        days_per_week=5
    )
    plan_marathon.set_start_date(datetime(2025, 1, 6))
    print(f"✓ Created {plan_marathon.weeks}-week plan with {len(plan_marathon.schedule)} weeks")

    # Test save and load
    print("\n5. Testing Save and Load...")
    filename = "test_marathon_plan.json"
    plan_marathon.save_to_file(filename)
    print(f"✓ Saved plan to {filename}")

    loaded_plan = RunningPlan.load_from_file(filename)
    print(f"✓ Loaded plan from {filename}")
    print(f"  Plan name: {loaded_plan.name}")
    print(f"  Goal: {loaded_plan.goal}")
    print(f"  Weeks: {len(loaded_plan.schedule)}")

    # Display sample week
    print("\n6. Sample Week from Marathon Plan:")
    print("-" * 60)
    week_4 = plan_marathon.get_week(4)
    if week_4:
        print(week_4)

    # Display plan overview
    print("\n7. Full Marathon Plan Overview:")
    print("-" * 60)
    print(plan_marathon)

    print("\n" + "="*60)
    print("All tests completed successfully!")
    print("="*60)

if __name__ == "__main__":
    test_plan_generation()
