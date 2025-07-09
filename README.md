# Command-line Habit tracker

This is a modular command-line habit tracker built with Python using 'argparse'.
Track, manage and analyze your habits seamlessly with daily, weekly, monthly or yearly frequencies.
Includes notification reminders and progress analytics -- all running seamlessly directly in your terminal. 

---

## Features

- Add, remove, or view habits
- Track habits with custom frequencies (daily, weekly, etc..)
- Mark habits as completed
- Receive morning or evening desktop notifications based on preference
- Analyze habits streaks and progress graphs with matplot
- Configure notification and reminders

---

## Project Structure
```shell
habit-tracker-application/
├── .venv          
├── habit_tracker/          
│   ├── __init__.py
│   ├── main.py             #Entry point using argparse
│   ├── database.py         #Habit management and SQLite interactions
│   ├── analysis.py         #Analytics and graph generation
│   ├── settings.py         #Notification and user preference
│
├── tests/
│   ├── test_analysis.py
│   ├── test_database.py
│   ├── test_settings.py
│
├── setup.py
├── README.md
└── requirements.txt
```
---

## Installation 
#### Option 1:
```shell
To insatll make sure system is compatilbe with pip and git and installed 
Clone and install from GitHub:

pip install git+https://github.com/peerka/OOFPP01_habits_project.git
```
#### Option 2: 
```shell
#In terminal run following steps 
git clone https://github.com/peerka/OOFPP01_habits_project.git
cd OOFPP01_habits_project
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt 
# Run pip install 
pip insatll . 
```

## Uninstall the habit tracker
```shell
pip uninstall habit_tracker
```
## How to use

How to use the habit tracker

### commands : habit | analytics | settings | example
--h or --help for simple help while usage of the application

### habit actions: create, delete, view, complete
```shell
## create a habit --name, --frequency (daily, weekly, monthly, yearly)
habit habit create --name programming --frequency daily

## delete a habit using it's id --id
habit habit delete --id 26

## complete mark habit as complete for period using it's id --id
habit habit complete --id 26

## view habits when created, display all habits
habit habit view
```
### analytics actions: longest streak, streak, plot, summary, filter
```shell
## longest streak display longest streaks
habit analytics longest_streak

## streak show streak of a specified habit by it's name --name
habit analytics streak --name programming 

## plotting progress of habits
habit analytics plot

## Show a list of habits, completions streaks
habit analytics summary

## filter and show streaks by frequency --frequency
habit analytics filter -- frequency daily
```
### settings actions: set_time, set_frequency, start_reminder
```shell
## setting time for notifications --time
habit settings set_time --time 08:30

##  setting the reminder frequency for notifications --frequency
habit settings set_frequency --frequency daily

## starting the reminders in a background process
habit settings start_reminder

## will stop the reminder background process
habit settings stop_reminder
```
### example actions: activate, deactivate
```shell
## activate activates preinstalled habits for testing
habit example activate

## deactivate, deactivates the preinstalled habits
habit example deactivate

### Delete the database and restart with ID 1 
rm habits.db
```

## Test Modules and running tests 

This project use pytest to test modules and key methods functionality, unit testing.

To run all tests, navigate to root folder and run: pytest tests/
