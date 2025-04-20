from habit import Habit
from datetime import datetime, timedelta
from db import (get_db, add_habit as db_add_habit, edit_habit, delete_habit, get_current_habits,
                get_habits_by_periodicity,
                check_database_content, add_habit_with_periodicity, get_completion_dates, get_habit)
import pytest
import os


@pytest.fixture
def periodicity():
    # Check for an environment variable to determine the periodicity
    if os.getenv("TEST_PERIODICITY") == "Weekly":
        return "Weekly"
    else:
        return "Daily"


@pytest.fixture(params=["Exercise", "Make Daily To Do List", "Medication", "Study", "Laundry"])
def habit_name(request):
    """Fixture to provide different habit names for the tests."""
    return request.param


@pytest.fixture
def get_periodicity():
    # This is a nested function that will take habit_name as an argument
    def _get_periodicity(habit_name):
        if habit_name in ["Medication", "Laundry"]:
            return "Weekly"
        else:
            return "Daily"

    return _get_periodicity  # Return the nested function


@pytest.fixture(scope='module')
def db_connect():
    db_path = "test_habit.db"
    db_connect = get_db(db_path)
    cur = db_connect.cursor()
    cur.execute("DELETE FROM tracker")
    cur.execute("DELETE FROM habit")  # Clear existing habits
    db_connect.commit()

    yield db_connect

    db_connect.close()
    os.remove(db_path)


@pytest.fixture
def habit_list(db_connect):
    """Fixture to provide a list of Habit objects."""
    habits = [
        Habit("Medication", "Weekly", db_connect),
        Habit("Laundry", "Weekly", db_connect),
        Habit("Exercise", "Daily", db_connect),
        Habit("Make Daily To Do List", "Daily", db_connect),
        Habit("Study", "Daily", db_connect)
    ]
    return habits


@pytest.fixture(scope='module', autouse=True)
def add_habit(db_connect):
    """Fixture to add habits with and without periodicity to the database before tests."""

    # Define the habits with periodicity
    habit_data_with_periodicity = [
        ("Exercise", "Daily"),
        ("Make Daily To Do List", "Daily"),
        ("Study", "Daily"),
        ("Medication", "Weekly"),
        ("Laundry", "Weekly")
    ]

    # Define the simple habit names
    habit_names = ["Medication", "Laundry", "Exercise", "Make Daily To Do List", "Study"]

    # Add the habits with periodicity
    add_habit_with_periodicity(db_connect, habit_data_with_periodicity)

    # Add the simple habits to the database
    db_add_habit(db_connect, habit_names)


@pytest.fixture
def get_longest_run_streak(habit):
    """Calculate the longest run streak for all habits."""
    streaks = [habit.get_longest_run_streak() for habit in habit]
    return max(streaks) if streaks else 0


