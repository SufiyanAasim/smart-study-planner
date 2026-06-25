# About the Smart Study Planner Interface

This document provides a comprehensive breakdown of the graphical user screens, layout regions, interactive components, keyboard shortcuts, and premium features of the Smart Study Planner desktop application.

> **Version 2.0.0 “Polish & Motion”.** See the [Changelog](CHANGELOG.md) for the full release history.

---

## 1. Window Geometry & Core Layout

The desktop application is configured with a default window size of **960×650 pixels** (minimum 920×600), built to run responsively on Windows, macOS, and Linux. The visual theme uses a modern, balanced **Slate Color Palette** supporting dynamic real-time Light/Dark mode toggling.

The user interface follows a single-window dashboard pattern divided into two principal layout containers:
- **Left Sidebar Navigation (width: 230px):** Handles profile status, main navigation tabs, theme switching, and secure logout.
- **Right Workspace Area (fluid/responsive):** Houses the active panel card container. A dynamic title and description header is displayed at the top of this area, updating instantly when switching tabs.

### Motion & Atmosphere
Selected "hero" screens — the authentication cards, the Focus Timer, and the Credits page — render an **animated particle-constellation background**: drifting nodes linked by faint connecting lines, drawn on a dedicated `ParticleCanvas`. It is theme-aware, capped for performance (~25 fps), pauses whenever its screen is not visible, and adds no extra image assets. Data-dense screens (Tasks, Insights, Settings, Timetable, Groups) intentionally keep a clean, static background for legibility.

### Audio Feedback
Interaction is reinforced by **bespoke, synthesized sound effects** bundled in `assets/sounds/` — a soft click, an ascending success chime, a gentle error tone, and a notification arpeggio for timer completion. If a sound file is missing, the app falls back to a Windows system alias. All effects can be toggled from **Settings → Sound & Feedback** and the preference persists between sessions.

---

## 2. Authentication Screens (Before Login)

The initial startup displays one of three centered authentication cards over the animated background, featuring an aligned top-right control bar.

### Shared Top-Right Control Bar
- **Language Dropdown:** a properly themed `ttk.Combobox` to set the interface language before logging in.
- **Theme Toggle:** an enhanced, accent-bordered pill button (`☀️ Light` / `🌙 Dark`) that switches palettes instantly **without losing the current screen or any typed input**.

### A. Login Card
- **Emblem Branding:** a transparent academic graduation-cap logo that blends into dark or light backgrounds.
- **Registered Accounts:** a quick-pick row of account chips — click one to prefill the identifier and jump to the password field.
- **Fields:**
  - *Username or Email* entry field — **prefilled with the last identifier used on this machine** for faster sign-in.
  - *Password* entry field with an **Eye Toggle Icon** to show/hide plain text (focus jumps here when the identifier is prefilled).
- **Actions:**
  - *Login* button (primary brand color; verifies credentials).
  - *Forgot Password?* hyperlink (routes to Password Recovery).
  - *Register Now* link (routes to Registration).
  - *Exit Application* button (asks for confirmation before quitting).

### B. Registration Card
- **Redesigned Unified Flow:** all required fields laid out cleanly without clipping or a scrollbar.
- **Fields:** Full Name, Username (optional), Email, Password & Confirm Password (strength-validated), Security Question dropdown, Security Answer (hashed on save).
- **Actions:** *Register Account* (creates the user and logs in), *Back to Login*, *Exit Application* (confirmed).

### C. Password Recovery Card
- **Step-by-step verification:** enter email → **Load Security Question** → answer the question, set and confirm a new password.
- **Actions:** *Reset Password* (compares the answer hash and resets the credential), *Back to Login*, *Exit Application* (confirmed).

---

## 3. Main Dashboard Screens (After Login)

After successful authentication, the interface displays the dual-column Workspace with 8 active sidebar tabs.

### I. Sidebar Navigation & Profile Header
- **Profile Area:** a 🎓 avatar, the student's full name, and registered email address.
- **Sidebar Tabs:** Tasks Workspace, Study Timetable, Focus Timer, Study Assistant, Study Groups, Insights Panel, Profile Settings, and Credits.
- **Theme Toggle:** re-instantiates the application with the opposite palette **while preserving the active tab**.
- **Log Out:** safe exit dialog, saving in-memory state to the database and JSON before routing back to Login.

---

## 4. Workspaces & Premium Dashboards (Right Pane)

