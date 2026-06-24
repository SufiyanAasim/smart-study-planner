# Smart Study Planner

A secure, production-ready, dual-interface desktop application designed for university students to manage academic coursework, deadlines, exams, and milestones. Built in Python, it integrates a command-line interface (CLI) and a sleek Tkinter graphical user interface (GUI) sharing a unified SQLite database backend with strict user isolation, password hashing, and visual analytics.

> **Current version: 2.0.0 “Polish & Motion”** — see the [Changelog](CHANGELOG.md) for the full release history.

---

## Author

* **Author:** Mohammad Sufiyan Aasim ([@msufiyanpk](https://github.com/msufiyanpk))
* **License:** [MIT License](LICENSE)

---

## Features

### 1. Unified Launch Orchestrator
- A single entry point (`main.py` or `SmartStudyPlanner.exe`) presents an interactive choice to run in **CLI Mode**, **GUI Mode**, or **Exit**.

### 2. Relational Database & User Isolation
- Powered by a SQLite backend (`data/planner.db`) containing two relational tables: `users` and `tasks` linked via `user_id` foreign keys.
- **Strict User Isolation:** Logged-in users can only view, create, edit, search, or delete their own data. Cross-user database leaks are mathematically prevented.
- **User-Specific Backups:** Automatically exports state backups to user-specific JSON files (`data/tasks_user_{id}.json`).

### 3. Comprehensive Security Model
- **Secure Hashing:** Passwords and security recovery answers are hashed using **PBKDF2 HMAC SHA-256** with unique, cryptographically random salts (100,000 iterations). Plaintext passwords are never stored.
- **Form Validations:**
  - Standard email format checking (regular expression).
  - Password strength verification (minimum 8 characters, at least one uppercase letter, one lowercase letter, one digit, and one special character).
  - Full Name validation.
- **Password Recovery:** Offers a secure "Forgot Password" workflow utilizing pre-registered Security Questions and hashed answer checks.

### 4. Rich Task Management (CRUD)
- Supports adding, viewing, modifying, completing, and deleting tasks.
- **Fields:** Title, Description, Priority (High, Medium, Low), Category (Study, Assignment, Exam, Project, Lab, etc.), Due Date (Deadline), and Status.
- **Query Engine:** Full support for keyword searches across titles/descriptions, status filters (Pending, Completed, Overdue), priority filters, category filters, and sorting (by deadline, priority, title, or category).
- **Polished empty states:** dedicated "No tasks yet" / "No matching tasks" messaging distinguishes a brand-new workspace from over-narrow filters.

### 5. Interactive Visual Dashboards
- **CLI Mode:** Renders dynamic stats, text-based completion bars, priority/category counts, and smart study recommendations.
- **GUI Mode (Tkinter):** A modern slate dashboard featuring:
  - Responsive grid and sidebar layout with Light/Dark theme switching that **preserves your current screen and form data** (no bounce back to login).
  - Form validation with **Password Visibility Toggles** (eye icons).
  - **Dynamic Canvas Drawings:** completion donut, priority bar chart, category bar chart, and a 5-day study-load line graph — with an empty-state placeholder when there is no data yet.

### 6. Focus Pomodoro Timer & Soundscapes
- Built-in study timer supporting the Pomodoro technique (25-min Work Session, 5-min Short Break).
- Interactive **Canvas Audio Wave Visualizer** that reacts to live soundscape playback.
- Selectable ambient study soundscapes (*Silence*, *Lo-Fi Beats*, *Rainforest*, *White Noise*, *Ocean Waves*, *Warm Fireplace*) — real, seamlessly-looping audio with **Play/Pause** and a **Volume** slider — plus a **bespoke completion chime** on countdown completion.

### 7. Study Assistant (Local Typewriter Simulator)
- Local chat interface supporting preloaded quick prompt actions (*Explain Concept*, *Summarize Tasks*, *Practice Questions*).
- Streams responses fluidly using a typewriter streaming animation.

### 8. Calendar Sync & Export (ICS Format)
- Instantly exports the user's active coursework timetable to an RFC-compliant timezone-safe `.ics` file.
- Events are formatted as all-day entries with priority labels, importable into Google Calendar or Microsoft Outlook.

### 9. Collaborative Study Groups
- Relational SQLite-backed team dashboard (`study_groups`, `group_members`, `group_tasks`).
- Prepopulated with a "Global Study Circle" demo group upon setup.
- Supports adding students by email, assigning joint tasks, and scheduling virtual group study sessions.

### 10. Premium UI, Motion, Audio & 12-Language Localization
- **Animated Interactive Backgrounds:** the Login/Register/Recovery, Focus Timer, and Credits screens render a performant, theme-aware **particle-constellation background** (drifting nodes linked by faint lines). Data-dense screens stay clean by design. The animation pauses when its screen is hidden and uses no extra image assets.
- **Bespoke Sound Design:** custom-synthesized audio cues (`click`, `success`, `error`, `notify`) bundled in `assets/sounds/`, with a graceful fallback to system sounds. All effects can be toggled on/off from **Settings → Sound & Feedback**.
- **Faster Sign-In:** the last identifier used on the machine is remembered and prefilled on the login screen (stored in `data/app_prefs.json`), and a **registered-accounts quick-pick** lets you click a chip to fill the identifier.
- **Exit Confirmation:** closing via the window button or an in-app Exit button asks for confirmation first, preventing accidental shutdowns.
- **Aligned Controls:** a properly themed language dropdown and an enhanced Light/Dark toggle, consistently aligned across all authentication screens and Settings.
- **Multilingual Support:** real-time translation covering **English**, **German (Deutsch)**, **Spanish (Español)**, **French (Français)**, **Russian (Русский)**, **Chinese (中文)**, **Japanese (日本語)**, **Korean (한국어)**, **Hindi (हिन्दी)**, **Urdu (اردو)**, **Arabic (العربية)**, and **Persian (فارسی)** — including right-to-left scripts.

---

## Folder Structure

```
├── assets/                     # Branding and media assets
│   ├── background.png          # (legacy) auth background image
│   ├── logo.png                # Application logo
│   ├── icon.ico                # Executable / window / taskbar icon
│   └── sounds/                 # Bespoke synthesized audio
│       ├── click.wav           # UI cues
│       ├── success.wav
│       ├── error.wav
│       ├── notify.wav
│       └── scape_*.wav         # Looping ambient soundscapes (lofi/rain/white/ocean/fire)
├── data/                       # SQLite database, JSON backups, and app_prefs.json
│   └── planner.db              # Relational database file
├── tests/                      # Automated test suite
│   └── test_database.py        # Comprehensive unit and integration tests
├── build_exe.ps1               # PowerShell build script for packaging
├── database.py                 # SQLite database schemas and query logic
├── gui.py                      # Tkinter GUI panels, animated canvas, and rendering
├── logic.py                    # TaskManager business logic controller
├── main.py                     # Entry point and terminal CLI interface
├── models.py                   # Task data structure models & JSON serializers
├── translations.py             # Centralized 12-language translation dictionary
├── utils.py                    # Security (hashing), validation, and audio helpers
├── requirements.txt            # Dependency configuration (PyInstaller)
├── README.md                   # Application documentation
├── About.md                    # Complete project & screen description
├── CHANGELOG.md                # Versioned, categorized change history
├── RELEASE_NOTES.md            # User-facing release highlights
└── LICENSE                     # Project license details
```

---

## Installation & Setup

### Prerequisites
- Python 3.8 or newer installed on your machine.
- Pip package manager.

### Install Dependencies
This application utilizes Python's standard library (SQLite3, Tkinter, Hashlib, Secrets, Wave) plus **Pillow** for image handling. The packaging dependency is for executable compilation:
```bash
pip install -r requirements.txt
```

---

## Usage

### 1. Launching from Source Code
Open a terminal in the root directory and execute:
```bash
python main.py
```
This prints the launch menu:
1. **Launch CLI Mode (Terminal):** Starts the CLI interface for registering, logging in, recovering passwords, and managing task workspaces directly in your terminal.
2. **Launch GUI Mode (Desktop Application):** Starts the desktop window dashboard.
3. **Exit:** Safely closes the planner.

### 2. Launching the GUI Directly
```bash
python gui.py
```

---

## Packaging the Windows Executable (.exe)

A production-ready executable can be generated using PyInstaller:

```bash
python -m PyInstaller --onefile --name "SmartStudyPlanner" --icon "assets/icon.ico" --add-data "assets;assets" --distpath . --workpath .build --specpath . "main.py"
```
*This command is defined inside `build_exe.ps1`.* The `--icon "assets/icon.ico"` flag sets the executable/taskbar icon, and `--add-data "assets;assets"` bundles the branding images **and** the `assets/sounds/` audio cues into the executable.

---

## Testing

Run the automated unit and integration tests using Python's unittest framework:
```bash
python -m unittest discover -s tests
```
The test suite validates password hashing and reset logic, duplicate registration prevention, user-isolation boundaries, and task CRUD/statistics calculations.

---

## Developer Credits

Developed by **Mohammad Sufiyan Aasim**.
- **Email**: [sufiyanaasim@outlook.com](mailto:sufiyanaasim@outlook.com)
- **GitHub**: [msufiyanpk](https://github.com/msufiyanpk)

## License

This project is licensed under the [MIT License](LICENSE) © 2026 Mohammad Sufiyan Aasim.
