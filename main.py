import questionary
import sys
import os
import contextlib
from db import get_db, input_data_database, get_completion_dates, get_habit_periodicity, edit_habit, delete_habit
from habit import Habit, get_current_habits
from analyse import get_longest_run_streak, get_longest_run_streak_all_habits


def suppress_stdout(func=None):
    """Can be used both as a decorator and context manager to suppress stdout."""
    if func is None:
        # Being used as a context manager
        @contextlib.contextmanager
        def manager():
            original_stdout = sys.stdout
            with open(os.devnull, 'w') as devnull:
                sys.stdout = devnull
                try:
                    yield
                finally:
                    sys.stdout = original_stdout
        return manager()
    else:
        # Being used as a decorator
        def wrapper(*args, **kwargs):
            original_stdout = sys.stdout
            with open(os.devnull, 'w') as devnull:
                sys.stdout = devnull
                try:
                    return func(*args, **kwargs)
                finally:
                    sys.stdout = original_stdout
        return wrapper


def cli(completion_dates=None, name=None, current_habits=None):
    db_connect = get_db("main.db")  # Ensure the database name is specified
    if db_connect is None:
        print("Database connection failed.")
        return

    questionary.confirm("Do you want to continue").ask()

    # Initialize the database with data, suppress unwanted output
    with suppress_stdout():
        input_data_database(db_connect)

    stop = False
    while not stop:

        if current_habits is None:
            current_habits = []

        # Ensure current_habits is a list of Habit objects
        if not all(isinstance(habit, Habit) for habit in current_habits):
            raise ValueError("current_habits must be a list of Habit objects.")

        if name is None:
            # Prompt user to set a name only if it hasn't been set yet
            name = questionary.text("Please provide a name for the habit").ask()
            if not name:
                print("No name provided. Exiting.")
                return  # Exit if no name is provided

        choice = questionary.select(
            "What do you want to do?",
            choices=["Create", "Get completion dates", "Analyse", "Edit Habit", "Delete Habit", "Exit"]
        ).ask()

        if choice == "Create":
            name = questionary.text("What is the name of the habit?").ask()
            periodicity = questionary.text("What is the periodicity of the habit?").ask()
            habit = Habit(name, periodicity, db_connect)
            habit.store(db_connect)  # Assuming store method saves the habit to the database
            continue

        elif choice == "Get completion dates":
            # Retrieve all habits from the database to ensure the name is valid
            with suppress_stdout():
                current_habits = get_current_habits(db_connect)
            if not current_habits:
                print("No current habits found.")
                continue

            # Extract habit names from the list of Habit objects
            habit_names = [habit.name for habit in current_habits]

            # Select a habit to get completion dates
            habit_name = questionary.select("Select a habit to get completion dates:",
                                            choices=habit_names).ask()

            # Get completion dates for the selected habit
            completion_dates = get_completion_dates(db_connect, habit_name)  # type: ignore

            if not completion_dates:
                print(f"No completion dates found for habit '{habit_name}'.")
            else:
                print(f"Completion Dates for '{habit_name}':")
                for date in completion_dates:
                    print(date)  # Assuming date is the first element in the tuple

        elif choice == "Analyse":
            # Retrieve all habits for analysis
            with suppress_stdout():
                current_habits = get_current_habits(db_connect)
            if not current_habits:
                print("No current habits found.")
                continue

            # Display analysis options
            analysis_choice = questionary.select(
                "What would you like to analyse?",
                choices=[
                    "List all currently tracked habits",
                    "List all habits with the same periodicity",
                    "Get the longest run streak of all habits",
                    "Get the longest run streak for a specific habit",
                    "Get the longest run streak by periodicity"
                ]
            ).ask()

            if analysis_choice == "List all currently tracked habits":
                # Return a list of all currently tracked habits
                print("All Currently Tracked Habits:")
                for habit in current_habits:
                    print(f"- {habit}")

            elif analysis_choice == "List all habits with the same periodicity":
                # Return a list of all habits with the same periodicity
                periodicity = questionary.select(
                    "Select a periodicity:",
                    choices=["Daily", "Weekly"]
                ).ask()

                with suppress_stdout():
                    habits_with_periodicity = [habit for habit in current_habits if
                                               get_habit_periodicity(db_connect, habit.name) == periodicity]
                print(f"Habits with '{periodicity}' periodicity:")
                for habit in habits_with_periodicity:
                    print(f"- {habit}")

            elif analysis_choice == "Get the longest run streak of all habits":
                try:
                    with suppress_stdout():
                        longest_streak_all_habits = suppress_stdout(get_longest_run_streak_all_habits)(db_connect)
                    print(f"The longest run streak across all habits is: {longest_streak_all_habits}.")
                except Exception as e:
                    print(f"An error occurred: {e}")

            elif analysis_choice == "Get the longest run streak for a specific habit":
                # Retrieve all habits for analysis
                with suppress_stdout():
                    current_habits = get_current_habits(db_connect)
                if not current_habits:
                    print("No current habits found.")
                    continue

                habit_names = [habit.name for habit in current_habits]
                for habit in current_habits:
                    print(f"- {habit.name}")  # Assuming habit has a name attribute

                # Select a habit to analyze
                selected_habit_name = questionary.select("Select a habit to get the longest run streak:",
                                                         choices=habit_names).ask()
                # Find the selected habit object
                try:
                    habit_obj: Habit = next(habit for habit in current_habits if habit.name == selected_habit_name)
                    print(f"selected Habit is: {selected_habit_name}.")
                except StopIteration:
                    print(f"Error: Habit '{selected_habit_name}' not found in the current habits.")
                    continue

                # Call the get_longest_run_streak method on the selected habit object
                longest_streak = habit_obj.get_longest_run_streak()

                if longest_streak is None:
                    print(f"No run streak data found for habit '{selected_habit_name}'.")
                else:
                    print(f"The longest run streak for '{selected_habit_name}' is: {longest_streak}.")

            elif analysis_choice == "Get the longest run streak by periodicity":
                # Retrieve all habits for analysis
                with suppress_stdout():
                    current_habits = get_current_habits(db_connect)
                if not current_habits:
                    print("No current habits found.")
                    continue

                # Group habits by periodicity
                daily_habits = [h for h in current_habits if h.periodicity == "Daily"]
                weekly_habits = [h for h in current_habits if h.periodicity == "Weekly"]

                # Calculate the longest streak for daily habits
                longest_run_daily_streak = 0
                for habit in daily_habits:
                    current_streak = habit.get_longest_run_streak()
                    longest_run_daily_streak = max(longest_run_daily_streak, current_streak)

                # Calculate the longest streak for weekly habits
                longest_run_weekly_streak = 0
                habit: Habit
                for habit in weekly_habits:
                    current_streak = habit.get_longest_run_streak()
                    longest_run_weekly_streak = max(longest_run_weekly_streak, current_streak)

                # Display the results
                print(f"Longest run streak for daily habits: {longest_run_daily_streak}")
                print(f"Longest run streak for weekly habits: {longest_run_weekly_streak}")

        elif choice == "Edit Habit":
            # Retrieve all habits for editing
            with suppress_stdout():
                current_habits = get_current_habits(db_connect)
            if not current_habits:
                print("No current habits found.")
                continue

            habit_names = [habit.name for habit in current_habits]

            # Select a habit to edit
            selected_habit_name = questionary.select("Select a habit to edit:",
                                                     choices=habit_names).ask()

            # Find the selected habit object
            try:
                habit_obj: Habit = next(habit for habit in current_habits if habit.name == selected_habit_name)
            except StopIteration:
                print(f"Error: Habit '{selected_habit_name}' not found in the current habits.")
                continue

            # Prompt for new details
            new_name = questionary.text("Enter new name (leave blank to keep current):").ask()
            new_periodicity = questionary.text(
                "Enter new periodicity (Daily/Weekly, leave blank to keep current):").ask()

            # Edit the habit
            try:
                habit_obj.edit_habit(new_name=new_name or None, new_periodicity=new_periodicity or None)
                print(f"Habit '{selected_habit_name}' updated successfully!")
            except ValueError as e:
                print(f"Error: {e}")

        elif choice == "Delete Habit":
            # Retrieve all habits for deletion
            with suppress_stdout():
                current_habits = get_current_habits(db_connect)
            if not current_habits:
                print("No current habits found.")
                continue

            habit_names = [habit.name for habit in current_habits]

            # Select a habit to delete
            selected_habit_name = questionary.select("Select a habit to delete:",
                                                     choices=habit_names).ask()

            # Find the selected habit object
            try:
                habit_obj: Habit = next(habit for habit in current_habits if habit.name == selected_habit_name)
            except StopIteration:
                print(f"Error: Habit '{selected_habit_name}' not found in the current habits.")
                continue

            # Confirm deletion
            confirm = questionary.confirm(f"Are you sure you want to delete '{selected_habit_name}'?").ask()
            if confirm:
                habit_obj.delete_habit()
                print(f"Habit '{selected_habit_name}' deleted successfully!")
            else:
                print("Deletion canceled.")

        else:

            print("Bye!")
            stop = True

            break
    db_connect.close()  # Ensure the database connection is closed when done


if __name__ == "__main__":
    cli(completion_dates=None, name=None, current_habits=None)
