"""
logic.py
TaskManager controller class. This acts as the backend logic engine,
managing the task list in-memory and saving/loading from database & JSON.
Author: Mohammad Sufiyan Aasim (SufiyanAasim)
"""

import json
import os
from database import DatabaseManager
from models import Task, PRIORITY_LEVELS


class TaskManager:
    """Manages our collection of study tasks and handles database and backup JSON operations."""

    def __init__(self, data_file_base, db_file=None, user_id=None):
        self.db_file = db_file
        self.user_id = user_id
        self.db = DatabaseManager(db_file) if db_file else None

        # User isolation: Use user-specific backup JSON path
        if user_id is not None:
            dir_name = os.path.dirname(data_file_base)
            base_name = os.path.basename(data_file_base)
            name_part, ext_part = os.path.splitext(base_name)
            self.data_file = os.path.join(
                dir_name, f"{name_part}_user_{user_id}{ext_part}")
        else:
            self.data_file = data_file_base

        self.tasks = []
        self._next_id = 1

    def add_task(self, title, priority, deadline, description="", category="Study"):
        """Creates a new Task object with an auto-incremented ID and adds it to our list."""
        task = Task(
            task_id=self._next_id,
            title=title,
            priority=priority,
            deadline=deadline,
            description=description,
            category=category
        )
        self.tasks.append(task)
        self._next_id += 1
        return task

    def find_by_id(self, task_id):
        """Searches the task list by ID. Returns None if the task doesn't exist."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(self, task_id, title=None, priority=None, deadline=None, description=None, category=None):
        """Modifies specific fields of a task if they are provided."""
        task = self.find_by_id(task_id)
        if task is None:
            return False
        if title is not None:
            task.title = title
        if priority is not None:
            task.priority = priority
        if deadline is not None:
            task.deadline = deadline
        if description is not None:
            task.description = description
        if category is not None:
            task.category = category
        return True

    def delete_task(self, task_id):
        """Removes a task from the planner by its ID."""
        task = self.find_by_id(task_id)
        if task is None:
            return False
        self.tasks.remove(task)
        return True

    def complete_task(self, task_id):
        """Finds a task by ID and sets its status to Completed."""
        task = self.find_by_id(task_id)
        if task is None:
            return False
        task.mark_completed()
        return True

    def get_all(self):
        """Returns a copy of the entire task list."""
        return list(self.tasks)

    def filter_by_status(self, completed):
        """Filters tasks: True returns completed tasks, False returns pending ones."""
        return [task for task in self.tasks if task.is_completed() == completed]

    def filter_by_priority(self, priority):
        """Gets tasks that match the selected priority level (High, Medium, Low)."""
        return [task for task in self.tasks if task.priority == priority]

    def filter_by_category(self, category):
        """Gets tasks that match the selected category (case-insensitive)."""
        return [task for task in self.tasks if task.category.strip().lower() == category.strip().lower()]

    def search_by_keyword(self, keyword):
        """Performs a case-insensitive search on task titles and descriptions."""
        keyword = keyword.lower()
        return [
            task for task in self.tasks
            if keyword in task.title.lower() or keyword in task.description.lower()
        ]

    def sorted_by_deadline(self):
        """Sorts our task list based on deadline dates."""
        return sorted(self.tasks, key=lambda task: task.deadline)

    def sorted_by_priority(self):
        """Sorts tasks from High to Medium to Low priority using custom mapping."""
        order = {level: index for index, level in enumerate(PRIORITY_LEVELS)}
        return sorted(self.tasks, key=lambda task: order[task.priority])

    def sorted_by_title(self):
        """Sorts task list alphabetically by title."""
        return sorted(self.tasks, key=lambda task: task.title.lower())

    def sorted_by_category(self):
        """Sorts task list alphabetically by category."""
        return sorted(self.tasks, key=lambda task: task.category.lower())

    def get_overdue(self):
        """Retrieves all pending tasks whose deadline has already passed."""
        return [task for task in self.tasks if task.is_overdue()]

    def get_summary(self):
        """Calculates counts and percentages for our dashboard stats."""
        total = len(self.tasks)
        completed = len(self.filter_by_status(True))
        pending = total - completed
        overdue = len(self.get_overdue())
        by_priority = {}
        for level in PRIORITY_LEVELS:
            by_priority[level] = len(self.filter_by_priority(level))
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue,
            "by_priority": by_priority,
        }

    def _load_from_json(self):
        """Loads tasks from the backup JSON file when present."""
        if not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, "r", encoding="utf-8") as file_object:
                raw_tasks = json.load(file_object)
        except (json.JSONDecodeError, OSError):
            print("  ! Warning: could not read the saved data file. Starting empty.")
            return False

        if not isinstance(raw_tasks, list):
            print("  ! Warning: saved data file is not a list. Starting empty.")
            return False

        loaded_tasks = []
        for item in raw_tasks:
            if not isinstance(item, dict):
                continue
            try:
                loaded_tasks.append(Task.from_dict(item))
            except (KeyError, ValueError, TypeError):
                continue

        self.tasks = loaded_tasks
        if self.tasks:
            self._next_id = max(t.task_id for t in self.tasks) + 1
        return True

    def save(self):
        """Saves all current tasks to the database and backup JSON (strictly isolated)."""
        if self.user_id is None:
            return  # Authenticated user is required for database operations

        # Write to JSON backup
        folder = os.path.dirname(self.data_file)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        try:
            with open(self.data_file, "w", encoding="utf-8") as file_object:
                json.dump([task.to_dict()
                          for task in self.tasks], file_object, indent=4)
        except OSError:
            pass  # Fail-safe backup saving

        # Write to primary SQLite database
        if self.db is not None:
            self.db.save_tasks(self.user_id, self.tasks)

    def load(self):
        """Loads tasks from the database (strictly isolated); falls back to JSON backup if empty."""
        if self.user_id is None:
            return False

        if self.db is not None:
            db_tasks = self.db.load_tasks(self.user_id)
            if db_tasks:
                self.tasks = [
                    Task(
                        task_id=item["task_id"],
                        title=item["title"],
                        description=item["description"],
                        priority=item["priority"],
                        category=item["category"],
                        deadline=item["deadline"],
                        status=item["status"],
                        created_at=item["created_at"],
                    )
                    for item in db_tasks
                ]
                self._next_id = max(
                    (task.task_id for task in self.tasks), default=0) + 1
                return True

        # Fallback to user-specific JSON backup
        loaded = self._load_from_json()
        if loaded and self.db is not None:
            # Sync JSON backup tasks to database
            self.db.save_tasks(self.user_id, self.tasks)
        return loaded
