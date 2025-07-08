#!/usr/bin/env python3

import argparse
import signal
import subprocess
import sys
import os
import platform
from .database import Database, Habit, ExampleData
from .analysis import (
    get_all_habits,
    get_habit_streak,
    get_longest_streak,
    get_habits_by_frequency,
    plot_habits_completion, calculate_streak,
    get_completion_count
)
from .settings import Settings, Reminder
from rich.console import Console
from rich.table import Table

console = Console()

#Habits commands

def create_habits(name, frequency):
    """
    Create a new habit in the database and close connection.
    :param name: Name of the habit to create.
    :param frequency: Frequency of the habit (daily, weekly, monthly, yearly).
    :return: None.
    """
    db = Database()
    habit = Habit(db)
    habit.create(name, frequency)
    db.close()

def delete_habits(habit_id):
    """
    Delete habit by ID from database and close connection.
    :param habit_id: ID of the habit to delete.
    :return: None
    """
    db = Database()
    habit = Habit(db)
    habit.delete(habit_id)
    db.close()

def mark_habit_completed(habit_id):
    """
    Mark habit completed by ID from database and close connection.
    :param habit_id: ID of the habit to mark.
    :return: None.
    """
    db = Database()
    habit = Habit(db)
    was_completed = habit.mark_complete(habit_id)
    if was_completed:
        habits = db.get_habits()
        frequency, name = None, None
        for h in habits:
            if h[0] == habit_id:
                _, name, frequency = h[:3]
                break
        if frequency and name:
            completions = db.get_completions(habit_id)
            streak = calculate_streak(completions, frequency)
            console.print(f"Habit {name} with ID {habit_id} has been marked completed.")
            console.print(f"Great work, You've fulfilled {frequency} streak for '{name}': {streak} {frequency}{'s' if streak > 1 else ''} in a row")
        db.close()

def view_habits():
    """
    Display all habits in database by printing to console and close connection.
    :return: None.
    """
    db = Database()
    habit = Habit(db)
    habit.view()
    db.close()

def activate_example_data():
    """
    Activate example data.
    :return: None
    """
    db = Database()
    ex = ExampleData(db)
    ex.activate()
    db.close()

def deactivate_example_data():
    """
    Deactivate example data.
    :return: None
    """
    db = Database()
    ex = ExampleData(db)
    ex.deactivate()
    db.close()

def longest_streak():
    """
    Print longest streak of habits summary to console.
    :return: None.
    """
    db = Database()
    console.print("[bold blue] Habit Analysis longest streak:[/bold blue]")
    longest, streaks = get_longest_streak(db)
    if longest:
        console.print(f"Longest streak:[bold green] {longest}[/bold green] with {streaks} streaks")
    else:
        console.print("No habits with streak data found!")
    db.close()

def habit_streak(name):
    """
    Print habit streak of a specified habit by name.
    :param name: Name of the habit to check streak.
    :return: None.
    """
    db = Database()
    habits = get_all_habits(db)
    matches = [h for h in habits if name.lower() in h[1].lower()]
    if not matches:
        console.print(f"[bold red] Habit '{name}' not found![/bold red]")
    elif len(matches) == 1:
        habit_id, full_name, frequency = matches[0]
        completions = db.get_completions(habit_id)
        streak = calculate_streak(completions, frequency)
        console.print(f"[bold green]{full_name}[/bold green] has a {streak} {frequency}{'s' if streak > 1 else ''} streak.")
    else:
        console.print(f"[bold yellow]Multiple habits found matching your search [/bold yellow]")
        for h in matches:
            console.print(f"[cyan]{h[1]}[/cyan] (ID: {h[0]}, Frequency: {h[2]})")
        console.print("[bold]Please be more specific or use the habit ID.[/bold]")
    db.close()

def plot_habits():
    """
    Generate and display a chart of habits completion.
    :return: None.
    """
    db = Database()
    plot_habits_completion(db)
    db.close()

def show_all_habits():
    """
    Display all tracked habits in a formatted table.
    :return: None.
    """
    db = Database()
    habits = get_all_habits(db)
    if not habits:
        console.print("[bold red]No habits found![/bold red]")
        db.close()
        return
    table = Table(title="ALL Tracked Habits")
    table.add_column("ID", style="cyan")
    table.add_column("Habit Name", style="cyan")
    table.add_column("Frequency", style="magenta")
    table.add_column("Streak", style="yellow")
    table.add_column("Completions", style="green")
    for habit_id, name, frequency in habits:
        completions_count = get_completion_count(db, habit_id)
        streak = get_habit_streak(db, habit_id, frequency)
        table.add_row(str(habit_id), name, frequency, str(streak), str(completions_count))
    console.print(table)
    db.close()

def filter_habits_by_frequency(frequency):
    """
    Display habits filtered by frequency in a formatted table.
    :param frequency: Frequency of the habit (daily, weekly, monthly, yearly).
    :return: None
    """
    db = Database()
    habits = get_habits_by_frequency(db, frequency)
    if not habits:
        console.print(f"[bold red] No habits found with frequency {frequency}[/bold red]")
        db.close()
        return

    table = Table(title=f"Habits with frequency {frequency}")
    table.add_column("ID", style="cyan")
    table.add_column("Habit Name", style="magenta")
    for habit_id, name in habits:
        table.add_row(str(habit_id), name)
    console.print(table)
    db.close()

