<div align="center">

<img src="assets/logo.png" alt="Smart Study Planner Logo" width="110" />

# Smart Study Planner

**A secure, feature-rich desktop productivity app for university students**

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.2.5%20Apex-7c3aed?style=flat)](docs/releases/v1.2.5.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-64748b?style=flat)]()
[![Tests](https://img.shields.io/badge/tests-5%20passing-22c55e?style=flat)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-0ea5e9?style=flat)](CONTRIBUTING.md)

Manage tasks, timetables, study sessions, and group study — all from a single themed desktop app. Built with Python, Tkinter, and SQLite. No cloud, no subscriptions, no data leaving your machine.

[**Download .exe**](docs/releases/v1.2.5.md) · [**Changelog**](CHANGELOG.md) · [**Roadmap**](ROADMAP.md) · [**Report a Bug**](.github/ISSUE_TEMPLATE/bug.yml)

</div>

---

## 🖼️ Screenshots

> Screenshots are captured from a live build — dark and light themes available.

| Login Screen | Task Dashboard | Study Groups |
|:---:|:---:|:---:|
| *(coming soon)* | *(coming soon)* | *(coming soon)* |

| Focus Timer | Visual Insights | Credits |
|:---:|:---:|:---:|
| *(coming soon)* | *(coming soon)* | *(coming soon)* |

---

## ✨ Features

### 📋 Task Management
- Full CRUD — add, edit, delete, complete tasks
- Priority levels (High / Medium / Low), categories, deadlines, and status tracking
- Search and filter across all tasks
- `Ctrl+N` to add, `Delete` to remove, `Space` to complete

### 📅 Study Timetable
- Weekly, monthly, and 6-month calendar views
- One-click ICS export — open in Google Calendar, Outlook, or Apple Calendar
- Auto-generate a study plan distributed across your deadline load

### ⏱️ Focus Timer
- Pomodoro-style countdown with session tracking
- Ambient soundscapes (looping, with volume control)
- Live audio-wave visualizer synced to playback

### 🤖 Study Assistant
- Local AI-style assistant with typewriter streaming output
- Quick prompts: explain a concept, summarize task load, generate practice questions

### 👥 Study Groups & 🌐 LAN Rooms
- Create groups, add members by email, assign shared tasks and study sessions
- **LAN Study Rooms** — host a named room on your local network; peers discover it automatically via UDP broadcast (no server required)
- Rooms show host name, department, class, and section

### 🎓 Academic Profile
- Department, Class/Batch, Section, and Batch Year stored per account
- Shown in the sidebar and broadcast in LAN room beacons

### 📝 Notes Scratchpad
- Distraction-free writing workspace
- Live word, character, and paragraph counts
- Auto-saves per user; export as `.txt`

### 📊 Visual Insights
- Completion donut chart
- Priority distribution and category breakdown charts
- 5-day task load graph

### 🔐 Security
- Passwords and security answers hashed with **PBKDF2-HMAC-SHA-256** (100,000 iterations, unique random salts)
- All queries are parameterized — no SQL injection surface
- Strict per-user data isolation enforced at the query layer

### 🌍 Localization & Themes
- **12 languages** — English, Deutsch, Español, Français, Русский, 中文, 日本語, 한국어, हिन्दी, اردو, العربية, فارسی
- Full RTL support for Arabic and Persian
- Light and Dark theme — switch live without losing your current screen

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Entry Point                          │
│                     main.py                             │
└────────────────┬──────────────┬──────────────────────────┘
                 │              │
     ┌───────────▼──────┐  ┌────▼──────────────────────┐
     │    CLI Mode       │  │       GUI Mode             │
     │   (main.py)       │  │     (src/gui.py)           │
     └───────────┬───────┘  └────────────┬───────────────┘
                 │                        │
     ┌───────────▼────────────────────────▼───────────────┐
     │               Business Logic                       │
     │              src/logic.py  (TaskManager)           │
     └───────────────────────┬────────────────────────────┘
                             │
     ┌───────────────────────▼────────────────────────────┐
     │                  Data Layer                        │
     │           src/database.py  (DatabaseManager)       │
     └───────────────────────┬────────────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  data/planner.db    │
                  │  (SQLite)           │
                  └─────────────────────┘

  src/lan.py  ──► UDP broadcast (port 50505) — LAN room discovery
```

Full module breakdown in [docs/Architecture.md](docs/Architecture.md).

---

## 🛠️ Technology Stack

### Third-party packages

| Package | Purpose |
|---------|---------|
| [Pillow](https://python-pillow.org/) | Image loading and resizing |
| [PyInstaller](https://pyinstaller.org/) | Windows `.exe` packaging *(build only)* |

### Standard library (no install needed)

| Module | Purpose |
|--------|---------|
| `tkinter` / `ttk` | GUI framework — windows, widgets, themed controls |
| `sqlite3` | Embedded relational database |
| `hashlib` + `secrets` | PBKDF2-HMAC-SHA-256 hashing, random salts |
| `socket` + `threading` | LAN room discovery via UDP broadcast |
| `wave` + `winsound` | Audio synthesis and playback |
| `csv` | Task data export |
| `json` | App preferences and task backup |
| `webbrowser` | GitHub profile links in Credits screen |
| `tkinter.filedialog` | Native save/open dialogs |
| `datetime` / `re` / `os` | Date handling, validation, path resolution |

---

## 🚀 Getting Started

### Requirements
- Python 3.8 or newer
- `Pillow` — the only runtime dependency

### Install and run

```bash
git clone https://github.com/SufiyanAasim/smart-study-planner.git
cd smart-study-planner
pip install -r requirements.txt
python main.py
```

### Launch modes

```bash
python main.py          # GUI (default)
python main.py --cli    # Terminal interface
python main.py --menu   # Mode picker
```

Or double-click **SmartStudyPlanner.exe** on Windows.

---

## 🗂️ Project Structure

```
smart-study-planner/
├── src/
│   ├── gui.py              # All Tkinter panels, canvas, dialogs
│   ├── database.py         # SQLite schema and queries
│   ├── logic.py            # TaskManager — CRUD, stats, JSON backup
│   ├── models.py           # Task dataclass and constants
│   ├── lan.py              # LAN study room discovery (UDP)
│   ├── translations.py     # 12-language dictionary
│   └── utils.py            # Validation, audio, path helpers
├── tests/
│   └── test_database.py    # Integration test suite (5 tests)
├── docs/
│   ├── Architecture.md
│   ├── Database.md
│   ├── Development.md
│   ├── Troubleshooting.md
│   └── releases/           # Per-version release notes
├── assets/
│   ├── icon.ico
│   ├── logo.png
│   └── sounds/             # Synthesized audio and soundscapes
├── data/                   # Created at runtime
├── .github/
│   ├── ISSUE_TEMPLATE/     # Bug, feature, question, docs templates
│   └── workflows/          # CI — test, lint, build, release
├── main.py
├── SmartStudyPlanner.spec
├── requirements.txt
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── LICENSE
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Add new task |
| `Ctrl+F` | Focus search |
| `Ctrl+L` | Log out |
| `Double-click` | Edit selected task |
| `Delete` | Delete selected task |
| `Space` | Mark task complete |

---

## 🧪 Testing

```bash
python -m unittest discover -s tests
```

Covers: authentication, password reset, duplicate registration prevention, per-user task isolation, and task CRUD.

---

## 📦 Building the Windows Executable

```bash
python -m PyInstaller SmartStudyPlanner.spec
```

```powershell
.\build_exe.ps1
```

Output: `SmartStudyPlanner.exe` in the project root.

---

## 🛡️ Security

Passwords and security answers are hashed with PBKDF2-HMAC-SHA-256 (100,000 iterations, unique random salts per user). All database queries are fully parameterized. Per-user data isolation is enforced at the query layer — cross-user access is structurally impossible.

See [SECURITY.md](SECURITY.md) to report a vulnerability.

---

## 🤝 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/SufiyanAasim">
        <img src="https://github.com/SufiyanAasim.png" width="72" alt="SufiyanAasim"/><br/>
        <sub><b>Mohammad Sufiyan Aasim</b></sub>
      </a><br/>
      <sub>System Architect · AI/MLOps · Docs</sub>
    </td>
    <td align="center">
      <a href="https://github.com/FahadBinNasir">
        <img src="https://github.com/FahadBinNasir.png" width="72" alt="FahadBinNasir"/><br/>
        <sub><b>Fahad Bin Nasir</b></sub>
      </a><br/>
      <sub>Back-end Development</sub>
    </td>
    <td align="center">
      <a href="https://github.com/Ifrahim-yousuf">
        <img src="https://github.com/Ifrahim-yousuf.png" width="72" alt="Ifrahim-yousuf"/><br/>
        <sub><b>Ifrahim Yousuf</b></sub>
      </a><br/>
      <sub>UI/UX · Front-end · Animations</sub>
    </td>
    <td align="center">
      <a href="https://github.com/13eeCoder">
        <img src="https://github.com/13eeCoder.png" width="72" alt="13eeCoder"/><br/>
        <sub><b>Taha Siddiqui</b></sub>
      </a><br/>
      <sub>Networking · Cyber Security</sub>
    </td>
  </tr>
</table>

---

## 📄 License

[MIT License](LICENSE) © 2026 Smart Study Planner Contributors.

---

<div align="center">

⭐ **Star this repo if it helped you study smarter.**

[Report Bug](.github/ISSUE_TEMPLATE/bug.yml) · [Request Feature](.github/ISSUE_TEMPLATE/feature.yml) · [Ask a Question](.github/ISSUE_TEMPLATE/question.yml)

</div>
