from db import (add_habit, add_completion_dates, get_habit as db_get_habit,
                get_completion_dates as db_get_completion_dates, edit_habit, delete_habit,
                validate_periodicity,
                get_habits_by_periodicity,
                get_current_habits)
from datetime import datetime, timedelta


def get_longest_run_streak_all_habits(habit_list):
    longest_run_streak = 0
    for habit in habit_list:
        streak = habit.get_longest_run_streak()
        longest_run_streak = max(longest_run_streak, streak)
    return longest_run_streak


def load_habits_from_db(db):
    """
    Load habits from the database and return a list of Habit objects.
    """
    cur = db.cursor()
    cur.execute('SELECT name, periodicity FROM habit')
    habits_data = cur.fetchall()  # Fetch all rows as tuples (name, periodicity)

    # Convert the list of tuples into a list of Habit objects
    current_habits = [Habit(name, periodicity, db) for name, periodicity in habits_data]
    return current_habits


class Habit:
    def __init__(self, name, periodicity, db, completion_dates=None):
        """Habit class, to count events completed

        :param name: name of the habit
        :param periodicity: to determine the time difference
        """
        self.db = db
        self.name = name
        # Validate the periodicity before setting it
        if not self.validate_periodicity(periodicity):
            raise ValueError(f"Invalid periodicity: '{periodicity}'. Expected 'Daily' or 'Weekly'.")
        self.periodicity = periodicity  # e.g., 'Daily', 'Weekly'
        # Make sure each instance has its own list of completion dates
        if completion_dates is None:
            self.completion_dates = []
        else:
            self.completion_dates = [datetime.fromisoformat(date) for date in completion_dates]

        if completion_dates:
            self.add_completion_dates(completion_dates)  # Initialize with provided dates

    def __str__(self):
        return f"{self.name} ({self.periodicity})"

    def __repr__(self):
        return f"Habit(name: {self.name}, periodicity: {self.periodicity}, completion_dates: {self.completion_dates})"

    def add_completion_dates(self, completion_dates):
        """
        Add completion dates for the habit to the database.

        Args:
            completion_dates (list of datetime): The dates to be recorded as completion dates for the habit.
        """

        if not isinstance(completion_dates, list):
            raise ValueError("Completion dates must be provided as a list of datetime objects.")

        for date in completion_dates:
            # Ensure each date is a datetime object
            if not isinstance(date, datetime):
                raise ValueError(f"Each date must be a datetime object. Found: {type(date).__name__}")

        # Extend the completion dates list
        self.completion_dates.extend(completion_dates)

        # Prepare the database cursor
        cur = self.db.cursor()

        # Store existing dates in a set for quick lookup
        existing_dates = set(self.get_completion_dates(self.db, self.name))

        # List to hold newly added dates
        new_dates = []

        for date in completion_dates:
            # Check if the date already exists to avoid duplicates
            if date not in existing_dates:
                # Insert the completion date into the database
                cur.execute("INSERT INTO tracker (habit_name, completion_dates) VALUES (?, ?)",
                            (self.name, date.isoformat()))  # Store date as an ISO format string

                # Add the date to the instance's completion_dates list
                new_dates.append(date)
                existing_dates.add(date)  # Update the set with the newly added date

        # Commit the changes to the database
        self.db.commit()

        # Close the cursor
        cur.close()

    def get_longest_run_streak(self):
        # Return 0 if there are no completion dates
        if not self.completion_dates:
            return 0

        # Convert completion dates from strings to datetime objects
        #try:
            #self.completion_dates = [
                #datetime.fromisoformat(date) for date in self.completion_dates if isinstance(date, str)
            #]
        #except ValueError as e:
            #print(f"Error converting date: {e}")
            #return 0

            # Sort completion dates
        self.completion_dates.sort()

        # Output the completion_dates to debug
        print(f"Completion Dates: {self.completion_dates}")

        # Initialize streak counters
        streak = 1  # Start with 1 since we have at least one date
        longest_run_streak = 1  # At least one date means the streak is at least 1

        # Define the range to check for streaks based on periodicity
        if self.periodicity == "Daily":
            date_diff = timedelta(days=1)
        elif self.periodicity == "Weekly":
            date_diff = timedelta(weeks=1)
        else:
            raise ValueError("Unknown periodicity")

            # Check for streaks
        for i in range(1, len(self.completion_dates)):
            current_date = self.completion_dates[i]
            previous_date = self.completion_dates[i - 1]

            # Check if the current date is a continuation of the streak
            if current_date - previous_date == date_diff:
                streak += 1
            else:
                longest_run_streak = max(longest_run_streak, streak)
                streak = 1  # Reset streak

        # Final check to update longest_run_streak
        longest_run_streak = max(longest_run_streak, streak)
        print(f"Final Streak Calculation: Current Streak = {streak}, Longest run Streak = {longest_run_streak}")

        return longest_run_streak

    @staticmethod
    def get_longest_run_streak_by_periodicity(db, periodicity):
        """
        Calculate the longest run streak for habits grouped by periodicity.

        Args:
            db: The database connection.
            periodicity (str): The periodicity to filter habits by ("Daily" or "Weekly").

        Returns:
            int: The longest run streak for the given periodicity.
        """
        # Get all habits with the specified periodicity
        habits = get_habits_by_periodicity(db, periodicity)

        # Initialize the longest streak
        longest_run_streak = 0

        # Calculate the longest streak for each habit
        for habit in habits:
            habit_instance = Habit(habit[0], habit[1], db)  # Create a Habit instance
            streak = habit_instance.get_longest_run_streak()  # Get the longest streak for this habit
            longest_run_streak = max(longest_run_streak, streak)  # Update the longest streak

        return longest_run_streak

    def update_longest_run_streak(self, db):
        current_streak = self.get_longest_run_streak()

        cur = db.cursor()
        cur.execute("""  
            UPDATE habit  
            SET longest_run_streak = ?  
            WHERE name = ?  
        """, (current_streak, self.name))

        db.commit()  # Commit the changes to the database

    def store(self, db):
        """Store the habit in the database."""
        add_habit(db, [(self.name, self.periodicity)])  # Wrap in a list of tuples
        print(f"Habit '{self.name}' with periodicity '{self.periodicity}' stored in the database.")

    def store_completion_dates(self, completion_dates):
        for current_date in completion_dates:
            add_completion_dates(self.db, self.name, current_date)

        self.db.commit()

    @staticmethod
    def get_habit(db, name):
        return db_get_habit(db, name)  # Call the imported function

    def edit_habit(self, new_name=None, new_periodicity=None):
        """
        Edit the habit's attributes and update the database.
        """
        if new_name:
            self.name = new_name
        if new_periodicity:
            if not self.validate_periodicity(new_periodicity):
                raise ValueError(f"Invalid periodicity: '{new_periodicity}'. Expected 'Daily' or 'Weekly'.")
            self.periodicity = new_periodicity
        # Update the database
        edit_habit(self.db, self.name, new_name, new_periodicity)

    def delete_habit(self):
        delete_habit(self.db, self.name)   # Delete the habit from the database

    @staticmethod
    def get_completion_dates(db, name):
        return db_get_completion_dates(db, name)  # Call the imported function

    @staticmethod
    def get_periodicity(name):
        if name in ["Medication", "Laundry"]:
            return "Weekly"
        else:
            return "Daily"

    @staticmethod
    def validate_periodicity(periodicity):
        return periodicity in ["Daily", "Weekly"]


class Tracker:
    def __init__(self, db, name, periodicity):
        """
        To store and provide non static data in the habits
        """
        self.db = db
        self.name = name
        self.periodicity = periodicity
        self.habit = []

    def add_current_habit(self, habit_names):
        """ Adds a list of habits to the database.

        :param habit_names: List of habit names to be added
        """
        add_habit(self.db, habit_names)

        self.db.commit()

    def get_current_habits(self, habit_load_habits_from_db):
        return load_habits_from_db(self.db)  # Call the imported function

    def get_habits_by_periodicity(self, periodicity):
        return get_habits_by_periodicity(self.db, periodicity)

    def close(self):
        """Close the database connection."""
        self.db.close()

