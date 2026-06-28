# Architecture

## Overview

Smart Study Planner follows a layered desktop architecture with a clear separation between the data layer, business logic, and presentation layer. The CLI and GUI share the same backend — one database, one logic controller.

```
┌──────────────────────────────────────────────┐
│                  Entry Point                 │
│                   main.py                    │
│         (CLI interface + launcher)           │
└────────────┬─────────────┬───────────────────┘
             │             │
     ┌───────▼──────┐ ┌───▼──────────────────┐
     │   CLI Mode   │ │      GUI Mode         │
     │  (main.py)   │ │     (src/gui.py)      │
     └───────┬──────┘ └───────────┬───────────┘
             │                    │
     ┌───────▼────────────────────▼───────────┐
     │            Business Logic              │
     │           src/logic.py                 │
     │          (TaskManager)                 │
     └───────────────────┬────────────────────┘
                         │
     ┌───────────────────▼────────────────────┐
     │             Data Layer                 │
     │          src/database.py               │
     │         (DatabaseManager)              │
     └───────────────────┬────────────────────┘
                         │
              ┌──────────▼──────────┐
              │    SQLite Database  │
              │   data/planner.db   │
              └─────────────────────┘
```

---

## Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `main.py` | Entry point. Parses CLI args, runs the terminal interface or launches GUI. |
| `src/gui.py` | All Tkinter UI panels, animated canvas, dialogs, and event handling. |
| `src/logic.py` | `TaskManager` — in-memory task list, CRUD operations, statistics, JSON backup. |
| `src/database.py` | `DatabaseManager` — SQLite schema, all queries, user auth, hashing. |
| `src/models.py` | `Task` dataclass, serialization/deserialization, constants. |
| `src/utils.py` | Validation helpers, audio playback, resource path resolution. |
| `src/lan.py` | `LANManager` — UDP broadcast discovery and room hosting for LAN study rooms. |
| `src/translations.py` | Centralized 12-language translation dictionary. |

---

## Database Schema

See [Database.md](Database.md) for the full schema.

---

## Authentication Flow

1. User submits credentials in the Login screen.
2. `DatabaseManager.login_user()` fetches the stored salt and hash for that identifier.
3. The submitted password is hashed with the stored salt using PBKDF2-HMAC-SHA-256.
4. If the digest matches, the user's record is returned and stored in the GUI session state.
5. All subsequent queries are scoped to that `user_id` — cross-user access is structurally impossible.

---

## LAN Study Rooms (v1.2.5)

`src/lan.py` — `LANManager`:
- UDP broadcast on port 50505 for peer/room discovery (no TCP required for v1.2.5).
- Host model: one user hosts a named study room; the beacon includes room name, host name, department, class, and section.
- Discovery: passive UDP listener strips stale rooms after 10 seconds of silence.
- All network I/O runs in daemon threads; UI updates are dispatched via `Tk.after()`.
- Department, class, section, and batch year are stored in the `users` table and shown in the sidebar, LAN room detail view, and study-room beacon.
