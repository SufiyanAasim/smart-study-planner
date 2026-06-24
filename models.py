"""
models.py
This file defines our core Task data class. It handles representing a single 
study task (like physics lab, essays, etc.) and serialization/deserialization 
for saving it.
Author: Mohammad Sufiyan Aasim (msufiyanpk)
"""

from datetime import date, datetime

# Global settings for priority tags, statuses, and uniform calendar date format
PRIORITY_LEVELS = ("High", "Medium", "Low")
STATUS_PENDING = "Pending"
STATUS_COMPLETED = "Completed"
DATE_FORMAT = "%Y-%m-%d"


class Task:
    """Represents a single academic study task or course milestone."""

    def __init__(self, task_id, title, priority, deadline,
                 description="", category="Study",
                 status=STATUS_PENDING, created_at=None):
        # Unique task ID tracker
        self.task_id = task_id
        # Descriptive task name
        self.title = title
        # Extra details about the task
        self.description = description if description is not None else ""
        # Priority level: High, Medium, or Low
        self.priority = priority
        # Task category (e.g. Study, Assignment, Exam, Project, Lab, etc.)
        self.category = category if category is not None else "Study"
        # Calendar deadline (stored as a date object)
        self.deadline = deadline
        # Current status: Pending or Completed
        self.status = status
        # Creation timestamp (defaults to today if not provided)
        self.created_at = created_at if created_at is not None else date.today()

    def mark_completed(self):
        """Updates the task status to completed."""
        self.status = STATUS_COMPLETED

    def is_completed(self):
        """Checks if the task status is set to Completed."""
        return self.status == STATUS_COMPLETED

    def is_overdue(self):
        """Determines if the task is pending and its deadline date has already passed."""
        return (not self.is_completed()) and (self.deadline < date.today())

    def days_left(self):
        """Calculates how many days are left until the deadline (returns negative if overdue)."""
        return (self.deadline - date.today()).days

    def to_dict(self):
        """Converts task attributes into a dictionary so we can save it to JSON."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "category": self.category,
            "deadline": self.deadline.strftime(DATE_FORMAT),
            "status": self.status,
            "created_at": self.created_at.strftime(DATE_FORMAT),
        }

    @classmethod
    def from_dict(cls, data):
        """Loads data from a saved dictionary to reconstruct a Task object."""
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data["priority"],
            category=data.get("category", "Study"),
            deadline=datetime.strptime(data["deadline"], DATE_FORMAT).date(),
            status=data["status"],
            created_at=datetime.strptime(data["created_at"], DATE_FORMAT).date(),
        )