class TestHabit:

    @pytest.fixture
    def habit(self, db_connect):
        """Fixture to create a Habit instance with sample data."""
        habit_names = ["Medication", "Laundry", "Exercise", "Make Daily To Do List", "Study"]
        return [Habit(name=habit_name, periodicity="Weekly" if habit_name in ["Medication", "Laundry"] else "Daily",
                      db=db_connect) for habit_name in habit_names]

    @pytest.fixture
    def habit_data(self):
        return [
        ("Medication", "Weekly", [
            datetime(2025, 4, 1, 0, 0).isoformat(),
            datetime(2025, 4, 8, 0, 0).isoformat(),
            datetime(2025, 4, 15, 0, 0).isoformat(),
            datetime(2025, 4, 22, 0, 0).isoformat()
        ]),
        ("Laundry", "Weekly", [
            datetime(2025, 4, 3, 0, 0).isoformat(),
            datetime(2025, 4, 10, 0, 0).isoformat(),
            datetime(2025, 4, 17, 0, 0).isoformat(),
            datetime(2025, 4, 24, 0, 0).isoformat()
        ]),
        ("Exercise", "Daily", [
            datetime(2025, 4, 2, 0, 0).isoformat(),
            datetime(2025, 4, 3, 0, 0).isoformat(),
            datetime(2025, 4, 6, 0, 0).isoformat(),
            datetime(2025, 4, 7, 0, 0).isoformat(),
            datetime(2025, 4, 8, 0, 0).isoformat(),
            datetime(2025, 4, 10, 0, 0).isoformat(),
            datetime(2025, 4, 11, 0, 0).isoformat(),
            datetime(2025, 4, 12, 0, 0).isoformat(),
            datetime(2025, 4, 13, 0, 0).isoformat(),
            datetime(2025, 4, 14, 0, 0).isoformat(),
            datetime(2025, 4, 15, 0, 0).isoformat(),
            datetime(2025, 4, 16, 0, 0).isoformat(),
            datetime(2025, 4, 17, 0, 0).isoformat(),
            datetime(2025, 4, 18, 0, 0).isoformat(),
            datetime(2025, 4, 20, 0, 0).isoformat(),
            datetime(2025, 4, 21, 0, 0).isoformat(),
            datetime(2025, 4, 23, 0, 0).isoformat(),
            datetime(2025, 4, 24, 0, 0).isoformat(),
            datetime(2025, 4, 25, 0, 0).isoformat(),
            datetime(2025, 4, 26, 0, 0).isoformat(),
            datetime(2025, 4, 27, 0, 0).isoformat(),
            datetime(2025, 4, 28, 0, 0).isoformat(),
            datetime(2025, 4, 29, 0, 0).isoformat(),
            datetime(2025, 4, 30, 0, 0).isoformat()
        ]),
        ("Make Daily To Do List", "Daily", [
            datetime(2025, 4, 2, 0, 0).isoformat(),
            datetime(2025, 4, 4, 0, 0).isoformat(),
            datetime(2025, 4, 5, 0, 0).isoformat(),
            datetime(2025, 4, 6, 0, 0).isoformat(),
            datetime(2025, 4, 7, 0, 0).isoformat(),
            datetime(2025, 4, 9, 0, 0).isoformat(),
            datetime(2025, 4, 10, 0, 0).isoformat(),
            datetime(2025, 4, 11, 0, 0).isoformat(),
            datetime(2025, 4, 12, 0, 0).isoformat(),
            datetime(2025, 4, 13, 0, 0).isoformat(),
            datetime(2025, 4, 14, 0, 0).isoformat(),
            datetime(2025, 4, 17, 0, 0).isoformat(),
            datetime(2025, 4, 18, 0, 0).isoformat(),
            datetime(2025, 4, 19, 0, 0).isoformat(),
            datetime(2025, 4, 21, 0, 0).isoformat(),
            datetime(2025, 4, 22, 0, 0).isoformat(),
            datetime(2025, 4, 23, 0, 0).isoformat(),
            datetime(2025, 4, 25, 0, 0).isoformat(),
            datetime(2025, 4, 26, 0, 0).isoformat(),
            datetime(2025, 4, 28, 0, 0).isoformat(),
            datetime(2025, 4, 29, 0, 0).isoformat(),
            datetime(2025, 4, 30, 0, 0).isoformat()
        ]),
        ("Study", "Daily", [
            datetime(2025, 4, 1, 0, 0).isoformat(),
            datetime(2025, 4, 2, 0, 0).isoformat(),
            datetime(2025, 4, 3, 0, 0).isoformat(),
            datetime(2025, 4, 4, 0, 0).isoformat(),
            datetime(2025, 4, 5, 0, 0).isoformat(),
            datetime(2025, 4, 7, 0, 0).isoformat(),
            datetime(2025, 4, 8, 0, 0).isoformat(),
            datetime(2025, 4, 9, 0, 0).isoformat(),
            datetime(2025, 4, 10, 0, 0).isoformat(),
            datetime(2025, 4, 12, 0, 0).isoformat(),
            datetime(2025, 4, 13, 0, 0).isoformat(),
            datetime(2025, 4, 14, 0, 0).isoformat(),
            datetime(2025, 4, 15, 0, 0).isoformat(),
            datetime(2025, 4, 16, 0, 0).isoformat(),
            datetime(2025, 4, 17, 0, 0).isoformat(),
            datetime(2025, 4, 18, 0, 0).isoformat(),
            datetime(2025, 4, 19, 0, 0).isoformat(),
            datetime(2025, 4, 20, 0, 0).isoformat(),
            datetime(2025, 4, 21, 0, 0).isoformat(),
            datetime(2025, 4, 22, 0, 0).isoformat(),
            datetime(2025, 4, 23, 0, 0).isoformat(),
            datetime(2025, 4, 24, 0, 0).isoformat(),
            datetime(2025, 4, 26, 0, 0).isoformat(),
            datetime(2025, 4, 27, 0, 0).isoformat(),
            datetime(2025, 4, 28, 0, 0).isoformat(),
            datetime(2025, 4, 29, 0, 0).isoformat(),
            datetime(2025, 4, 30, 0, 0).isoformat()
        ])
    ]

    def test_habit_with_completion_dates(self, habit_list, habit_data, habit_name, db_connect):
        """Test adding completion dates to habits."""
        # Find the specific habit data for the given habit_name
        habit_info = next((data for data in habit_data if data[0] == habit_name), None)

        # Check if the habit data exists
        assert habit_info is not None, f"Habit data for '{habit_name}' not found."

        habit_data_name, periodicity, completion_dates = habit_info
        print("Habit Info:", habit_info)

        # Find the habit by name
        habit = next((h for h in habit_list if h.name == habit_data_name), None)

        if habit:
            print(f"Found habit: {habit.name}")  # Debug print to confirm habit found

            # Convert all date strings to datetime objects
            try:
                print("Original completion dates:", completion_dates)
                datetime_dates = [datetime.fromisoformat(date_str) for date_str in completion_dates]
                print("Converted dates:", datetime_dates)  # Debug print to show converted dates
            except ValueError as e:
                print("Error converting dates:", e)
                return  # Exit if there's a conversion error

            habit.completion_dates.clear()
            # Add completion dates directly from habit_data
            habit.add_completion_dates(datetime_dates)  # Pass the list of datetime objects
            print(f"Habit: {habit.name}, Completion Dates: {habit.completion_dates}")  # Should show added dates

        else:
            print(f"Habit '{habit_data_name}' not found in the habit_list.")

        # Print the updated habit list for verification
        print("\nUpdated Habit List:")
        for h in habit_list:
            print(h)

        # Verify and print completion dates for the specific habit
        print(f"\nCompletion Dates for '{habit_data_name}':")
        if habit:
            if habit and habit.completion_dates:
                for date in habit.completion_dates:
                    print(date)
            else:
                print("No completion dates found for this habit.")
        else:
            print(f"Habit '{habit_data_name}' not found, so no completion dates available.")

    @pytest.mark.parametrize("habit_name, expected", [
        ("Medication", 4),  # Expected longest streak for  Medication
        ("Laundry", 4),  # Expected longest streak for  Laundry
        ("Exercise", 9),  # Expected longest streak for Exercise
        ("Make Daily To Do List", 6),  # Expected longest streak for Make Daily To Do List
        ("Study", 13)  # Expected longest streak for Study
    ])
    def test_get_longest_run_streak(self, habit_list, habit_data, habit_name, expected, db_connect):
        """Test getting the longest run streak for habits."""
        # Find the specific habit data for the given habit_name
        habit_info = next((data for data in habit_data if data[0] == habit_name), None)

        # Check if the habit data exists
        assert habit_info is not None, f"Habit data for '{habit_name}' not found."

        # Unpack habit_data
        habit_data_name, periodicity, completion_dates = habit_info
        print("Habit Info:", habit_info)

        # Find the habit by habit_name
        habit = next((h for h in habit_list if h.name == habit_data_name), None)

        # Ensure the habit was found
        assert habit is not None, f"Habit '{habit_data_name}' not found in habit_list."

        # Convert all date strings to datetime objects
        datetime_dates = [datetime.fromisoformat(date_str) for date_str in completion_dates]

        # Add completion dates directly from habit_data
        habit.add_completion_dates(datetime_dates)  # Pass the list of datetime objects

        print(f"Retrieving completion dates for habit: {habit_data_name}")

        # Print all habits and their completion dates for verification
        for h in habit_list:
            print(f"Habit: {h.name}, Completion dates: {h.completion_dates}")

            # Fetch the dates for the habit
        completion_dates = habit.completion_dates

        print(f"Completion dates: {completion_dates}")

        # Get the actual longest streak
        actual_longest_run_streak = habit.get_longest_run_streak()

        # Assert that the actual longest streak matches the expected value
        assert actual_longest_run_streak == expected, (
            f"Expected longest streak for {habit.name} to be {expected}, "
            f"but got {actual_longest_run_streak}."
        )

    def test_get_longest_run_streak_all_habits(self, habit_list, habit_data, habit_name,
                                               db_connect):
        """Test to check the longest run streak across all habits."""
        overall_longest_streak = 0
        habits_with_longest_streak = []

        # Populate habit_list with completion dates from habit_data
        for habit_info in habit_data:
            habit_name, periodicity, completion_dates = habit_info
            # Find the habit in the habit_list
            habit = next((h for h in habit_list if h.name == habit_name), None)
            if habit:
                # Convert completion date strings to datetime objects
                datetime_dates = [datetime.fromisoformat(date_str) for date_str in completion_dates]
                habit.add_completion_dates(sorted(list(set(datetime_dates))))

        # Iterate through all habits to calculate their longest run streaks
        for habit in habit_list:
            # Calculate the longest run streak for the current habit
            current_streak = habit.get_longest_run_streak()

            # Check if the current streak matches the longest streak found so far
            if current_streak > overall_longest_streak:
                overall_longest_streak = current_streak
                habits_with_longest_streak = [habit.name]  # Start a new list with the current habit's name
            elif current_streak == overall_longest_streak:
                habits_with_longest_streak.append(habit.name)  # Add the current habit's name to the list

        print(f"Calculated longest run streak across all habits: {overall_longest_streak}")
        print(f"Habit(s) with the longest streak: {', '.join(habits_with_longest_streak)}")

        # Assert the expected longest streak
        expected_longest_run_streak = 13  # Adjust this based on your expectations
        assert overall_longest_streak == expected_longest_run_streak, (
            f"Expected longest streak to be {expected_longest_run_streak}, "
            f"but got {overall_longest_streak}."
        )

    def test_get_longest_run_streak_by_periodicity(self, habit_list, habit_data, habit_name, periodicity, db_connect):
        """
        Test to check the longest run streak for habits grouped by periodicity.
        """
        # Populate habit_list with completion dates from habit_data
        for habit_info in habit_data:
            habit_name, periodicity, completion_dates = habit_info
            # Find the habit in the habit_list
            habit = next((h for h in habit_list if h.name == habit_name), None)
            if habit:
                # Convert completion date strings to datetime objects
                datetime_dates = [datetime.fromisoformat(date_str) for date_str in completion_dates]
                habit.add_completion_dates(datetime_dates)

        # Group habits by periodicity
        daily_habits = [h for h in habit_list if h.periodicity == "Daily"]
        weekly_habits = [h for h in habit_list if h.periodicity == "Weekly"]

        # Calculate the longest streak for daily habits
        longest_run_daily_streak = 0
        for habit in daily_habits:
            current_streak = habit.get_longest_run_streak()
            if current_streak > longest_run_daily_streak:
                longest_run_daily_streak = current_streak

        # Calculate the longest streak for weekly habits
        longest_run_weekly_streak = 0
        for habit in weekly_habits:
            current_streak = habit.get_longest_run_streak()
            if current_streak > longest_run_weekly_streak:
                longest_run_weekly_streak = current_streak

        # Print results for debugging
        print(f"Longest run streak for daily habits: {longest_run_daily_streak}")
        print(f"Longest run streak for weekly habits: {longest_run_weekly_streak}")

        # Assert the expected longest streaks
        expected_longest_run_daily_streak = 13  # Adjust based on your data
        expected_longest_run_weekly_streak = 4  # Adjust based on your data

        assert longest_run_daily_streak == expected_longest_run_daily_streak, (
            f"Expected longest daily streak to be {expected_longest_run_daily_streak}, "
            f"but got {longest_run_daily_streak}."
        )
        assert longest_run_weekly_streak == expected_longest_run_weekly_streak, (
            f"Expected longest weekly streak to be {expected_longest_run_weekly_streak}, "
            f"but got {longest_run_weekly_streak}."
        )

    def test_edit_habit_name_only(self, db_connect, habit_name):
        """Test editing only the habit name."""
        habit_name = "Exercise"
        new_name = "Swimming"

        # Edit the habit name
        edit_habit(db_connect, habit_name, new_name=new_name)

        # Verify the name was updated
        updated_habit = get_habit(db_connect, new_name)
        assert updated_habit is not None, "Habit name should be updated"

        # Ensure that updated_habit is a tuple with two values
        assert isinstance(updated_habit, tuple), "Expected updated_habit to be a tuple"
        assert len(updated_habit) == 2, "Expected updated_habit to have two elements"

        periodicity: object
        name, periodicity = updated_habit  # Unpack the tuple
        assert name == new_name, f"Expected name: {new_name}, got: {name}"
        assert periodicity == "Daily", f"Expected periodicity: Daily, got: {periodicity}"

    def test_edit_habit_periodicity_only(self, db_connect):
        """Test editing only the periodicity."""
        habit_name = "Medication"
        new_periodicity = "Daily"  # Originally "Weekly"

        # Edit the periodicity
        edit_habit(db_connect, habit_name, new_periodicity=new_periodicity)

        # Verify the periodicity was updated
        updated_habit = get_habit(db_connect, habit_name)
        assert updated_habit is not None, "Habit should exist"
        assert updated_habit[1] == new_periodicity, f"Expected periodicity: {new_periodicity}, got: {updated_habit[1]}"

    def test_edit_habit_name_and_periodicity(self, db_connect):
        """Test editing both name and periodicity."""
        habit_name = "Make_Daily_To_Do_List"
        new_name = "Agenda"
        new_periodicity = "Weekly"
        initial_periodicity = "Daily"

        # Cleanup the habit if it already exists
        db_connect.execute("DELETE FROM habit WHERE name = ?", (habit_name,))
        db_connect.commit()

        # Create the test habit if it doesn't exist
        cursor = db_connect.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO habit (name, periodicity) VALUES (?, ?)",
            (habit_name, initial_periodicity)
        )
        db_connect.commit()

        # Verify the habit exists before editing
        habit: object = get_habit(db_connect, habit_name)
        assert habit is not None, f"Test setup failed -  habit '{habit_name}' doesn't exist"

        # Check if the new name already exists in the database
        cursor.execute("SELECT COUNT(*) FROM habit WHERE name = ?", (new_name,))
        name_exists = cursor.fetchone()[0] > 0  # Check if there's a habit with the new name

        # Handle the case where the new name already exists
        if name_exists:
            # If necessary, you can adjust the new_name to avoid conflicts, or raise an error.
            pytest.skip(f"Habit name '{new_name}' already exists. Skipping test.")

        # Edit both name and periodicity
        edit_habit(db_connect, habit_name, new_name=new_name, new_periodicity=new_periodicity)

        # Verify the old name no longer exists
        assert get_habit(db_connect, habit_name) is None, " habit_name should no longer exist"

        # Verify both fields were updated
        updated_habit = get_habit(db_connect, new_name)
        assert updated_habit is not None, "Habit should exist"
        assert updated_habit[0] == new_name, f"Expected name: {new_name}, got: {updated_habit[0]}"

        print(f"Updated periodicity for '{new_name}': {updated_habit[1]}")

        assert updated_habit[1] == new_periodicity, f"Expected periodicity: {new_periodicity}, got: {updated_habit[1]}"

        # Cleanup (optional)
        cursor.execute("DELETE FROM habit WHERE name=?", (new_name,))
        db_connect.commit()

    def test_edit_habit_no_changes(self, db_connect):
        """Test editing with no changes provided (should leave the habit unchanged)."""
        habit_name = "Study"
        original_habit = get_habit(db_connect, habit_name)

        # Edit with no new_name or new_periodicity
        edit_habit(db_connect, habit_name)

        # Verify nothing changed
        unchanged_habit = get_habit(db_connect, habit_name)
        assert unchanged_habit == original_habit, "Habit should remain unchanged"

    def test_edit_nonexistent_habit(self, db_connect):
        """Test editing a habit that doesn't exist (should not modify the database)."""
        non_existent_habit = "NonExistentHabit"
        new_name = "ShouldNotExist"

        # Try to edit a non-existent habit
        edit_habit(db_connect, non_existent_habit, new_name=new_name)

        # Verify no habit was created/modified
        result = get_habit(db_connect, new_name)
        assert result is None, "No habit should be modified or created"

    def test_delete_habit(self, db_connect):
        """Test deleting a habit from the database."""
        habit_name = "Medication"
        tracker_entries = [
            ("Medication", "2025-04-01"),
            ("Medication", "2025-04-08"),
            ("Medication", "2025-04-15"),
            ("Medication", "2025-04-22")
        ]

        # Ensure the habit does not already exist by deleting it before the test
        db_connect.execute("DELETE FROM habit WHERE name=?", (habit_name,))
        db_connect.execute("DELETE FROM tracker WHERE habit_name=?",
                           (habit_name,))  # Clean up any existing related entries
        db_connect.commit()

        # Insert the habit
        db_connect.execute(
            "INSERT INTO habit (name, periodicity) VALUES (?, ?)",
            (habit_name, "Weekly")
        )

        # Insert associated tracker entries
        for habit_name, completion_dates in tracker_entries:
            db_connect.execute(
                "INSERT INTO tracker (habit_name, completion_dates) VALUES (?, ?)",
                (habit_name, completion_dates)
            )

        db_connect.commit()

        # Verify the habit exists
        cur = db_connect.cursor()
        cur.execute("SELECT * FROM habit WHERE name = ?", (habit_name,))
        assert cur.fetchone() is not None, f"The habit '{habit_name}' should exist."

        # Verify tracker entries exist
        cur.execute("SELECT * FROM tracker WHERE habit_name = ?", (habit_name,))
        assert len(cur.fetchall()) == len(tracker_entries), "Tracker entries should exist for this habit."

        # Now delete the habit
        delete_habit(db_connect, habit_name)

        # Verify the habit no longer exists
        cur.execute("SELECT * FROM habit WHERE name = ?", (habit_name,))
        assert cur.fetchone() is None, f"The habit '{habit_name}' should have been deleted."

        # Verify tracker entries are deleted
        cur.execute("SELECT * FROM tracker WHERE habit_name = ?", (habit_name,))
        assert cur.fetchone() is None, "Tracker entries for the habit should also be deleted."


