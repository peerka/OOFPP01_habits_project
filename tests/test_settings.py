import os
import pytest
import json

from habit_tracker.settings import Settings

SETTINGS_FILE = "settings.json"

@pytest.fixture
def settings():
    #Remove any existing file
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)
    s = Settings()
    yield s
    if os.path.exists(SETTINGS_FILE):
        os.remove(SETTINGS_FILE)

#Test set_notification_time, sets time to 08:00.
def test_set_notification_time(settings):
    settings.set_notification_time("08:00")
    assert settings.settings["notification_time"] == "08:00"

#Test set_reminder_frequency, sets reminder frequency to weekly.
def test_set_reminder_frequency(settings):
    settings.set_reminder_frequency("weekly")
    assert settings.settings["reminder_frequency"] == "weekly"

#Test load and saved settings from Json file.
def test_load_and_save_settings(settings):
    settings.set_notification_time("08:00")
    settings.set_reminder_frequency("weekly")
    loaded = settings.load_settings()
    assert loaded["notification_time"] == "08:00"
    assert loaded["reminder_frequency"] == "weekly"


