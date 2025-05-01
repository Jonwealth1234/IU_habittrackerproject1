import sqlite3
from datetime import datetime


def get_db(name: str = "main.db") -> sqlite3.Connection:
    db_connect = sqlite3.connect(name)
    create_tables(db_connect)
    add_longest_run_streak_column(db_connect)
    delete_invalid_habits(db_connect)   # Delete invalid habits when the database is initialized
    fix_null_periodicity(db_connect)
    habit_data = [
        ("Medication", "Weekly"),
        ("Laundry", "Weekly"),
        ("Exercise", "Daily"),
        ("Make Daily To Do List", "Daily"),
        ("Study", "Daily")
    ]
    update_default_periodicity(db_connect, habit_data)
    return db_connect


def create_tables(db_connect):
    cur = db_connect.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS habit(    
      name TEXT PRIMARY KEY,
      periodicity TEXT
      longest_run_streak INTEGER DEFAULT 0)""")
    db_connect.commit()

    cur.execute("""CREATE TABLE IF NOT EXISTS tracker(
    
      completion_dates TEXT,
      habit_name TEXT,
      FOREIGN KEY(habit_name)REFERENCES habit(name))""")
    db_connect.commit()


def add_longest_run_streak_column(db_connect):
    """
    Add the longest_run_streak column to the habit table if it doesn't exist.

    :param db_connect: Database connection object.
    """

    cur = db_connect.cursor()

    # Check if the longest_run_streak column exists
    cur.execute("PRAGMA table_info(habit)")
    columns = cur.fetchall()
    column_names = [column[1] for column in columns]

    if "longest_run_streak" not in column_names:
        # Add the longest_run_streak column
        cur.execute("ALTER TABLE habit ADD COLUMN longest_run_streak INTEGER DEFAULT 0")

        # Comment out the statement
        # print("Added longest_run_streak column to the habit table.")
    else:
        # Comment out the statement
        # print("longest_run_streak column already exists in the habit table.")

        db_connect.commit()


def update_default_periodicity(db_connect, habit_data):
    """
    Update the periodicity of habits that have the default "Daily" periodicity.

    :param db_connect: Database connection object
    :param habit_data: List of tuples with habit name and new periodicity.
                       Each tuple should be (habit_name, periodicity).
    """

    cur = db_connect.cursor()

    for habit_name, new_periodicity in habit_data:
        # Check if the habit exists and has the default "Daily" periodicity
        cur.execute('SELECT periodicity FROM habit WHERE name = ?', (habit_name,))
        result = cur.fetchone()

        if result and result[0] == "Daily":
            # Update the periodicity
            cur.execute('UPDATE habit SET periodicity = ? WHERE name = ?', (new_periodicity, habit_name))
            # Comment out the print statement
            # print(f"Updated periodicity for '{habit_name}' to '{new_periodicity}'.")
        else:
            # Comment out the print statement
            # print(f"Skipping '{habit_name}': No default 'Daily' periodicity found.")

            db_connect.commit()


def add_habit(db_connect, habit_data):
    """
    Insert a list of habits into the database, optionally with their periodicity.

    :param db_connect: Database connection object
    :param habit_data: List of tuples or strings with habit data.
                       - If a list of tuples, each tuple should be (habit_name, periodicity).
                       - If a list of strings, each string should be a habit_name with no periodicity.
    """

    cur = db_connect.cursor()

    # Prevent adding 'Daily' or 'Weekly' as habit names
    for habit in habit_data:
        if isinstance(habit, tuple):
            habit_name = habit[0]
        else:
            habit_name = habit

        if habit_name in ['Daily', 'Weekly']:
            raise ValueError(f"Habit names cannot be '{habit_name}'.")

    # Process each habit
    for habit in habit_data:
        if isinstance(habit, tuple):
            habit_name, periodicity = habit
        else:
            habit_name = habit
            # Look up existing periodicity for the habit (if it exists)
            cur.execute('SELECT periodicity FROM habit WHERE name = ?', (habit_name,))
            result = cur.fetchone()
            if result:
                periodicity = result[0]  # Use existing periodicity
            else:
                raise ValueError(f"Periodicity must be provided for new habit: {habit_name}")

        # Insert the habit with its periodicity
        cur.execute('INSERT OR REPLACE INTO habit (name, periodicity) VALUES (?, ?)', (habit_name, periodicity))

    db_connect.commit()


def add_habit_with_periodicity(db_connect, habit_data):
    """
    Insert a list of habits with periodicity into the database, avoiding duplicates.

    :param db_connect: Database connection object
    :param habit_data: List of tuples with habit name and periodicity.
    """
    cur = db_connect.cursor()
    for habit_name, periodicity in habit_data:
        if habit_name in ['Daily', 'Weekly']:
            raise ValueError(f"Habit names cannot be '{habit_name}'.")
        if not periodicity:
            raise ValueError(f"Periodicity cannot be None for habit '{habit_name}'.")
        cur.execute('INSERT OR IGNORE INTO habit (name, periodicity) VALUES (?, ?)', (habit_name, periodicity))
    db_connect.commit()


def fix_null_periodicity(db_connect):
    """
    Set a default periodicity ('Daily') for habits where periodicity is NULL.

    :param db_connect: Database connection object.
    """

    cur = db_connect.cursor()
    cur.execute("UPDATE habit SET periodicity = 'Daily' WHERE periodicity IS NULL")
    db_connect.commit()
    #  print("Fixed NULL periodicity values in the database.")  # This line is commented out


def get_habit(db_connect, habit_name):
    cur = db_connect.cursor()
    cur.execute("SELECT name, periodicity FROM habit WHERE name=?", (habit_name,))
    return cur.fetchone()


def add_completion_dates(db_connect, name, completion_dates):
    # Ensure db is a valid SQLite connection
    if not isinstance(db_connect, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection object")

    # Normalize the completion_dates to a list if it's a single datetime object
    if isinstance(completion_dates, datetime):
        completion_dates = [completion_dates]

    # Create a cursor object
    cur = db_connect.cursor()

    # Check for existing completion dates for the specified habit
    cur.execute("SELECT completion_dates FROM tracker WHERE habit_name = ?", (name,))
    existing_dates_row = cur.fetchone()  # Fetch existing completion dates

    # Convert existing dates to a set of date objects for comparison
    if existing_dates_row and existing_dates_row[0]:
        existing_dates = set(existing_dates_row[0].split(','))
    else:
        existing_dates = set()

    # Initialize a list to hold new dates to insert
    new_dates = []

    # Check for duplicates and prepare new dates for insertion
    for date in completion_dates:
        normalized_date = date.date()  # Normalize to date only
        if normalized_date not in existing_dates:
            new_dates.append(date.isoformat())
            print(f"Added completion date for '{name}': {normalized_date.isoformat()}")
        else:
            print(f"Duplicate date: {normalized_date.isoformat()} already exists for habit '{name}'.")

    if new_dates:
        # Combine existing and new dates
        all_dates = existing_dates.union(new_dates)  # Combine sets to avoid duplicates
        updated_dates = ','.join(sorted(all_dates))  # Sort and join dates

        # Insert or update the completion_dates in the database
        if existing_dates_row:

            # Update the completion_dates in the database
            cur.execute("UPDATE tracker SET completion_dates = ? WHERE habit_name = ?",
                        (updated_dates, name))
        else:
            # Insert a new row
            cur.execute("INSERT INTO tracker (completion_dates, habit_name) VALUES (?, ?)",
                        (updated_dates, name))
    else:
        print(f"No new dates to add for habit '{name}'.")

    db_connect.commit()

    # Close the cursor
    cur.close()


def check_database_content(db_connect):
    """Checks and returns the current habits in the database."""
    cursor = db_connect.cursor()
    cursor.execute("SELECT name FROM habit")
    rows = cursor.fetchall()

    # Create a list of habits from the fetched rows
    habits = [row[0] for row in rows]

    # Print the habits for debugging purposes
    print("Current habits in the database:", habits)

    # Return the list of habits
    return habits


def delete_invalid_habits(db_connect):
    """
    Delete rows from the habit table where the name is 'Daily' or 'Weekly'.

    :param db_connect: Database connection object.
    """
    cur = db_connect.cursor()

    # Delete rows where the name is 'Daily' or 'Weekly'
    cur.execute("DELETE FROM habit WHERE name IN ('Daily', 'Weekly')")

    # Commit the changes
    db_connect.commit()
    # Comment out the print statement
    # print("Invalid habits 'Daily' and 'Weekly' have been deleted.")


def input_data_database(db_connect):
    """Populate the database with completion dates."""

    habit_info = [
        ("Medication", "Weekly", [datetime(2025, 4, d, 0, 0) for d in [1, 8, 15, 22]]),
        ("Laundry", "Weekly", [datetime(2025, 4, d, 0, 0) for d in [3, 10, 17, 24]]),
        ("Exercise", "Daily", [datetime(2025, 4, d, 0, 0) for d in range(2, 31) if d not in
                               [4, 5, 9, 19, 22]]),
        ("Make Daily To Do List", "Daily",
         [datetime(2025, 4, d, 0, 0) for d in range(2, 31) if d not in
          [1, 3, 8, 15, 16, 20, 24, 27]]),
        ("Study", "Daily", [datetime(2025, 4, d, 0, 0) for d in range(1, 31) if d not in
                            [6, 11, 25]])
    ]
    for name, periodicity, dates in habit_info:
        add_habit(db_connect, [(name, periodicity)])
        add_completion_dates(db_connect, name, dates)


def get_habits_by_periodicity(db_connect, periodicity):
    """
    Retrieve habit names from the database based on the specified periodicity.

    :param db_connect: an initialized sqlite3 database connection
    :param periodicity: the periodicity of the habits to retrieve
    :return: a list of habit names with the specified periodicity
    """
    # Ensure db is a valid SQLite connection
    if not isinstance(db_connect, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection object")

    # Prepare and execute the SQL query to get habits by periodicity
    cur = db_connect.cursor()
    cur.execute("SELECT name FROM habit WHERE periodicity = ?", (periodicity,))

    # Fetch all the rows in the result
    rows = cur.fetchall()

    # Extract habit names from the rows
    habit_names = [row[0] for row in rows]

    # Close the cursor
    cur.close()

    return habit_names


def validate_periodicity(periodicity):
    valid_periodicity = ["Weekly", "Daily"]  # List of valid periodicity

    # Check if the periodicity is not valid
    if periodicity not in valid_periodicity:
        raise ValueError(f"Invalid periodicity '{periodicity}'. Use one of {valid_periodicity}.")

    # Print confirmation message if the periodicity is valid
    print(f"Periodicity '{periodicity}' is valid.")
    return True  # Optionally return True to indicate valid periodicity


def get_habit_periodicity(db_connect, habit_name):
    cur = db_connect.cursor()
    cur.execute("SELECT periodicity FROM habit WHERE name = ?", (habit_name,))
    result = cur.fetchone()
    return result[0] if result else None


def get_current_habits(db_connect):
    """
    Fetch the current habits from the database as a list of Habit objects.

    :param db_connect: The database connection object.
    :return: A list of Habit objects.
    """
    # Ensure db_connect is a valid SQLite connection
    if not isinstance(db_connect, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection object")

    cur = db_connect.cursor()

    # Execute the query to select habit names and periodicity from the 'habit' table
    cur.execute("SELECT name, periodicity FROM habit")

    # Fetch all rows as tuples (name, periodicity)
    habits_data = cur.fetchall()

    # Filter out invalid habit names
    invalid_habit_names = ["Daily", "Weekly"]
    valid_habits_data = [
        (name, periodicity) for name, periodicity in habits_data
        if name not in invalid_habit_names
    ]

    # Import Habit class locally
    from habit import Habit

    # Convert the list of tuples into a list of Habit objects with completion dates
    current_habits = []
    for name, periodicity in valid_habits_data:
        # Retrieve completion dates for the habit
        completion_dates = get_completion_dates(db_connect, name)
        if completion_dates is not None:
            # Create a Habit object with the retrieved data
            habit = Habit(name, periodicity, db_connect)
            habit.completion_dates = completion_dates
            current_habits.append(habit)

    return current_habits


def edit_habit(db_connect, name, new_name=None, new_periodicity=None):
    """
    Edit an existing habit in the database.
    """
    cur = db_connect.cursor()
    if new_periodicity:
        cur.execute("UPDATE habit SET periodicity = ? WHERE name = ?", (new_periodicity, name))
    if new_name:
        cur.execute("UPDATE habit SET name = ? WHERE name = ?", (new_name, name))
    db_connect.commit()
    cur.close()


def delete_habit(db_connect, name):
    """
    Delete a habit from the database.
    """
    cur = db_connect.cursor()
    cur.execute("DELETE FROM habit WHERE name = ?", (name,))
    cur.execute("DELETE FROM tracker WHERE habit_name = ?", (name,))  # Delete associated completion dates
    db_connect.commit()
    cur.close()


def get_completion_dates(db_connect, name):
    """
    Retrieve completion dates for a specific habit from the database and convert them to datetime objects.

    Args:
        db_connect (sqlite3.Connection): The database connection.
        name (str): The name of the habit.

    Returns:
        list: A list of completion dates as datetime objects.
    """
    # Ensure db is a valid SQLite connection
    if not isinstance(db_connect, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection object")

    cur = db_connect.cursor()

    # Execute the query to fetch completion dates for the specified habit
    cur.execute("SELECT completion_dates FROM tracker WHERE habit_name = ?", (name,))

    # Fetch all results
    rows = cur.fetchall()  # Fetch all rows

    # Close the cursor
    cur.close()

    # If no rows are found, return an empty list
    if not rows:
        return []

    # Initialize a list to hold all completion dates
    completion_dates = []

    # Iterate through the rows and split the completion dates
    for row in rows:
        if row[0] is not None:  # Check if the completion_dates is not None
            # Split the completion dates string into individual date strings
            date_strings = row[0].split(',')

            # Convert each date string to a datetime object
            for date_str in date_strings:
                try:
                    # Convert the ISO formatted string to a datetime object
                    date_obj = datetime.fromisoformat(date_str.strip())  # Use strip() to remove any extra spaces
                    completion_dates.append(date_obj)
                except ValueError as e:
                    print(f"Error converting date string '{date_str}' to datetime object: {e}")

    return completion_dates  # Return the list of completion dates as datetime objects


def get_habit_data(db_connect, habit):
    """
    Retrieve the habit data from the specified database.

    :param db_connect: an initialized sqlite3 database connection
    :param habit: name of the habit to retrieve data for
    :return: a list of completion dates and periodicity for the specified habit
    """
    # Ensure db is a valid SQLite connection
    if not isinstance(db_connect, sqlite3.Connection):
        raise TypeError("Expected a sqlite3.Connection object")

    cur = db_connect.cursor()

    # Get the periodicity for the habit
    cur.execute("SELECT periodicity FROM tracker WHERE habit_name = ?", (habit,))
    periodicity_row = cur.fetchone()
    periodicity = periodicity_row[0] if periodicity_row else None

    # Prepare and execute the SQL query to get data for the specified habit

    cur.execute("SELECT completion_dates FROM tracker WHERE habit_name = ?", (habit,))

    # Fetch all the rows in the result
    rows = cur.fetchall()

    # Extract dates from the rows
    completion_dates = [row[0] for row in rows]

    # Close the cursor
    cur.close()

    return completion_dates, periodicity


def commit():
    return None


def close():
    return None
