#!/usr/bin/env python3
"""
Command-Line Interface for Running Plan Creator.
Allows users to create, view, and manage running plans.
"""
import sys
from datetime import datetime
from running_plan import RunningPlan
from plan_generator import PlanGenerator


def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("         RUNNING PLAN CREATOR")
    print("="*60 + "\n")


def get_user_choice(prompt: str, options: list) -> str:
    """Get user choice from a list of options."""
    print(prompt)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)


def get_user_input(prompt: str, default=None) -> str:
    """Get text input from user."""
    try:
        if default is not None:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            while True:
                user_input = input(f"{prompt}: ").strip()
                if user_input:
                    return user_input
                print("This field is required. Please enter a value.")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        sys.exit(0)


def get_number_input(prompt: str, min_val: int = None, max_val: int = None, default: int = None) -> int:
    """Get numeric input from user."""
    while True:
        try:
            if default:
                user_input = input(f"{prompt} [{default}]: ").strip()
                if not user_input:
                    return default
                value = int(user_input)
            else:
                value = int(input(f"{prompt}: "))

            if min_val is not None and value < min_val:
                print(f"Please enter a number >= {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Please enter a number <= {max_val}")
                continue

            return value
        except ValueError:
            print("Please enter a valid number")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)


def get_yes_no(prompt: str, default: bool = False) -> bool:
    """Get yes/no input from user."""
    default_str = "Y/n" if default else "y/N"
    try:
        while True:
            response = input(f"{prompt} [{default_str}]: ").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")
        sys.exit(0)


def get_date_input(prompt: str, allow_skip: bool = False, default: str = None):
    """Get a date from user in YYYY-MM-DD format."""

    while True:
        try:
            if default:
                raw = input(f"{prompt} [{default}]: ").strip()
                if not raw:
                    raw = default
            else:
                raw = input(f"{prompt}: ").strip()

            if allow_skip and not raw:
                return None

            return datetime.strptime(raw, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)


def get_time_input(prompt: str, allow_skip: bool = False):
    """Get a time string in HH:MM:SS or MM:SS format."""

    while True:
        try:
            raw = input(f"{prompt}: ").strip()
            if allow_skip and not raw:
                return None

            parts = raw.split(":")
            if len(parts) not in (2, 3):
                print("Use HH:MM:SS or MM:SS format")
                continue

            # Validate numeric values
            if not all(part.isdigit() for part in parts):
                print("Use only numbers and colons (e.g., 00:45:00)")
                continue

            return raw
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            sys.exit(0)


def create_new_plan():
    """Interactive function to create a new running plan."""
    print("\n--- Create New Running Plan ---\n")

    # Get plan name
    plan_name = get_user_input("Plan name", default=f"My Training Plan {datetime.now().strftime('%Y-%m-%d')}")

    # Get event and goal
    event_distance = get_user_choice(
        "\nWhat is your target race distance?",
        ["5K", "10K", "Half Marathon", "Marathon"]
    )

    event_date = get_date_input(
        "When is your target race? (YYYY-MM-DD)", allow_skip=True
    )
    event_name = get_user_input("Race name", default="")
    event_location = get_user_input("Race location (city/region)", default="")
    event_info_source = get_user_input(
        "Official site or course link (optional)", default=""
    )

    # Get level
    level = get_user_choice(
        "\nWhat is your training level?",
        ["beginner", "intermediate", "advanced"]
    )

    # Get duration
    default_weeks = PlanGenerator._get_default_weeks(event_distance)
    weeks = get_number_input(
        f"\nHow many weeks for your plan?",
        min_val=4,
        max_val=26,
        default=default_weeks
    )

    # Get days per week
    days_per_week = get_number_input(
        "\nHow many days per week do you want to train?",
        min_val=3,
        max_val=6,
        default=4
    )

    # Get performance context
    current_pb = get_time_input("\nWhat's your current PB for this distance? (HH:MM:SS)", allow_skip=True)
    target_time = get_time_input("What's your target finish time? (HH:MM:SS)", allow_skip=True)

    # Motivation and logistics
    motivation = get_user_input("\nWhat's your main motivation for this race?", default="")
    logistics_raw = get_user_input(
        "Any logistical constraints (surface, schedule, location)? Separate by commas",
        default=""
    )
    logistics = [item.strip() for item in logistics_raw.split(',') if item.strip()]

    print("\n--- Race Day Environment ---")
    hotter_or_more_humid = get_yes_no(
        "Is the race expected to be hotter or more humid than your usual training?",
        default=False,
    )
    more_gain_or_descents = get_yes_no(
        "Will the race have more elevation gain/descents than you're used to?",
        default=False,
    )
    colder_or_windier = get_yes_no(
        "Is the race likely colder or windier than your baseline?",
        default=False,
    )

    # Confirm
    print("\n--- Plan Summary ---")
    print(f"Name: {plan_name}")
    print(f"Goal: {event_distance}")
    if event_date:
        print(f"Race Date: {event_date.strftime('%Y-%m-%d')}")
    if event_name:
        print(f"Race Name: {event_name}")
    if event_location:
        print(f"Race Location: {event_location}")
    if event_info_source:
        print(f"Reference Link: {event_info_source}")
    print(f"Level: {level}")
    print(f"Duration: {weeks} weeks")
    print(f"Training Days: {days_per_week} days/week")
    if current_pb:
        print(f"Current PB: {current_pb}")
    if target_time:
        print(f"Target Time: {target_time}")
    if motivation:
        print(f"Motivation: {motivation}")
    if logistics:
        print(f"Logistics: {', '.join(logistics)}")

    if not get_yes_no("\nCreate this plan?", default=True):
        print("Plan creation cancelled.")
        return None

    # Generate plan
    print("\nGenerating your training plan...")
    plan = PlanGenerator.generate_plan(
        name=plan_name,
        goal=event_distance,
        level=level,
        weeks=weeks,
        days_per_week=days_per_week
    )

    # Attach contextual data
    if event_date:
        plan.set_event_info(
            event_distance,
            event_date,
            name=event_name,
            location=event_location,
            info_source=event_info_source,
        )

    if target_time or current_pb:
        plan.set_performance_targets(current_pb, target_time, distance_label=event_distance)

    plan.update_training_context(motivation=motivation, logistics=logistics)
    plan.update_environment_strategy(
        hotter_or_more_humid=hotter_or_more_humid,
        more_gain_or_descents=more_gain_or_descents,
        colder_or_windier=colder_or_windier,
    )

    # Ask for start date
    if get_yes_no("\nWould you like to set a start date?", default=True):
        while True:
            date_str = get_user_input("Enter start date (YYYY-MM-DD)", default=datetime.now().strftime('%Y-%m-%d'))
            try:
                start_date = datetime.strptime(date_str, '%Y-%m-%d')
                plan.set_start_date(start_date)
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD")

    # Save plan
    filename = f"{plan_name.replace(' ', '_').lower()}.json"
    plan.save_to_file(filename)
    print(f"\nPlan saved to: {filename}")

    return plan


