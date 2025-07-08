import os
import warnings
import pytest
import sqlite3
import matplotlib
from datetime import datetime, timedelta
from habit_tracker.database import Database, Habit
from habit_tracker.analysis import(
    get_all_habits,
    get_habits_by_frequency,
    get_habit_streak,
    get_longest_streak,
    plot_habits_completion,
    calculate_streak
)


TEST_DB = "test_habits.db"

@pytest.fixture
def setup_test_data():
    db = Database(TEST_DB)
    db.cursor.execute("DELETE FROM habits")
    db.cursor.execute("DELETE FROM completions")

    #create and complete habits
    habit = Habit(db)
    habit.create("Exercise", "daily")
    habit.create("Read", "weekly")
    habit.create("Meditate", "daily")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.cursor.execute("INSERT INTO completions (habit_id, completed_at) VALUES (1, ?)",
                      (now,))
    db.cursor.execute("INSERT INTO completions (habit_id, completed_at) VALUES (3, ?)",
                      (now,))
    db.conn.commit()

    yield db
    db.close()
    os.remove(TEST_DB)

#Test get_all_habits, fetch 3 habits.
def test_get_all_habits(setup_test_data):
    db = setup_test_data
    habits = get_all_habits(db)
    assert len(habits) == 3

#Test get_habits_by_frequency.
def test_get_habits_by_frequency(setup_test_data):
    db = setup_test_data
    habits = get_habits_by_frequency(db, "daily")
    assert len(habits) == 2

#Test get_habit_streak, habit id 1 has been marked as completed.
def test_get_habits_streak(setup_test_data):
    db = setup_test_data
    streak = get_habit_streak(db,1, "daily")
    assert isinstance(streak, int)
    assert streak >= 1

#Test get_longest_streak, habit 1 and 3 has a streak.
def test_get_longest_streak(setup_test_data):
    db = setup_test_data
    habit, streak = get_longest_streak(db)
    assert habit in ["Exercise", "Meditate"]
    assert isinstance(streak, int)

#Test plot_habit_completion, try call plot_habit_completions if fails raise an exception.
def test_plot_habit_completion(setup_test_data):
    db = setup_test_data
    matplotlib.use("Agg")   #Disable GUI backend for testing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            plot_habits_completion(db)
        except Exception as e:
            pytest.fail(f"plot_habits_completion raised an exception: {e}")


def format_date(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

#Test daily calculated streak all completed.
def test_calculate_streak_daily():
    today = datetime.now().date()
    dates = [
        format_date(datetime.combine(today - timedelta (days=2), datetime.min.time())),
        format_date(datetime.combine(today - timedelta(days=1), datetime.min.time())),
        format_date(datetime.combine(today, datetime.min.time())),
    ]
    assert calculate_streak(dates, "daily") == 3

#Test daily calculated streak with broken streak.
def test_calculate_streak_daily_with_gap():
    today = datetime.now().date()
    dates = [
        format_date(datetime.combine(today - timedelta(days=3), datetime.min.time())),
        format_date(datetime.combine(today - timedelta(days=1), datetime.min.time())),
        format_date(datetime.combine(today, datetime.min.time())),
    ]
    assert calculate_streak(dates, "daily") == 2  # gap broke the streak before

#Test weekly calculated streak for 3 consecutive weeks.
def test_calculate_streak_weekly():
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)
    dates = [
        format_date(datetime.combine(two_weeks_ago, datetime.min.time())),
        format_date(datetime.combine(last_week, datetime.min.time())),
        format_date(datetime.combine(today, datetime.min.time())),
    ]
    assert calculate_streak(dates, "weekly") == 3

#Test monthly calculated streak for 3 consecutive monthly.
def test_calculate_streak_monthly():
    today = datetime.now()
    dates = [
        format_date(datetime(today.year, today.month, 1)),
        format_date(datetime(today.year, today.month - 1, 1)),
        format_date(datetime(today.year, today.month - 2, 1)),
    ]
    assert calculate_streak(dates, "monthly") == 3

#Test yearly calculated streak for 3 consecutive yearly.
def test_calculate_streak_yearly():
    this_year = datetime.now().year
    dates = [
        format_date(datetime(this_year - 2, 1, 1)),
        format_date(datetime(this_year - 1, 1, 1)),
        format_date(datetime(this_year, 1, 1)),
    ]
    assert calculate_streak(dates, "yearly") == 3

#Test calculated streak for daily if empty
def test_calculate_streak_empty():
    assert calculate_streak([], "daily") == 0

#Test invalid value for calculated streak
def test_calculate_streak_invalid_frequency():
    now = format_date(datetime.now())
    assert calculate_streak([now], "hourly") == 0