### Panel 1: Tasks Workspace
- **Filters Bar (Top):** live search, Status combobox, Priority combobox, Sort-By dropdown, and a Clear button.
- **Main Treeview (Middle):** Task ID, Title, Category, Priority, Deadline, Status, and Days Left (with overdue/remaining badges).
- **Empty State:** when the table has no rows, a centered placeholder distinguishes **"No tasks yet"** (new workspace) from **"No matching tasks"** (filters too narrow).
- **Action Buttons Bar (Bottom):** Add New Task, Edit Selected, Complete Selected, Delete Selected (with a delete confirmation).

### Panel 2: Study Timetable
- **Action Bar (Top):** segment switches for Weekly Plan, Monthly Calendar, and 6-Month Schedule; **Generate Study Plan** (round-robin distribution); **Export Calendar (ICS)**.
- **Timetable Views (Middle):** scrollable canvas with day-by-day, weekly, and milestone cards.
- **Empty State:** a 🗓️ placeholder ("Nothing scheduled yet") guides the user to add active tasks first.

### Panel 3: Focus Timer
- **Large Digital Clock**, **Work Session (25 min) / Short Break (5 min)** modes.
- **Ambient Soundscapes:** a themed dropdown (Lo-Fi, Rainforest, White Noise, Ocean, Fireplace) with a **Play/Pause** button and a **Volume** slider — real seamlessly-looping audio. The **Canvas Audio Wave Visualizer** reacts to live playback. Soundscapes stop automatically when you leave the tab, log out, or exit.
- **Actions:** Start/Pause toggle and Reset. Session completion plays the bespoke `notify` chime.
- Rendered over the animated particle background.

### Panel 4: Study Assistant
- **Quick Action Prompts:** Explain Concept, Summarize Tasks, Practice Questions.
- **Chat Feed:** a scrollable log with tagged "User:" / "Assistant:" colors and a character-by-character typewriter streaming effect.
- **Entry Field (Bottom):** text box with a Send button for custom educational queries.

### Panel 5: Study Groups
- **Two-Column Split Dashboard:** a groups list (initialized with a "Global Study Circle" demo group) and a details pane with Members, Collaborative Tasks, and Scheduled Study Sessions cards.

### Panel 6: Insights Panel
- Four real-time analytical canvases: **Completion Rate Donut**, **Priority Load Bar Chart**, **Category Breakdown Bar Chart**, and **5-Day Study Load Line Graph**.
- **Empty State:** a 📊 placeholder ("No insights yet") appears until there is task data to chart.

### Panel 7: Profile Settings
- **Update Profile Card:** edit your **Full Name**, **Username** (forced lowercase, uniqueness-checked), and **Email** (validated, uniqueness-checked); Save Profile refreshes the sidebar instantly.
- **Change Password Card:** current, new, and confirm-new entries with strict validation. New/Confirm fields have eye (show/hide) toggles. Fields and buttons are aligned with the Update Profile card above.
- **Language Preference Card:** a themed dropdown updating the interface language in real time across **12 languages** (English, German, Spanish, French, Russian, Chinese, Japanese, Korean, Hindi, Urdu, Arabic, and Persian — including right-to-left scripts), keeping you on the Settings tab.
- **Sound & Feedback Card:** a checkbox to enable/disable interface sound effects (persisted).
- **Reports & Data Export Card:** *Export Tasks (CSV)* and *Generate Study Summary*.

### Panel 8: Credits Screen
- A centered card rendered over the animated background, displaying:
  - Application identity — **Smart Study Planner** and its tagline.
  - Developer — **Mohammad Sufiyan Aasim**, Lead Developer, UI Designer & System Architect.
  - Clickable email: **sufiyanaasim@outlook.com** (copies to clipboard with a success chime).
  - **View GitHub Profile** button (opens `https://github.com/msufiyanpk`).
  - Footer: **@msufiyanpk • MIT License**.

---

## 5. Keyboard Shortcuts

- `Control-n` : Add New Task (only active inside the Tasks Workspace).
- `Control-f` : Focus the Tasks Search field.
- `Control-l` : Log out safely (with a confirmation box).
- `Double-Click` / `Delete` / `Space` (on a selected task): edit, delete, or complete the task.

---

## 6. Credits & License

Developed by **Mohammad Sufiyan Aasim** — [sufiyanaasim@outlook.com](mailto:sufiyanaasim@outlook.com) · GitHub [msufiyanpk](https://github.com/msufiyanpk).
Licensed under the [MIT License](LICENSE) © 2026 Mohammad Sufiyan Aasim.