def set_notification_time(time_str):
    """
    Update notification time in setting.
    :param time_str: Time in HH:MM format.
    :return: None
    """
    settings = Settings()
    settings.set_notification_time(time_str)

def set_reminder_frequency(frequency):
    """
    Update reminder frequency in setting.
    :param frequency: Frequency of the habit (daily, weekly, monthly, yearly).
    :return: None.
    """
    settings = Settings()
    settings.set_reminder_frequency(frequency)

def start_reminder():
    """
    Start reminder loop based on stored setting
    :return: None.
    """
    settings = Settings().load_settings()
    reminder = Reminder(settings)
    reminder.start_reminder_loop()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PID_FILE = os.path.join(PROJECT_ROOT, "reminder.pid")

def start_reminder_in_background():
    """
    Launch the start_reminder method and loop based on stored setting and fork a background process.
    :return:
    """
    # Launch as a detach process
    proc = subprocess.Popen([sys.executable, "-m", "habit_tracker.main", "settings", "run_reminder"])
    # Save a PID for kill process
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    print(f"[INFO] Reminder started in background with PID {proc.pid}, you can keep using the terminal or close.")

def stop_reminder():
    """
    Stop reminder background process.
    :return:
    """
    try:
        if not os.path.exists(PID_FILE):
            print(f"[ERROR] No PID file found, is the reminder running?")
            return
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        try:
            os.kill(pid, signal.SIGTERM)
            print(f"[INFO] Reminder process {pid} stopped.")
        except  ProcessLookupError:
            print("f[WARNING] No process with PID {pid} found.")
        os.remove(PID_FILE)
    except Exception as e:
        print(f"[ERROR] Could not stop reminder: {e}")


def main():
    """
    Parse command line arguments and execution of corresponding action.
    :return: None.
    """
    parser = argparse.ArgumentParser(description="Habit tracker CLI")
    subparsers = parser.add_subparsers(dest="command")

    habit_parser = subparsers.add_parser("habit", help="Habit actions")
    habit_parser.add_argument(
        "action", choices=["create", "delete", "view", "complete"], help="Habit operation")
    habit_parser.add_argument("--name", help="Habit name, if habit name contain space use \"\" to create multiple-words sentences")
    habit_parser.add_argument("--frequency", choices=["daily", "weekly", "monthly", "yearly"], help="Frequency")
    habit_parser.add_argument("--id", type=int, help="Habit ID")

    example_parser = subparsers.add_parser("example", help="Example actions")
    example_parser.add_argument("action", choices= ["activate", "deactivate"], help="Activate or Deactivate Example data")

    analytics_parser = subparsers.add_parser("analytics", help="Analytics tools")
    analytics_parser.add_argument("action", choices=["longest_streak", "streak", "plot", "summary", "filter"], help="Analytics operation")
    analytics_parser.add_argument("--name", help="Habit name for streak, if habit name has space use partial name search or \"\" to search")
    analytics_parser.add_argument("--frequency", choices=["daily", "weekly", "monthly", "yearly"], help="Filter habits by frequency")

    settings_parser = subparsers.add_parser("settings", help="Reminder settings")
    settings_parser.add_argument("action", choices=["set_time", "set_frequency", "start_reminder",  "stop_reminder", "run_reminder"], help="Settings option. [NOTE: 'run_reminder' is for logic only and test and should not be called directly.]")
    settings_parser.add_argument("--time", help="Notification time (HH:MM)")
    settings_parser.add_argument("--frequency", choices=["daily", "weekly", "monthly", "yearly"], help="Reminder frequency")


    args = parser.parse_args()

    if args.command == "habit":
        if args.action == "create" and args.name and args.frequency:
            create_habits(args.name, args.frequency)
        elif args.action == "delete" and args.id:
            delete_habits(args.id)
        elif args.action == "complete" and args.id:
            mark_habit_completed(args.id)
        elif args.action == "view":
            view_habits()

    if args.command == "example":
        if args.action == "activate":
            activate_example_data()
        elif args.action == "deactivate":
            deactivate_example_data()

    elif args.command == "analytics":
        if args.action == "longest_streak":
            longest_streak()
        elif args.action == "streak" and args.name:
            habit_streak(args.name)
        elif args.action == "plot":
            plot_habits()
        elif args.action == "summary":
            show_all_habits()
        elif args.action == "filter":
            filter_habits_by_frequency(args.frequency)

    elif args.command == "settings":
        if args.action == "set_time" and args.time:
            set_notification_time(args.time)
        elif args.action == "set_frequency" and args.frequency:
            set_reminder_frequency(args.frequency)
        elif args.action == "start_reminder":
            start_reminder_in_background()
        elif args.action == "run_reminder": # not callable user action, used for testing and run the notification logic
            start_reminder()
        elif args.action == "stop_reminder":
            stop_reminder()

if __name__ == "__main__":
    main()