def view_plan():
    """View an existing plan."""
    print("\n--- View Running Plan ---\n")
    filename = get_user_input("Enter plan filename")

    try:
        plan = RunningPlan.load_from_file(filename)
        print(plan)

        # Ask if user wants to see specific week
        if get_yes_no("\nView a specific week in detail?", default=False):
            week_num = get_number_input("Which week?", min_val=1, max_val=plan.weeks)
            week = plan.get_week(week_num)
            if week:
                print(week)
            else:
                print(f"Week {week_num} not found")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error loading plan: {e}")


def quick_plan():
    """Create a quick plan with minimal input."""
    print("\n--- Quick Plan Generator ---\n")
    print("Let's create a plan with smart defaults!\n")

    goal = get_user_choice("What's your goal?", ["5K", "10K", "Half Marathon", "Marathon"])
    level = get_user_choice("Your experience level?", ["beginner", "intermediate", "advanced"])

    plan_name = f"{goal} Training Plan - {datetime.now().strftime('%Y-%m-%d')}"
    plan = PlanGenerator.generate_plan(
        name=plan_name,
        goal=goal,
        level=level
    )

    # Set start date to next Monday
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday = today + timedelta(days=days_until_monday)
    plan.set_start_date(next_monday)

    filename = f"{plan_name.replace(' ', '_').lower()}.json"
    plan.save_to_file(filename)

    print(f"\nPlan created and saved to: {filename}")
    print(f"Start date: {next_monday.strftime('%Y-%m-%d')}")
    print(f"Race date: {plan.get_race_date().strftime('%Y-%m-%d')}")

    if get_yes_no("\nView the full plan?", default=True):
        print(plan)


def main_menu():
    """Display main menu and handle user choice."""
    while True:
        print("\n" + "="*60)
        print("MAIN MENU")
        print("="*60)

        choice = get_user_choice(
            "\nWhat would you like to do?",
            [
                "Create new plan (detailed)",
                "Create quick plan (with defaults)",
                "View existing plan",
                "Exit"
            ]
        )

        if choice.startswith("Create new"):
            plan = create_new_plan()
            if plan and get_yes_no("\nView the plan now?", default=True):
                print(plan)

        elif choice.startswith("Create quick"):
            quick_plan()

        elif choice.startswith("View"):
            view_plan()

        elif choice == "Exit":
            print("\nThank you for using Running Plan Creator!")
            print("Happy running!\n")
            sys.exit(0)


def main():
    """Main entry point."""
    print_banner()

    # Check if command line arguments provided
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "quick":
            quick_plan()
        elif command == "view":
            if len(sys.argv) > 2:
                try:
                    plan = RunningPlan.load_from_file(sys.argv[2])
                    print(plan)
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Usage: python cli.py view <filename>")
        elif command == "help":
            print("Running Plan Creator - Command Line Interface\n")
            print("Usage:")
            print("  python cli.py           - Interactive mode")
            print("  python cli.py quick     - Quick plan creation")
            print("  python cli.py view <file> - View a saved plan")
            print("  python cli.py help      - Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'python cli.py help' for usage information")
    else:
        # Interactive mode
        main_menu()


if __name__ == "__main__":
    from datetime import timedelta
    main()
