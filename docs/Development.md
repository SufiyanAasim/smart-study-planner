# Development

## Prerequisites

- Python 3.8 or newer
- pip

## Setup

```bash
git clone https://github.com/SufiyanAasim/smart-study-planner.git
cd smart-study-planner
pip install -r requirements.txt
```

## Running from source

```bash
# GUI (default)
python main.py

# CLI interface
python main.py --cli

# Interactive mode picker
python main.py --menu
```

## Running tests

```bash
python -m unittest discover -s tests
```

The test suite covers password hashing and reset logic, duplicate registration prevention, user-isolation boundaries, and task CRUD/statistics.

## Project structure

```
smart-study-planner/
├── src/                    # Application source
│   ├── database.py         # SQLite schema and queries
│   ├── gui.py              # Tkinter GUI
│   ├── logic.py            # TaskManager business logic
│   ├── models.py           # Task data model
│   ├── translations.py     # 12-language dictionary
│   └── utils.py            # Validation and audio helpers
├── tests/
│   └── test_database.py
├── docs/
│   ├── Architecture.md
│   ├── Database.md
│   ├── Development.md
│   ├── Troubleshooting.md
│   └── releases/
├── assets/
│   ├── icon.ico
│   ├── logo.png
│   └── sounds/
├── data/                   # Created at runtime
├── .github/
├── main.py                 # Entry point
├── requirements.txt
└── SmartStudyPlanner.spec  # PyInstaller spec
```

## Building the Windows executable

```bash
python -m PyInstaller SmartStudyPlanner.spec
```

Or use the PowerShell helper:

```powershell
.\build_exe.ps1
```

The output `SmartStudyPlanner.exe` is placed in the project root.

## Commit convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(gui): add department profile fields
fix(auth): handle empty username on login
docs(readme): update installation section
refactor(db): extract query helpers
perf(gui): reduce particle canvas redraws
test(auth): add security question edge cases
```

One commit per release (`release: v4.0.0 - <Codename>`). No noise commits for minor doc or config tweaks — stage everything into the release commit.

## Branch naming

```
main
develop
feature/lan-connectivity
feature/department-profiles
bugfix/timer-audio-crash
docs/api-reference
release/v4.0.0
hotfix/login-encoding
```
