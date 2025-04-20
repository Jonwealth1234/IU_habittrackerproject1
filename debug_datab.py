from db import get_db, get_completion_dates, get_habit, add_habit, check_database_content

# Connect to the database
db_connect = get_db("main.db")  # Ensure the database name is correct

if db_connect is None:
    print("Failed to connect to the database.")
else:
    habits = check_database_content(db_connect)
    print("Habits in the database:", habits)
    habits = get_habit(db_connect)
    for habit in habits:
        print(f"Habit: {habit[0]}, Periodicity: {habit[1]}")

        # Specify the habit name you want to check
    habit_name = "Study"  # Replace with the actual habit name

    # Get completion dates for the specified habit
    completion_dates = get_completion_dates(db_connect, habit_name)

    # Print the results
    if completion_dates:
        print(f"Completion Dates for '{habit_name}': {completion_dates}")
    else:
        print(f"No completion dates found for habit '{habit_name}'.")

    # Close the database connection
    db_connect.close()



