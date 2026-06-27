# Changelog

All notable changes to Smart Study Planner are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] — "Apex" — 2026-06-28

### Added
- **Notes Scratchpad.** A distraction-free, sidebar-accessible note-taking workspace. Displays live word, character, and paragraph counts. Auto-saves per-user content to the SQLite database. Supports exporting drafts as `.txt` files. Fully translated across all 12 languages.
- **Console-free packaged executable.** Built with `--noconsole` — double-clicking `SmartStudyPlanner.exe` opens the GUI directly without spawning a terminal window.

### Changed
- `main.py` now launches the GUI by default unless `--cli` or `--menu` is passed.
- Standard output reconfigured to UTF-8 to prevent charmap encoding errors on Windows terminals.

### Improved
- Repository restructured to professional open-source standard: source files moved to `src/`, full `docs/` hierarchy, `.github/` issue templates and CI workflows.
- All source module headers updated to reflect current contributor roles.
- Asset path resolution anchored to the project root, resolving a regression introduced by the `src/` move.

---

## [1.1.5] — "Horizon" — 2026-06-26

### Added
- **Animated particle-constellation backgrounds.** A `ParticleCanvas` renders a drifting, theme-aware background behind the authentication screens, Focus Timer, and Credits screen. Capped at ~25 fps, pauses when off-screen, uses no extra image assets.
- **Bespoke sound design.** Custom-synthesized audio cues (`click`, `success`, `error`, `notify`) in `assets/sounds/`, replacing raw system beeps.
- **Sound enable/disable toggle.** Settings → Sound & Feedback; preference persists across sessions.
- **Last-identifier prefill.** The login screen remembers and prefills the last used username or email (stored in `data/app_prefs.json`), with focus moved to the password field.
- **Exit confirmation.** Closing via the window X or an in-app Exit button asks for confirmation first.
- **Empty states.** Dedicated translated messages for Tasks ("No tasks yet" / "No matching tasks"), Insights, and Study Timetable.
- **Arabic (العربية) and Persian (فارسی)** — total localization now covers **12 languages**, including right-to-left script support.
- **Playable ambient soundscapes.** Real, seamlessly-looping audio in the Focus Timer with Play/Pause, a Volume slider, and a live-reacting audio-wave visualizer.
- **Registered-accounts quick-pick.** Click an account chip on the login screen to prefill the identifier.
- **Exit button** in the dashboard sidebar (below Log Out), distinguished by color — Log Out is amber, Exit is red.
- **Update Profile card** in Settings — edit Full Name, Username, and Email with validation and uniqueness checks; the sidebar refreshes instantly.
- **Study group deletion** — removes the group, its members, and its shared tasks.
- **Application icon** (`assets/icon.ico`) applied to the window, taskbar, and packaged executable.
- **Eye (show/hide) toggles** on the New/Confirm password fields in Settings.

### Changed
- Language selector replaced with a properly themed `ttk.Combobox` on all auth screens and Settings.
- Light/Dark theme toggle redesigned as an enhanced, accent-bordered pill control.
- Theme switching now preserves the active screen and form data — no bounce back to login.
- Timer completion plays the bespoke `notify` chime instead of a raw `MessageBeep`.
- Authentication background uses the same particle-constellation as the Focus Timer.
- Usernames are now always stored lowercase — enforced live and at the database layer.

### Fixed
- **Focus Timer rendered blank.** Switched from `place()` to grid-centering so the full timer UI renders reliably.
- **Register/Recovery theme bounce.** Screen state is now captured and restored across the theme rebuild.
- **Latent `TclError` crashes.** Study Assistant typewriter and timer audio visualizer now guard on `winfo_exists()` before rescheduling `after()` callbacks.
- **Calendar `.ics` export `TypeError`.** Deadline `date` objects are now formatted directly instead of being treated as strings.
- **Invisible active sidebar tab in light mode.** Resting colors are now mutable so the active-tab highlight survives hover.
- **Insights dashboard blank with no data.** Charts now always render headings and default zero values.
- **Sound effects silent when launched from another directory.** Asset paths now anchor to the project root.

---

## [1.1.0] — "Genesis" — 2026-06-25

### Added
- Unified launch orchestrator (`main.py`) offering CLI mode, GUI mode, or exit.
- Relational SQLite backend with `users` and `tasks` tables and strict per-user data isolation, plus user-specific JSON backups.
- PBKDF2-HMAC-SHA-256 password and security-answer hashing (100k iterations, random salts).
- Security-question password recovery workflow.
- Email, password strength, and full-name validation.
- Rich task CRUD — title, description, priority, category, deadline, and status.
- Query engine: keyword search, status/priority/category filters, multi-key sorting.
- CLI text stats, completion bars, priority/category counts, and study recommendations.
- Dynamic canvas dashboards: completion donut, priority bar chart, category bar chart, 5-day load line graph.
- Focus Pomodoro Timer (25-min work / 5-min break) with ambient soundscape selection and an animated audio-wave visualizer.
- Local study assistant with quick prompts and typewriter streaming animation.
- Collaborative Study Groups: member management, joint tasks, and scheduled sessions.
- Calendar export to RFC-compliant `.ics` files.
- CSV export and study-summary report generator in Settings.
- 10-language localization: English, German, Spanish, French, Russian, Chinese, Japanese, Korean, Hindi, and Urdu.
- Automated test suite covering hashing, registration, user isolation, and task statistics.

---

## [1.0.5] — "Momentum" — 2026-06-20

### Added
- First functional CLI build — registration, login, password recovery, and task CRUD operational end-to-end.
- SQLite schema stabilized; per-user data isolation enforced at the query layer.
- JSON task backup export working alongside the database.
- Password strength validation and PBKDF2-HMAC-SHA-256 hashing integrated.
- Basic Tkinter window scaffold with sidebar navigation and placeholder panels.

### Fixed
- Database initialization errors on first run when `data/` directory did not exist.
- Hashing inconsistency between registration and login due to encoding mismatch.

---

## [1.0.0] — "Insight" — 2026-06-18

> Pre-release. Internal development milestone — not publicly distributed.

### Added
- Initial project scaffold: `main.py` entry point, `database.py`, `models.py`, `logic.py`, `utils.py`.
- SQLite database schema design for `users` and `tasks`.
- Authentication proof-of-concept: register and login flow with plaintext verification (replaced in v1.0.5).
- Task data model (`Task` dataclass) with serialization/deserialization.
- Basic CLI loop for task entry and listing.

---

[1.2.0]: docs/releases/v1.2.0.md
[1.1.5]: docs/releases/v1.1.5.md
[1.1.0]: docs/releases/v1.1.0.md
[1.0.5]: docs/releases/v1.0.5.md
[1.0.0]: docs/releases/v1.0.0.md
