from db import get_db, get_habit_data, get_habits_by_periodicity, get_completion_dates
from habit import Habit
import sqlite3


def analyse_habit_data(db_con, habit):
    """
    Analyze the events in the habit.

    :param db_con: an initialized sqlite3 database connection
    :param habit: name of the habit present in the DB
    :return: length of data in the habit, longest streak, or names of habits depending on conditions
    """
    data = get_habit_data(db_con, habit)
    return len(data)


def get_current_habits(db_con):
    # Ensure db is a valid SQLite connection
    if not isinstance(db_con, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection object")

    try:
        # Fetch current habits from the database
        cur = db_con.cursor()
        cur.execute("SELECT name, periodicity FROM habit")  # Fetch habit names and periodicity
        habits_data = cur.fetchall()

        # Convert the fetched data into a list of habits
        current_habits = []
        for name, periodicity in habits_data:
            # Fetch completion dates for the habit
            completion_dates = get_completion_dates(db_con, name)

            # Assuming you have a Habit class to represent habits
            habit = Habit(name, periodicity, db_con)
            habit.completion_dates = completion_dates  # Attach completion dates to the habit
            current_habits.append(habit)

        # Analyze the habits
        analyze_habits(current_habits)

        return current_habits  # Return the list of habits

    except Exception as e:
        print(f"An error occurred: {e}")
        return []  # Return an empty list in case of error


def analyze_habit_streak(db_con, habit):
    """
    Analyze and print the longest streak for a specific habit.

    :param db_con: An initialized sqlite3 database connection
    :param habit: The name of the habit to analyze
    """
    completion_dates, periodicity = get_habit_data(db_con, habit)

    if completion_dates:
        if periodicity == 'daily':
            streak = Habit.get_longest_run_streak(completion_dates)
            print(f"The longest run streak for habit {habit} ('{periodicity}') is: {streak} day(s)")
        elif periodicity == 'weekly':
            streak = Habit.get_longest_run_streak(completion_dates)
            print(f"The longest run streak for habit {habit} ('{periodicity}') is: {streak} week(s)")
    else:
        print(f"No completion records found for habit  {habit}.")


def analyze_habits(habits):
    print("Current Habits:")
    for habit in habits:
        print(f"- {habit}")

    print(f"Total number of habits: {len(habits)}")


def analyze_habits_by_periodicity(db_con, periodicity):
    """
    Analyze and print habits based on their periodicity.

    :param db_con: Initialize SQLite database connection (path)
    :param periodicity: The periodicity to filter habits
    """

    # Ensure db is a valid SQLite connection
    if not isinstance(db_con, sqlite3.Connection):
        raise TypeError("Expected db_con to be sqlite3.Connection object")

        # Call the function to get habits by periodicity
    habits = get_habits_by_periodicity(db_con, periodicity)

    # Print the results
    print(f"Habits with periodicity {periodicity}:")
    for habit in habits:
        print(f"- {habit}")

    # Close the database connection
    db_con.close()


def get_longest_run_streak(data):
    """
    Get the longest run streak in all habits.
    :param data:  list of habit objects
    :return: the longest streak in all habits
    """
    if not all(isinstance(habit, Habit) for habit in data):
        raise ValueError("All items in data must be Habit objects.")
    return max((habit.get_longest_run_streak() for habit in data), default=0)


def get_longest_run_streak_all_habits(db_con):
    # Retrieve all habits from the database
    current_habits = get_current_habits(db_con)  # Ensure this function is defined to fetch habits

    if not current_habits:
        return 0  # Return 0 if no habits are found

    # Calculate the longest run streak for each habit
    longest_streaks = [habit.get_longest_run_streak() for habit in current_habits]

    # Return the maximum streak found
    return max(longest_streaks, default=0)  # Use default=0 to handle empty list
