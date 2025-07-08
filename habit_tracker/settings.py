import json
import os
import time
from datetime import datetime
import platform as py_platform
from pynotifier import Notification, NotificationClient
from pynotifier.backends import platform as pn_platform

#Default application settings
default_settings = {
    "notification_time": "08:00",
    "reminder_frequency": "daily"
}

class Settings:
    """Manage loading, saving and updating application settings"""
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        """
        Initialize settings by loading existing settings or creating defaults
        """
        self.settings = self.load_settings()

    def load_settings(self):
        """
        Load settings from settings JSON file or create defaults if files does not exist
        If failed to load settings, missing file, invalid JSON return default settings
        :return: A dictionary of settings
        """
        try:
            if os.path.exists(self.SETTINGS_FILE):
                with open(self.SETTINGS_FILE, "r") as file:
                    return json.load(file)
            else:
                self.save_settings(default_settings)
                return default_settings
        except (IOError, json.JSONDecodeError) as error:
            print(f"[ERROR] Failed to load settings: {error}")
            return default_settings

    def save_settings(self, settings):
        """
        Save current settings to settings JSON file
        :param settings: The settings to save
        :return: None
        """
        try:
            with open(self.SETTINGS_FILE, "w") as file:
                json.dump(settings, file, indent=4)
        except IOError as error:
            print(f"[ERROR] Failed to save settings: {error}")

    def set_notification_time(self, time_str):
        """
        Set the notification time and save the updated settings
        Check for invalid format, validates format and time values (24hour format)
        :param time_str: Time in HH:MM format
        :return: None
        """
        try:
            # Try parsing the input to validate HH:MM format
            valid_time = datetime.strptime(time_str, "%H:%M")
            self.settings["notification_time"] = time_str
            self.save_settings(self.settings)
            print(f"Notification time is set to {time_str}.")
        except ValueError:
            print(f"[WARNING] Invalid time format: '{time_str}', use 24-hour format HH:MM (e.g., 08:00 or 18:30)")

    def set_reminder_frequency(self, frequency):
        """
        Set reminder frequency, how often the reminder occurs, save the updated settings
        Check user value for frequency.
        :param frequency: frequency for reminder (daily, weekly, monthly, yearly)
        :return: None
        """
        if frequency in ["daily", "weekly", "monthly", "yearly"]:
            self.settings["reminder_frequency"] = frequency
            self.save_settings(self.settings)
            print(f"Reminder frequency is set to {frequency}")
        else:
            print(f"[WARNING] Invalid frequency. Choose from: {frequency}")

class Reminder:
    """Handles sending reminder notifications based on settings"""

    @staticmethod
    def notif_with_pynotify(title: str, message: str):
        """
        Sends notification with pynotifier engine.
        :param title: The title of the notification
        :param message: The message of the notification
        :return:
        """
        try:
            c = NotificationClient()
            c.register_backend(pn_platform.Backend())
            notification = Notification(
                title=title,
                message=message,
                duration=10,
                keep_alive=True,
                threaded=True
            )
            c.notify_all(notification)
            print("[INFO] Notification sent successfully.")
        except Exception as e:
            print(f"[WARNING] Failed to send notification: {e}")

            # Run fallback logic for notification.
            system = py_platform.system()
            try:
                if system == "Linux":
                    import subprocess
                    subprocess.run(["notify-send", title, message])
                    print("[INFO] Notification sent via notify-send fallback.")
                elif system == "Darwin":
                    import os
                    os.system(f'''
                                    osascript -e 'display notification "{message}" with title "{title}"'
                                ''')
                    print("[INFO] Notification sent via osascript fallback.")
                elif system == "Windows":
                    import ctypes
                    MessageBox = ctypes.windll.user32.MessageBoxW
                    MessageBox(None, message, title, 0)
                    print("[INFO] Notification sent via MessageBox fallback.")
                else:
                    print(f"[INFO] Notification fallback: {title} - {message}")
            except Exception as ex:
                print(f"[ERROR] Final notification fallback failed: {ex}")

    def __init__(self, settings):
        """
        Initialize reminder service with settings.
        :param settings: Settings manager instance
        """
        self.settings = settings

    def send_notification(self):
        """
        Send notification if the current time matches schedule notification time.
        If notification fails exception is raised.
        :return: None
        """
        current_time = datetime.now().strftime("%H:%M")
        notification_time = self.settings["notification_time"]
        if current_time == notification_time:
            try:
                self.notif_with_pynotify(
                    title="Habit Reminder",
                    message="Don't forget to log habits today!",
                )
                print("[INFO] Notification sent via pynotifier successfully.")
            except Exception as error:
                print(f"[ERROR] pynotifier failed to send notification: {error}")

                try:
                    os.system('notify-send "Habit Reminder" "Don\'t forget to log habits today!"')
                    print("[INFO] Notification sent via notify-send successfully.")
                except Exception as error:
                    print(f"[ERROR] Both failed to send notification: {error}")

    def start_reminder_loop(self):
        """
        Start a continuous reminder loop to send notifications.
        :return: None
        """
        print("Reminder service started.")
        last_notified = None
        try:
            while True:
                current_time = datetime.now().strftime("%H:%M")
                notification_time = self.settings["notification_time"]
                if current_time == notification_time and last_notified != current_time:
                    self.send_notification()
                    last_notified = current_time
                    time.sleep(61) #check every minute
                else:
                    time.sleep(10)
        except KeyboardInterrupt:
            print("Reminder service stopped.")