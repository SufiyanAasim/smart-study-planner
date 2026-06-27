# Smart Study Planner

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.0%20Apex-blueviolet)](docs/releases/v1.2.0.md)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()

A secure, dual-interface desktop application for university students to manage academic coursework, deadlines, exams, and study sessions. Built in Python with a Tkinter GUI and a shared SQLite backend.

---

## Features

| Feature | Details |
|---------|---------|
| Task management | CRUD with priority, category, deadline, status, search, and filtering |
| Study timetable | Weekly, monthly, and 6-month views; ICS calendar export |
| Focus timer | Pomodoro technique with ambient soundscapes and an audio-wave visualizer |
| Study assistant | Local prompt-based assistant with typewriter streaming |
| Study groups | Member management, shared tasks, and scheduled sessions |
| Notes scratchpad | Auto-saving, live word/character/paragraph counts, TXT export |
| Visual insights | Completion donut, priority chart, category chart, 5-day load graph |
| Security | PBKDF2-HMAC-SHA-256 hashing, security-question recovery, per-user isolation |
| Localization | 12 languages including Arabic and Persian (RTL supported) |
| Themes | Light and Dark — switch at any time without losing your current screen |

---

## Screenshots

> Screenshots coming soon. See [docs/Architecture.md](docs/Architecture.md) for a layout description.

---

## Architecture

```
main.py  ──►  src/gui.py       (Tkinter UI)
         └──►  src/logic.py    (TaskManager)
                    └──►  src/database.py  (SQLite)
```

Full details in [docs/Architecture.md](docs/Architecture.md).

---

## Technology stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.8+ |
| GUI | Tkinter / ttk |
| Database | SQLite 3 (standard library) |
| Image handling | Pillow |
| Audio | wave + winsound / playsound |
| Packaging | PyInstaller |
| Security | hashlib PBKDF2-HMAC-SHA-256 |

---

## Requirements

- Python 3.8 or newer
- pip

---

## Installation

```bash
git clone https://github.com/SufiyanAasim/smart-study-planner.git
cd smart-study-planner
pip install -r requirements.txt
```

---

## Quick start

```bash
# Launch GUI (default)
python main.py

# Launch CLI interface
python main.py --cli

# Show mode picker
python main.py --menu
```

Or double-click **SmartStudyPlanner.exe** on Windows.

---

## Project structure

```
smart-study-planner/
├── src/
│   ├── database.py         # SQLite schema and all queries
│   ├── gui.py              # Tkinter GUI — panels, canvas, dialogs
│   ├── logic.py            # TaskManager business logic
│   ├── models.py           # Task data model and constants
│   ├── translations.py     # 12-language translation dictionary
│   └── utils.py            # Validation, audio, and path helpers
├── tests/
│   └── test_database.py    # Unit and integration test suite
├── docs/
│   ├── Architecture.md
│   ├── Database.md
│   ├── Development.md
│   ├── Troubleshooting.md
│   └── releases/           # Per-version release notes
├── assets/
│   ├── icon.ico
│   ├── logo.png
│   └── sounds/             # Synthesized audio cues and soundscapes
├── data/                   # Created at runtime (database + JSON backups)
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
├── main.py                 # Entry point
├── SmartStudyPlanner.spec  # PyInstaller build spec
├── build_exe.ps1           # Windows build helper
├── requirements.txt
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── ROADMAP.md
└── LICENSE
```

---

## Testing

```bash
python -m unittest discover -s tests
```

Covers password hashing and reset, duplicate registration prevention, user-isolation boundaries, and task CRUD/statistics.

---

## Building the Windows executable

```bash
python -m PyInstaller SmartStudyPlanner.spec
```

Or:

```powershell
.\build_exe.ps1
```

The output `SmartStudyPlanner.exe` is placed in the project root.

---

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Add new task (Tasks panel) |
| `Ctrl+F` | Focus task search |
| `Ctrl+L` | Log out |
| `Double-click` | Edit selected task |
| `Delete` | Delete selected task |
| `Space` | Complete selected task |

---

## Security

Passwords and security answers are hashed with PBKDF2-HMAC-SHA-256 (100,000 iterations, unique random salts). All database queries are parameterized. Per-user data isolation is enforced at the query layer. See [SECURITY.md](SECURITY.md) for the full policy and how to report vulnerabilities.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Roadmap

See [ROADMAP.md](ROADMAP.md). Next: v1.3.0 — LAN connectivity, department and class profiles, real-time group study.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full versioned history.

---

## Contributors

| Name | Role | GitHub |
|------|------|--------|
| Mohammad Sufiyan Aasim | System Architect · AI/MLOps · Documentation | [@SufiyanAasim](https://github.com/SufiyanAasim) |
| Fahad Bin Nasir | Back-end Development | [@FahadBinNasir](https://github.com/FahadBinNasir) |
| Ifrahim Yousuf | UI/UX Designer · Front-end Development | [@ifrahim-yousaf](https://github.com/ifrahim-yousaf) |
| Taha Siddiqui | Networking & Cyber Security | [@13eeCoder](https://github.com/13eeCoder) |

---

## License

[MIT License](LICENSE) © 2026 Smart Study Planner Contributors.
