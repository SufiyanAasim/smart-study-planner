# Changelog

All notable changes to the **Smart Study Planner** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] — "Polish & Motion" — 2026-06-26

The second release is a UX, stability, and presentation overhaul. It keeps every
v1.0.0 capability intact while making the application feel modern, alive, and
production-ready.

### Added
- **Animated interactive backgrounds.** A new performant, theme-aware
  `ParticleCanvas` renders a drifting particle-constellation behind the
  authentication screens (over the branding image), the Focus Timer, and the
  Credits screen. The loop is capped (~25 fps), pauses when its screen is hidden,
  and self-terminates on widget destruction — no extra image assets required.
- **Bespoke sound design.** Custom-synthesized audio cues (`click`, `success`,
  `error`, `notify`) generated into `assets/sounds/`, replacing raw system beeps.
  Each helper falls back gracefully to a system alias if a file is unavailable.
- **Sound enable/disable toggle.** A new *Sound & Feedback* card in
  **Settings** turns interface audio on or off; the choice persists across runs.
- **Faster sign-in.** The last identifier used on the machine is remembered and
  prefilled on the login screen (stored in `data/app_prefs.json`), with focus
  moved straight to the password field.
- **Exit confirmation.** Closing via the window's X button or an in-app Exit
  button now asks for confirmation first, preventing accidental shutdowns.
- **Empty states.** Dedicated, translated empty-state messaging for the Tasks
  workspace ("No tasks yet" vs. "No matching tasks"), the Insights dashboard, and
  the Study Timetable.
- **Redesigned Developer Credits screen.** Centered card sourced from the README:
  app name, tagline, author, email, GitHub, and license.
- **Two new languages — Arabic (العربية) and Persian (فارسی)** — bringing the
  total to **12 fully translated languages**, including right-to-left scripts.
- **Full localization of new strings** across all supported languages.
- **Playable ambient soundscapes.** The Focus Timer's soundscapes (Lo-Fi, Rain,
  White Noise, Ocean, Fireplace) are now real, seamlessly-looping audio with a
  **Play/Pause** button and a **Volume** slider; the visualizer reacts to live
  playback. (Bundled, synthesized loops in `assets/sounds/`.)
- **Registered-accounts quick-pick on the login screen.** Click an account chip to
  prefill the identifier and jump to the password field.
- **Exit button in the dashboard sidebar**, directly beneath Log Out (confirmed).
- **Update Profile card** in Profile Settings — edit Full Name, Username, and Email
  (with validation and uniqueness checks); the sidebar refreshes instantly.
- **Study group deletion** — selecting a group reveals a Delete button (hidden
  otherwise) that removes the group, its members, and its shared tasks.
- **Application icon** (`assets/icon.ico`) applied to the window, taskbar, and the
  packaged executable (`--icon`).
- **Eye (show/hide) toggles** on the New / Confirm password fields in Settings.

### Changed
- **Language selector** is now a properly themed, aligned dropdown
  (`ttk.Combobox`) on both the authentication screens and Settings, replacing the
  previous ad-hoc menu button.
- **Light/Dark theme toggle** is an enhanced, accent-bordered pill control,
  consistently aligned with the language dropdown across all auth screens.
- **Theme switching now preserves navigation state and form data** — toggling the
  theme keeps you on the current screen (and keeps typed input) instead of
  rebuilding back to the login view or the default tab.
- **Timer completion** now plays the bespoke `notify` chime instead of a raw
  `MessageBeep`.
- **Authentication background** now uses the same theme-aware gradient
  particle-constellation as the Focus Timer (no static image), so it adapts
  cleanly to light and dark themes.
- **Removed the redundant back arrow** on the Register screen (the "Back to Login"
  link already covers it); the Recovery screen now relies on its top back arrow
  instead of a clipped bottom link.
- **Usernames are now always stored lowercase** (enforced live as you type and at
  the database layer) — no mixed/sentence case.
