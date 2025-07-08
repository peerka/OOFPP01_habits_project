import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta

def get_all_habits(db):
    """
    Function to fetch and list all habits from the database.
    If fails exception is raised.
    :param db: Name of the SQLite database object.
    :return: List of tuple containing habits ID, name and frequency.
    """
    try:
        habits = db.get_habits()
        return [(h[0], h[1], h[2]) for h in habits]
    except Exception as error:
        print(f"[ERROR] Failed to retrieve all habits: {error}")
        return []

def get_habits_by_frequency(db, frequency):
    """
    Fetch and filter habits by frequency.
    :param frequency: frequency to filter habits by.
    :param db: Name of the SQLite database file.
    :return: List of tuple containing habits ID, name and frequency.
    """
    try:
        habits = db.get_habits()
        return [(h[0], h[1]) for h in habits if h[2] == frequency]
    except Exception as error:
        print(f"[ERROR] Failed to retrieve habits by frequency: {error}")
        return []

def get_longest_streak(db):
    """
    Determine the longest streak from the habits.
    :param db: Name of the SQLite database object.
    :return: (habit name, streak length).
    """
    try:
        habits = get_all_habits(db)
        max_streak = 0
        best_habit = None
        for habit_id, name, frequency in habits:
            completions = db.get_completions(habit_id)
            streak = calculate_streak(completions, frequency)
            if streak > max_streak:
                max_streak = streak
                best_habit = name
        return best_habit, max_streak
    except Exception as error:
        print(f"[ERROR] Failed to retrieve longest streak: {error}")
        return None, 0


def get_habit_streak(db, habit_id, frequency): # In use again
    """
    Fetch completions and calculate streak for summaries.
    Try fetch completion and calculate streak, if failed exception will be raised.
    :param habit_id: Name of the habit.
    :param frequency: frequency to fetch streak.
    :param db: Name of the SQLite database file.
    :return: The current streak count of specified habit.
    """
    try:
        completions = db.get_completions(habit_id)
        if not completions:
            print(f"Habit ID {habit_id} not found or no completions!")
            return 0
        return calculate_streak(completions, frequency)
    except Exception as error:
        print(f"[ERROR] Failed to retrieve streak for habit '{habit_id}': {error}")
        return 0

def calculate_streak(completions, frequency):
    """
    Calculate streak in periods for a habit on it's completions
    :param completions: List of datetime strings (YYYY-MM-DD HH:MM:SS)
    :param frequency: Frequency of habit in 'daily', 'weekly', 'monthly', 'yearly'.
    :return: Streak count (1 if completed, 0 otherwise).
    """
    if not completions:
        return 0
    dates = sorted(datetime.strptime(c, "%Y-%m-%d %H:%M:%S").date() for c in completions)
    periods = []
    streak = 0
    today = datetime.now().date()


    #periods keys (daily, weekly, monthly, yearly)
    if frequency == 'daily':
        #Calculate streak ending at yesterday or today, depending on whether today has a completion
        #Start at today if today has completion, else yesterday
        last_period = today
        if today not in dates:
            last_period = today - timedelta(days=1)
        #Walk backward as long as completions for each previous day
        current = last_period
        dates_set = set(dates)
        while current in dates_set:
            streak += 1
            current -= timedelta(days=1)
    elif frequency == 'weekly':
        #Same idea, but with weeks (using ISO year/week)
        this_week = today - timedelta(days=today.weekday())  #Start of this week (Monday)
        weeks = set(d - timedelta(days=d.weekday()) for d in dates)
        last_period = this_week
        if this_week not in weeks:
            last_period = this_week - timedelta(weeks=1)
        current = last_period
        while current in weeks:
            streak += 1
            current -= timedelta(weeks=1)
    elif frequency == 'monthly':
        months = set((d.year, d.month) for d in dates)
        current_month = (today.year, today.month)
        last_period = current_month if (today.year, today.month) in months else (
            today.year if today.month > 1 else today.year - 1,
            today.month - 1 if today.month > 1 else 12
        )
        y, m = last_period
        def prev_month(y, m):
            return (y-1, 12) if m == 1 else (y, m-1)
        while (y, m) in months:
            streak += 1
            y, m = prev_month(y, m)
    elif frequency == 'yearly':
        years = set(d.year for d in dates)
        current_year = today.year
        last_period = current_year if current_year in years else current_year - 1
        y = last_period
        while y in years:
            streak += 1
            y -= 1
    return streak

def plot_habits_completion(db):
    """
    Plot habits completion and streak count of each habit as barchart .
    If no data message will be printed.
    If plot fails to generate exception will be raised.
    :param db: Name of the SQLite database file.
    :return: None.
    """
    try:
        habits = get_all_habits(db)
        names = []
        completions_counts = []
        streak_counts = []
        for habit_id, name, frequency in habits:
            completions = db.get_completions(habit_id)
            completions_counts.append(len(completions))
            streak_counts.append(calculate_streak(completions, frequency))
            names.append(name)

        if not any(completions_counts):
            print("No habits data is available.")
            return

        x = np.arange(len(names))
        width = 0.3

        fig, ax = plt.subplots(figsize=(10, 5))
        rects1 = ax.bar(x - width/2, completions_counts, width, label='Completions', color='red')
        rects2 = ax.bar(x + width/2, streak_counts, width, label='Streak', color='skyblue')

        ax.set_xlabel("Habits")
        ax.set_ylabel("Completed count")
        ax.set_title("Habits Completion vs current streak")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45)
        ax.legend()
        fig.tight_layout()
        plt.show()
    except Exception as error:
        print(f"[ERROR] Failed to generate plot: {error}")

def get_completion_count(db, habit_id):
    """
    Return total number of completions for a habit.
    """
    try:
        return len(db.get_completions(habit_id))
    except Exception as error:
        print(f"[ERROR] Failed to count completions: {error}")
        return 0