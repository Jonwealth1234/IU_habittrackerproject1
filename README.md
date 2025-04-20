# My Habit Tracker Application/Project

An application that allows users to create, track and analyse their habits. 
It is a python project that utilizes SQLite storage and command-line
interface (CLI) for interaction

## Features

- **Create Habits**: Add new habits with a name and periodicity (daily or weekly).
- **Get Completion Dates**: Tracks completion dates for each habit.
- **Analyze Habits**:
  - List all currently tracked habits.
  - List habits with the same periodicity.
  - Get the longest run streak for a specific habit.
  - Get the longest run streak across all habits.
  - Get the longest streak by periodicity.
- **Edit Habits**: Modify the name or periodicity of existing habits.
- **Delete Habits**: Remove habits from the tracker.

## Installation

'''shell
pip install -r requirements.txt
'''

## Usage

Start

'''shell
python main.py
'''

and follow the instructions on the screen

## Tests

'''shell
pytest .
'''