- **Sidebar button colours**: Log Out is amber and Exit is red, so the two are
  clearly distinguishable.
- **Aligned the Profile and Password cards** in Settings — fields and Save buttons
  now line up on a shared label column.

### Fixed
- **Focus Timer rendered blank.** The timer card was centered with `place()`
  against the panel's initial 1×1 size, pushing it off-screen. Switched to
  grid-centering so the entire timer UI (clock, mode buttons, soundscape dropdown,
  Start/Reset) renders reliably.
- **Register screen "theme bounce".** Toggling the theme on the Register or
  Recovery screen reset the user back to the Login view and discarded entered
  data. State is now captured and restored across the rebuild.
- **Latent `TclError` crashes.** The Study Assistant typewriter animation and the timer audio
  visualizer rescheduled `after()` callbacks that could fire against destroyed
  widgets during theme switches or logout. Both now guard on `winfo_exists()`.
- **Calendar (.ics) export crash.** The exporter treated each task's `deadline` as
  a string, but it is a `date` object — so exporting always raised a `TypeError`.
  It now formats `date` objects directly (with a string fallback).
- **Invisible active sidebar tab in light mode.** The hover handler reset a
  button's background to its creation-time colour, clobbering the active-tab
  highlight (white-on-white). Resting colours are now mutable so the highlight
  survives hover.
- **Insights dashboard looked empty with no data.** Instead of a blank overlay,
  the four charts now always render their headings and default 0 values.
- **Sound effects could fail to play** when the app was launched from another
  directory — asset paths now anchor to the project root, not the working dir.

### Documentation
- Consolidated the documentation set to **README**, **About** (full project
  description), **CHANGELOG**, and **RELEASE_NOTES**, plus **LICENSE**. Removed the
  legacy report draft and the `Course Work/` folder.
- Updated the license to the MIT License © 2026 Mohammad Sufiyan Aasim.

### Verification
- All modules compile; the unit/integration test suite passes (5/5).
- Dark and light themes verified by screenshot across the updated screens.
- All 12 languages exercised across every panel with no runtime errors.

---

## [1.0.0] — "Foundation" — 2026-06-25

The initial release: a complete, secure, dual-interface academic planner.

### Added
- **Unified launch orchestrator** (`main.py`) offering CLI mode, GUI mode, or exit.
- **Relational SQLite backend** with `users` and `tasks` tables and strict
  per-user data isolation, plus user-specific JSON backups.
- **Comprehensive security model:** PBKDF2-HMAC-SHA-256 password and
  security-answer hashing (100k iterations, random salts), email/password/full-name
  validation, and a security-question password recovery workflow.
- **Rich task management (CRUD)** with title, description, priority, category,
  deadline, and status, plus a query engine (search, status/priority/category
  filters, multi-key sorting).
- **Interactive dashboards:** CLI text stats and GUI canvas visualizations
  (completion donut, priority bar chart, category bar chart, 5-day load line graph).
- **Focus Pomodoro Timer** with work/break modes, ambient soundscape selection,
  and an animated audio-wave visualizer.
- **Local Study Assistant** with quick prompts and a typewriter streaming effect.
- **Calendar export** to RFC-compliant, timezone-safe `.ics` files.
- **Collaborative Study Groups** backed by relational tables, with a demo group,
  member management, joint tasks, and scheduled sessions.
- **Modern slate GUI** with Light/Dark theming, password visibility toggles, and a
  responsive sidebar dashboard.
- **10-language localization:** English, German, Spanish, French, Russian, Chinese,
  Japanese, Korean, Hindi, and Urdu.
- **CSV export** and a study-summary report generator in Settings.
- **Automated test suite** covering hashing, registration, user isolation, and
  task statistics.

---

[2.0.0]: #200--polish--motion--2026-06-26
[1.0.0]: #100--foundation--2026-06-25
