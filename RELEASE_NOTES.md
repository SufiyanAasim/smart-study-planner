# Smart Study Planner — Release Notes

User-facing highlights for each release. For the full, categorized change history
see the [Changelog](CHANGELOG.md). For a complete walkthrough of every screen and
feature, see [About](About.md).

---

## 🚀 Version 2.0.0 — "Polish & Motion"
*Released 2026-06-26*

Version 2.0 turns a feature-complete planner into a polished, modern desktop
experience. Everything from v1.0.0 still works — this release is about how the app
**looks, sounds, and feels**, plus a set of important reliability fixes.

### ✨ What's new
- **Living, animated backgrounds.** The login/registration/recovery screens, the
  Focus Timer, and the Credits page now drift with a subtle, theme-aware
  particle-constellation effect. It's lightweight, pauses when off-screen, and
  uses no extra image files. Data-heavy screens stay clean and readable.
- **Real sound design.** Custom-made audio cues for clicks, success, errors, and
  timer completion replace the old system beeps — and you can switch all sounds
  on or off from **Settings → Sound & Feedback**.
- **Playable ambient soundscapes.** The Focus Timer's soundscapes are now real
  looping audio with **Play/Pause** and a **Volume** slider, and the wave
  visualizer moves with the sound.
- **Quick sign-in.** Pick a registered account from the login screen with one click.
- **Two more languages: Arabic (العربية) and Persian (فارسی).** The interface is
  now fully translated into **12 languages**, including right-to-left scripts.
- **Faster sign-in.** Your last username/email is remembered and pre-filled on the
  login screen, with the cursor ready in the password box.
- **Safer exit.** Closing the app now asks for confirmation first, so you never
  lose a session by accident.
- **Friendlier empty screens.** The Tasks, Insights, and Timetable screens now show
  helpful guidance when there's nothing to display yet, instead of a blank area.
- **A refreshed Credits screen** and **cleaner, aligned controls** — a proper
  language dropdown and an enhanced Light/Dark toggle throughout.

### 🛠️ Fixes that matter
- The **Focus Timer** is no longer blank — the full timer, modes, soundscape
  picker, and controls render correctly.
- Switching the **theme on the Register/Recovery screen** no longer kicks you back
  to login or erases what you typed — your screen and form data are preserved.
- Eliminated background errors that could occur when switching themes or logging
  out mid-animation.

### ✅ Quality
Every module compiles cleanly, the automated test suite passes, and all 12
languages were exercised across every screen with no runtime errors.

---

## 🎓 Version 1.0.0 — "Foundation"
*Released 2026-06-25*

The first release: a secure, complete, dual-interface academic planner for
university students — available as both a terminal (CLI) app and a desktop (GUI)
application sharing one database.

### Highlights
- **Two ways to work:** a guided command-line interface and a modern Tkinter
  desktop dashboard, backed by the same SQLite database.
- **Secure by design:** PBKDF2-HMAC-SHA-256 password hashing, strict per-user data
  isolation, and a security-question password-recovery flow.
- **Complete task management:** create, edit, complete, and delete tasks with
  priority, category, deadline, and status — plus search, filtering, and sorting.
- **Visual insights:** a completion donut, priority and category charts, and a
  5-day study-load graph.
- **Study tools:** a Pomodoro Focus Timer with ambient soundscapes, a local
  study assistant, and collaborative study groups.
- **Stay in sync:** export your timetable to a standard `.ics` calendar file and
  your tasks to CSV.
- **Your language:** a localized interface in 10 languages.

---

*Developed by **Mohammad Sufiyan Aasim** — [sufiyanaasim@outlook.com](mailto:sufiyanaasim@outlook.com) · GitHub [msufiyanpk](https://github.com/msufiyanpk). Licensed under the [MIT License](LICENSE).*
