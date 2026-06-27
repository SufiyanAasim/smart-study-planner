# Database

Smart Study Planner uses a local **SQLite** database at `data/planner.db`, managed entirely by `src/database.py` (`DatabaseManager`).

---

## Tables

### `users`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment user identifier |
| `full_name` | TEXT | Display name |
| `username` | TEXT UNIQUE | Lowercase username |
| `email` | TEXT UNIQUE | Validated email address |
| `password_hash` | TEXT | PBKDF2-HMAC-SHA-256 digest |
| `password_salt` | TEXT | Cryptographically random salt (hex) |
| `security_question` | TEXT | Selected recovery question |
| `security_answer_hash` | TEXT | Hashed security answer |
| `security_answer_salt` | TEXT | Salt for the answer hash |
| `created_at` | TEXT | ISO timestamp |

### `tasks`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment task identifier |
| `user_id` | INTEGER FK → users | Owning user |
| `title` | TEXT | Task title |
| `description` | TEXT | Optional details |
| `priority` | TEXT | High / Medium / Low |
| `category` | TEXT | Study / Assignment / Exam / etc. |
| `deadline` | TEXT | ISO date string (YYYY-MM-DD) |
| `status` | TEXT | Pending / Completed / Overdue |
| `created_at` | TEXT | ISO timestamp |

### `study_groups`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Group identifier |
| `name` | TEXT | Group display name |
| `created_by` | INTEGER FK → users | Creator |
| `created_at` | TEXT | ISO timestamp |

### `group_members`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `group_id` | INTEGER FK → study_groups | |
| `user_id` | INTEGER FK → users | |

### `group_tasks`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `group_id` | INTEGER FK → study_groups | |
| `title` | TEXT | Shared task title |
| `assigned_to` | INTEGER FK → users | |
| `status` | TEXT | Pending / Completed |

### `group_sessions`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `group_id` | INTEGER FK → study_groups | |
| `scheduled_at` | TEXT | ISO datetime |
| `topic` | TEXT | Session topic |

### `scratchpads`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK → users | |
| `content` | TEXT | Note text (auto-saved) |
| `updated_at` | TEXT | ISO timestamp |

---

## Security

- **Passwords** and **security answers** are hashed with PBKDF2-HMAC-SHA-256 using unique, cryptographically random salts (100,000 iterations).
- Plaintext secrets are never written to disk.
- All queries are parameterized — no string interpolation, no SQL injection surface.
- Every query that reads or writes task/note data includes a `WHERE user_id = ?` clause. Cross-user data access is structurally impossible.

---

## Backup

On every task write, `TaskManager` also exports a per-user JSON snapshot to `data/tasks_user_{id}.json`. This is a lightweight backup, not a primary store.
