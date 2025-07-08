from setuptools import setup, find_packages

setup(
    name='habit-tracker',
    version='0.0.1',
    description="A commandline-based Habit tracker application with analytics tools and reminders",
    author="Patrik Soerman",
    author_email="<EMAIL>",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rich",
        "matplotlib",
        "py-notifier",
        "schedule",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "habit=habit_tracker.main:main"
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming language :: python :: 3",
        "Operating System :: OS Independent",
    ],
)


