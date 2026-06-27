import os
import sqlite3
from datetime import date, datetime, timedelta
import utils


class DatabaseManager:
    """SQLite-backed store for users and tasks with secure hashing and user isolation."""

    def __init__(self, db_file):
        self.db_file = db_file
        self._initialize()

    def _initialize(self):
        folder = os.path.dirname(self.db_file)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        
        conn = sqlite3.connect(self.db_file)
        try:
            # Check if columns are already updated. If users exists but has no 'email', it's the old schema.
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                info_cursor = conn.execute("PRAGMA table_info(users)")
                columns = [row[1] for row in info_cursor.fetchall()]
                if "email" not in columns:
                    # Drop tables to recreate with new schema
                    conn.execute("DROP TABLE IF EXISTS tasks")
                    conn.execute("DROP TABLE IF EXISTS users")
                    conn.commit()
                elif "language" not in columns:
                    conn.execute("ALTER TABLE users ADD COLUMN language TEXT NOT NULL DEFAULT 'en'")
                    conn.commit()

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    username TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    security_question TEXT NOT NULL,
                    security_answer_hash TEXT NOT NULL,
                    security_answer_salt TEXT NOT NULL,
                    language TEXT NOT NULL DEFAULT 'en',
                    created_at TEXT NOT NULL DEFAULT CURRENT_DATE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    category TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS study_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    creator_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_DATE,
                    FOREIGN KEY(creator_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS group_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY(group_id) REFERENCES study_groups(id),
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    UNIQUE(group_id, user_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS group_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    category TEXT NOT NULL,
                    deadline TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Pending',
                    created_at TEXT NOT NULL DEFAULT CURRENT_DATE,
                    FOREIGN KEY(group_id) REFERENCES study_groups(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scratchpads (
                    user_id INTEGER PRIMARY KEY,
                    content TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def check_duplicate_email(self, email):
        """Returns True if the email already exists in the database."""
        conn = sqlite3.connect(self.db_file)
        try:
            row = conn.execute("SELECT 1 FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
        finally:
            conn.close()
        return row is not None

    def check_duplicate_username(self, username):
        """Returns True if the username already exists in the database."""
        if not username:
            return False
        conn = sqlite3.connect(self.db_file)
        try:
            row = conn.execute("SELECT 1 FROM users WHERE LOWER(username) = LOWER(?)", (username.strip(),)).fetchone()
        finally:
            conn.close()
        return row is not None

    def register_user(self, full_name, email, username, password, security_question, security_answer):
        """Create a new user with secure password/answer hashing and return the user as a dict."""
        email_clean = email.strip()
        # Usernames are always stored lowercase (no mixed/sentence case).
        username_clean = username.strip().lower() if username and username.strip() else None
        full_name_clean = full_name.strip()
        
        # Unique constraints checks
        if self.check_duplicate_email(email_clean):
            raise ValueError("Email is already registered.")
        if username_clean and self.check_duplicate_username(username_clean):
            raise ValueError("Username is already taken.")

        # Hashing password
        salt, password_hash = utils.hash_password(password)

        # Hashing security answer (case-insensitive checking)
        sec_answer_clean = security_answer.strip().lower()
        sec_salt, sec_hash = utils.hash_password(sec_answer_clean)

        conn = sqlite3.connect(self.db_file)
        try:
            cursor = conn.execute(
                """
                INSERT INTO users (
                    full_name, email, username, password_hash, salt, 
                    security_question, security_answer_hash, security_answer_salt
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    full_name_clean,
                    email_clean,
                    username_clean,
                    password_hash,
                    salt,
                    security_question.strip(),
                    sec_hash,
                    sec_salt
                )
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            row = conn.execute(
                "SELECT id, full_name, email, username, created_at, language FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        finally:
            conn.close()

        return {
            "id": row[0],
            "full_name": row[1],
            "email": row[2],
            "username": row[3],
            "created_at": row[4],
            "language": row[5],
        }

    def update_user_profile(self, user_id, full_name, email, username):
        """Update a user's name, email, and (lowercase) username. Validates that the
        new email/username are not already used by a different account."""
        email_clean = email.strip()
        username_clean = username.strip().lower() if username and username.strip() else None
        full_name_clean = full_name.strip()

        conn = sqlite3.connect(self.db_file)
        try:
            dup_email = conn.execute(
                "SELECT 1 FROM users WHERE LOWER(email) = LOWER(?) AND id != ?",
                (email_clean, user_id),
            ).fetchone()
            if dup_email:
                raise ValueError("That email is already used by another account.")
            if username_clean:
                dup_user = conn.execute(
                    "SELECT 1 FROM users WHERE LOWER(username) = LOWER(?) AND id != ?",
                    (username_clean, user_id),
                ).fetchone()
                if dup_user:
                    raise ValueError("That username is already taken.")
            conn.execute(
                "UPDATE users SET full_name = ?, email = ?, username = ? WHERE id = ?",
                (full_name_clean, email_clean, username_clean, user_id),
            )
            conn.commit()
            row = conn.execute(
                "SELECT id, full_name, email, username, created_at, language FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        finally:
            conn.close()
        return {
            "id": row[0], "full_name": row[1], "email": row[2],
            "username": row[3], "created_at": row[4], "language": row[5],
        }

    def authenticate_user(self, login_credential, password):
        """Authenticate user by username or email. Return user dict on success, None otherwise."""
        cred = login_credential.strip()
        conn = sqlite3.connect(self.db_file)
        try:
            row = conn.execute(
                """
                SELECT id, full_name, email, username, password_hash, salt, created_at, language 
                FROM users 
                WHERE LOWER(email) = LOWER(?) OR LOWER(username) = LOWER(?)
                """,
                (cred, cred),
            ).fetchone()
        finally:
            conn.close()
            
        if not row:
            return None

        user_id, full_name, email, username, stored_hash, salt, created_at, language = row
        
        # Verify password
        _, input_hash = utils.hash_password(password, salt)
        if input_hash != stored_hash:
            return None

        return {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "username": username,
            "created_at": created_at,
            "language": language,
        }

    def list_users(self, limit=8):
        """Return registered accounts (most recent first) for quick login selection."""
        conn = sqlite3.connect(self.db_file)
        try:
            rows = conn.execute(
                """
                SELECT full_name, username, email
                FROM users
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        finally:
            conn.close()
        return [{"full_name": r[0], "username": r[1], "email": r[2]} for r in rows]

    def get_security_question(self, email):
        """Get security question for a given email address."""
        conn = sqlite3.connect(self.db_file)
        try:
            row = conn.execute("SELECT security_question FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
        finally:
            conn.close()
        return row[0] if row else None

    def reset_password(self, email, security_question, security_answer, new_password):
        """Verify the security question & answer for the given email, and update the password."""
        email_clean = email.strip()
        sec_answer_clean = security_answer.strip().lower()

        conn = sqlite3.connect(self.db_file)
        try:
            row = conn.execute(
                """
                SELECT id, security_question, security_answer_hash, security_answer_salt 
                FROM users 
                WHERE LOWER(email) = LOWER(?)
                """,
                (email_clean,),
            ).fetchone()

            if not row:
                raise ValueError("No account found with that email address.")

            user_id, stored_question, stored_sec_hash, stored_sec_salt = row

            if stored_question.strip().lower() != security_question.strip().lower():
                raise ValueError("Security question does not match.")

            # Verify security answer
            _, input_sec_hash = utils.hash_password(sec_answer_clean, stored_sec_salt)
            if input_sec_hash != stored_sec_hash:
                raise ValueError("Incorrect security answer.")

            # Hashing new password
            new_salt, new_password_hash = utils.hash_password(new_password)

            conn.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (new_password_hash, new_salt, user_id),
            )
            conn.commit()
        finally:
            conn.close()
        return True

    def change_password(self, user_id, new_password):
        """Update a logged-in user's password using secure hashing."""
        new_salt, new_password_hash = utils.hash_password(new_password)
        conn = sqlite3.connect(self.db_file)
        try:
            conn.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (new_password_hash, new_salt, user_id)
            )
            conn.commit()
        finally:
            conn.close()
        return True

    def save_tasks(self, user_id, tasks):
        """Replace all tasks for a user in the database (strictly isolated)."""
        conn = sqlite3.connect(self.db_file)
        try:
            conn.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
            for task in tasks:
                conn.execute(
                    """
                    INSERT INTO tasks (user_id, task_id, title, description, priority, category, deadline, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        task.task_id,
                        task.title,
                        task.description,
                        task.priority,
                        task.category,
                        task.deadline.strftime("%Y-%m-%d"),
                        task.status,
                        task.created_at.strftime("%Y-%m-%d"),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    def load_tasks(self, user_id):
        """Load all tasks for a specific user from the database (strictly isolated)."""
        conn = sqlite3.connect(self.db_file)
        try:
            rows = conn.execute(
                """
                SELECT task_id, title, description, priority, category, deadline, status, created_at 
                FROM tasks 
                WHERE user_id = ? 
                ORDER BY task_id
                """,
                (user_id,),
            ).fetchall()
        finally:
            conn.close()
            
        tasks = []
        for row in rows:
            task_id, title, description, priority, category, deadline, status, created_at = row
            tasks.append(
                {
                    "task_id": task_id,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "category": category,
                    "deadline": datetime.strptime(deadline, "%Y-%m-%d").date(),
                    "status": status,
                    "created_at": datetime.strptime(created_at, "%Y-%m-%d").date(),
                }
            )
        return tasks

    def change_language(self, user_id, language):
        """Update a user's interface language preference in the database."""
        conn = sqlite3.connect(self.db_file)
        try:
            conn.execute("UPDATE users SET language = ? WHERE id = ?", (language, user_id))
            conn.commit()
        finally:
            conn.close()
        return True

    def create_study_group(self, group_name, creator_id):
        conn = sqlite3.connect(self.db_file)
        try:
            cursor = conn.execute(
                "INSERT INTO study_groups (name, creator_id) VALUES (?, ?)",
                (group_name.strip(), creator_id)
            )
            group_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, creator_id)
            )
            conn.commit()
        finally:
            conn.close()
        return group_id

    def delete_study_group(self, group_id, user_id):
        """Delete a study group (and its members + tasks). Only a member of the
        group may delete it, preserving user isolation."""
        conn = sqlite3.connect(self.db_file)
        try:
            member = conn.execute(
                "SELECT 1 FROM group_members WHERE group_id = ? AND user_id = ?",
                (group_id, user_id),
            ).fetchone()
            if not member:
                raise ValueError("You can only delete groups you belong to.")
            conn.execute("DELETE FROM group_tasks WHERE group_id = ?", (group_id,))
            conn.execute("DELETE FROM group_members WHERE group_id = ?", (group_id,))
            conn.execute("DELETE FROM study_groups WHERE id = ?", (group_id,))
            conn.commit()
        finally:
            conn.close()
        return True

    def add_group_member_by_email(self, group_id, email):
        conn = sqlite3.connect(self.db_file)
        try:
            user = conn.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),)).fetchone()
            if not user:
                raise ValueError("No registered user found with that email address.")
            user_id = user[0]
            conn.execute(
                "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, user_id)
            )
            conn.commit()
        finally:
            conn.close()
        return True

    def get_user_groups(self, user_id):
        conn = sqlite3.connect(self.db_file)
        try:
            rows = conn.execute(
                """
                SELECT g.id, g.name, g.creator_id, g.created_at
                FROM study_groups g
                JOIN group_members m ON g.id = m.group_id
                WHERE m.user_id = ?
                """,
                (user_id,)
            ).fetchall()
        finally:
            conn.close()
        return [{"id": r[0], "name": r[1], "creator_id": r[2], "created_at": r[3]} for r in rows]

    def get_group_members(self, group_id):
        conn = sqlite3.connect(self.db_file)
        try:
            rows = conn.execute(
                """
                SELECT u.full_name, u.email
                FROM users u
                JOIN group_members m ON u.id = m.user_id
                WHERE m.group_id = ?
                """,
                (group_id,)
            ).fetchall()
        finally:
            conn.close()
        return [{"full_name": r[0], "email": r[1]} for r in rows]

    def get_group_tasks(self, group_id):
        conn = sqlite3.connect(self.db_file)
        try:
            rows = conn.execute(
                """
                SELECT id, title, description, priority, category, deadline, status, created_at
                FROM group_tasks
                WHERE group_id = ?
                ORDER BY deadline ASC
                """,
                (group_id,)
            ).fetchall()
        finally:
            conn.close()
        return [
            {
                "id": r[0],
                "title": r[1],
                "description": r[2],
                "priority": r[3],
                "category": r[4],
                "deadline": datetime.strptime(r[5], "%Y-%m-%d").date(),
                "status": r[6],
                "created_at": datetime.strptime(r[7], "%Y-%m-%d").date()
            } for r in rows
        ]

    def add_group_task(self, group_id, title, priority, deadline, category, description=""):
        conn = sqlite3.connect(self.db_file)
        try:
            conn.execute(
                """
                INSERT INTO group_tasks (group_id, title, description, priority, category, deadline)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (group_id, title.strip(), description.strip(), priority, category, deadline)
            )
            conn.commit()
        finally:
            conn.close()
        return True

    def create_demo_groups_for_user_if_none(self, user_id):
        conn = sqlite3.connect(self.db_file)
        try:
            # Check if user has any groups
            cursor = conn.execute("SELECT 1 FROM group_members WHERE user_id = ?", (user_id,))
            if cursor.fetchone():
                return
            
            # Create "Global Study Circle"
            cursor = conn.execute(
                "INSERT INTO study_groups (name, creator_id) VALUES (?, ?)",
                ("Global Study Circle", user_id)
            )
            group_id = cursor.lastrowid
            
            # Add user as member
            conn.execute(
                "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)",
                (group_id, user_id)
            )
            
            # Add some group tasks
            group_tasks = [
                ("Physics Exam Study Session", "Prepare review sheets for chapters 4-6", "High", "Exam", (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")),
                ("Group Essay Feedback", "Review introductory thesis drafts together", "Medium", "Study", (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")),
                ("Programming Assignment Lab", "Debug memory leak in group code repository", "High", "Project", (date.today() + timedelta(days=7)).strftime("%Y-%m-%d"))
            ]
            for title, desc, priority, category, deadline in group_tasks:
                conn.execute(
                    """
                    INSERT INTO group_tasks (group_id, title, description, priority, category, deadline)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (group_id, title, desc, priority, category, deadline)
                )
            conn.commit()
        finally:
            conn.close()

    def get_scratchpad(self, user_id):
        """Load scratchpad content for a specific user."""
        conn = sqlite3.connect(self.db_file)
        try:
            row = conn.execute("SELECT content FROM scratchpads WHERE user_id = ?", (user_id,)).fetchone()
        finally:
            conn.close()
        return row[0] if row else ""

    def save_scratchpad(self, user_id, content):
        """Save/update scratchpad content for a specific user."""
        conn = sqlite3.connect(self.db_file)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO scratchpads (user_id, content) VALUES (?, ?)",
                (user_id, content)
            )
            conn.commit()
        finally:
            conn.close()
        return True
