import os
import pytest

from habit_tracker.database import Database, Habit, ExampleData

TEST_DB = "test_habits.db"

@pytest.fixture
def db():
    db = Database(db_name=TEST_DB)

    #Clean both tables for consisting tests
    db.cursor.execute("DELETE FROM habits")
    db.cursor.execute("DELETE FROM completions")
    db.conn.commit()
    yield db
    db.close()
    os.remove(TEST_DB)

#Test add_habit method, adds a habit with frequency daily.
def test_add_habit(db):
    db.add_habit("Test Habit", "daily")
    habits = db.get_habits()
    assert len(habits) == 1
    assert habits[0][1] == "Test Habit"
    assert habits[0][2] == "daily"

#Test delete_habit from database.
def test_delete_habits(db):
    db.add_habit("Delete Habit", "weekly")
    habit_id = db.get_habits()[0][0]
    db.delete_habit(habit_id)
    assert db.get_habits() == []

#Test mark_habit_complete, mark a habit as complete in database.
def test_mark_habit_complete(db):
    db.add_habit("Mark complete", "monthly")
    habit_id = db.get_habits()[0][0]
    db.mark_habit_completed(habit_id)
    updated = db.get_habits()[0][4]
    assert updated is not None

#Test completions logg, verifies mark complete also population completions
def test_completion_logg_in_table(db):
    db.add_habit("Completion Log", "daily")
    habit_id = db.get_habits()[0][0]
    db.mark_habit_completed(habit_id)

    completions = db.cursor.execute("SELECT * FROM completions WHERE habit_id = ?",
                                    (habit_id,)).fetchall()
    assert len(completions) == 1

#Testing activating example data adds 5 habits
def test_example_data_activation(db):
    example = ExampleData(db)
    example.activate()

    habits = db.get_habits()
    assert len(habits) == 5
    names = [h[1] for h in habits]
    assert "Morning walk" in names
    assert "Weekly reflection" in names
    assert "Annual goal review" in names

#Test completions added with example data
def test_example_data_completions(db):
    example = ExampleData(db)
    example.activate()
    habits = db.get_habits()
    for habit in habits:
        completions = db.get_completions(habit[0])
        name = habit[1]
        if name == "Morning Walk":
            assert len(completions) == 28
        elif name == "Weekly reflection":
            assert len(completions) == 4
        elif name == "Annual goal review":
            assert len(completions) == 0
        elif name == "Budget review":
            assert len(completions) == 1
        elif name == "Read a book":
            assert len(completions) == 14

#Testing deactivation of the example data
def test_example_data_deactivation(db):
    example = ExampleData(db)
    example.activate()
    example.deactivate()
    habits = db.get_habits()
    names = [h[1] for h in habits]
    assert "Morning Walk" not in names
    assert "Weekly reflection" not in names
