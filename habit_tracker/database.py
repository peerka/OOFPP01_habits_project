import sqlite3
import datetime


class Database:
    """Database class using sqlite3"""

    def __init__(self, db_name="habits.db"):
        """
        Initialize the database connection.

        :param db_name: name of the SQLite database.
        """
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """
        Create required table for habits if not exists.
        """
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                frequency TEXT CHECK(frequency IN ('daily', 'weekly', 'monthly', 'yearly'))NOT NULL,
                                created_at TEXT NOT NULL,
                                last_completed TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS completions (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               habit_id INTEGER NOT NULL,
                               completed_at TEXT NOT NULL,
                               FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE)''')
        self.conn.commit()

    def add_habit(self, name, frequency):
        """
        Adds a new habit to the database.
        If fails to add habit to database, an exception is raised.
        :param name: Name of the habit.
        :param frequency: Frequency of the habit (daily, monthly, weekly, yearly).
        """
        try:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("INSERT INTO habits (name, frequency, created_at) values (?, ?, ?)",
                            (name, frequency, created_at))
            self.conn.commit()
        except sqlite3.Error as error:
            print(f"[ERROR] Failed to add habit {name} to database: {error}")

    def add_habit_with_completions(self, name, frequency, created_at, completions):
        """
        Inserts habits from example data and set last_completed as the last completion.
        :param name: Name of the habit.
        :param frequency: Frequency of the habit (daily, weekly, monthly, yearly).
        :param created_at: Habit creation date.
        :param completions: Frequency of completion habits.
        """
        last_completed = max(completions) if completions else None
        self.cursor.execute(
            "INSERT INTO habits (name, frequency, created_at, last_completed) values (?, ?, ?, ?)",
            (name, frequency, created_at, last_completed)
        )
        self.conn.commit()

    def add_completions(self, habit_id, completions):
        """
        Inserts multiple completion records for given habit id.
        :param habit_id: ID of the habit.
        :param completions: List of completion timestamps
        """
        for completed_at in completions:
            self.cursor.execute(
                "INSERT INTO completions (habit_id, completed_at) values (?, ?)",
                (habit_id, completed_at)
            )
        self.conn.commit()

    def get_completions(self, habit_id):
        """
        Fetches all completions timestamps for given habit id, sorted by date.
        :param habit_id: id of the habit to fetch
        :return: List of completion timestamps
        """
        self.cursor.execute("SELECT completed_at FROM completions WHERE habit_id = ? ORDER BY completed_at ASC",
                            (habit_id,)

        )
        return [row[0] for row in self.cursor.fetchall()]

    def get_habits(self):
        """
        Fetch all habits. Remember put in try exception
        :return: habits.
        """
        self.cursor.execute("SELECT * FROM habits")
        return self.cursor.fetchall()

    def delete_habit(self, habit_id):
        """
        Delete a habit from the database.
        If ID is not found warning will be printed, if delete fails exception is raised.
        :param habit_id: ID of the habit to delete.
        """
        try:
            self.cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            if self.cursor.rowcount == 0:
                print(f"[WARNING] Failed to find habit with ID {habit_id}.")
            else:
                print(f"Habit ID {habit_id} deleted")
                self.conn.commit()
        except sqlite3.Error as error:
            print(f"[ERROR] Failed to delete habit {habit_id}: {error}")


    def mark_habit_completed(self, habit_id):
        """
        Marking the habit completed in the database with timestamp.
        Preventing duplicate completion records on same period.
        If ID is not found a warning will be printed, if mark fails exception is raised.
        :param habit_id: ID of the habit to mark.
        """
        try:
            completed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            today = datetime.datetime.now().date()
            self.cursor.execute("SELECT completed_at FROM completions WHERE habit_id = ?", (habit_id,))
            completions = [datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").date() for row in self.cursor.fetchall()]
            if today in completions:
                print("[INFO] Habit has already been completed for today")
                return False

            self.cursor.execute("INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",(habit_id, completed_at))
            self.cursor.execute("UPDATE habits SET last_completed = ? WHERE id = ?", (completed_at, habit_id))
            if self.cursor.rowcount == 0:
                print(f"[WARNING] Failed to find habit with ID {habit_id}.")
            else:
                self.conn.commit()
            return True
        except sqlite3.Error as error:
            print(f"[ERROR] Failed to mark habit {habit_id}: {error}")
            return False


    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

class Habit:
    """Habit class for habit management actions using database instance"""
    def __init__(self, db):
        """
        Initialize the database instance.
        :param db: Database instance.
        """
        self.db = db

    def create(self, name, frequency):
        """
        Create a new habit to store in database.
        :param name: Name of the habit.
        :param frequency: Frequency of the habit (daily, weekly, monthly, yearly).
        """
        self.db.add_habit(name, frequency)
        print(f"Habit '{name}' added with frequency {frequency}")

    def delete(self, habit_id):
        """
        Trigger deletion of a habit from the database.
        :param habit_id: ID of the habit to delete.
        """
        self.db.delete_habit(habit_id)

    def mark_complete(self, habit_id):
        """
        Trigger marking a habit completed in the database.
        :param habit_id: ID of the habit to mark.
        """
        return self.db.mark_habit_completed(habit_id)

    def view(self):
        """
        View all fetch habits from the database with timestamp.
        """
        habits = self.db.get_habits()
        if not habits:
            print("No habits found.")
            return
        print("\nYour habits:")
        for habit in habits:
            habit_id, name, frequency, created_at, last_completed = habit
            status = f"Last completed on {last_completed}" if last_completed else "Not completed yet"
            print(f"[{habit_id}] {name} - {frequency} - Created on {created_at} - {status}")

class ExampleData:
    """
    Handles activating and deactivating a set of example data for demo/testing purposes.
    """
    def __init__(self, db):
        self.db = db
        today = datetime.date.today() - datetime.timedelta(days=1)

        #Generate the example data on call
        self.example_habits = [
            (
                "Morning walk", "daily",
                (today - datetime.timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
                [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(28)]
            ),
            (
                "Read a book", "daily",
                (today - datetime.timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
                [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S") for i in range(0, 28, 2)]
            ),
            (
                "Weekly reflection", "weekly",
                (today - datetime.timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
                [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S") for i in (0, 7, 14, 21)]
            ),
            (
                "Budget review", "monthly",
                (today - datetime.timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
                [(today - datetime.timedelta(days=0)).strftime("%Y-%m-%d %H:%M:%S")]
            ),
            (
                "Annual goal review", "yearly",
                (today - datetime.timedelta(days=28)).strftime("%Y-%m-%d %H:%M:%S"),
                []
            ),
        ]

    def activate(self):
        """
        Fetch and activates the example habits from database
        :return:
        """
        for name, frequency, created_at, completions in self.example_habits:
            existing = [h for h in self.db.get_habits() if h[1] == name]
            if not existing:
                self.db.add_habit_with_completions(name, frequency, created_at, completions)
                self.db.cursor.execute(
                    "SELECT id FROM habits WHERE name=? AND frequency=? AND created_at=?",
                    (name, frequency, created_at)
                )
                habit_id = self.db.cursor.fetchone()[0]
                self.db.add_completions(habit_id, completions)
        print("[INFO] Example data with habits completed has been activated.")

    def deactivate(self):
        """
        Deactivates the example habits from database.
        :return:
        """
        all_habits = self.db.get_habits()
        for habit in all_habits:
            habit_id, name = habit[0], habit[1]
            if name in [eh[0] for eh in self.example_habits]:
                self.db.delete_habit(habit_id)
        print("[INFO] Example data has been deactivated.")