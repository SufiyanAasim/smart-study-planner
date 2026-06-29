import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import DatabaseManager  # noqa: E402
from logic import TaskManager  # noqa: E402


class SmartStudyPlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "planner.db")
        self.data_file_base = os.path.join(self.temp_dir, "tasks.json")
        self.db = DatabaseManager(self.db_path)

        # Register two test users
        self.user_a = self.db.register_user(
            full_name="Alice Smith",
            email="alice@example.com",
            username="alice",
            password="Password123!",
            security_question="What is your favorite pet's name?",
            security_answer="Goldie"
        )
        self.user_b = self.db.register_user(
            full_name="Bob Jones",
            email="bob@example.com",
            username="bob",
            password="Password123!",
            security_question="What is your mother's maiden name?",
            security_answer="Miller"
        )

    def test_registration_duplicates(self):
        # Prevent duplicate email
        with self.assertRaises(ValueError):
            self.db.register_user(
                full_name="Alice Duplicate",
                email="alice@example.com",
                username="alice_dup",
                password="Password123!",
                security_question="What is your favorite pet's name?",
                security_answer="Goldie"
            )
        # Prevent duplicate username
        with self.assertRaises(ValueError):
            self.db.register_user(
                full_name="Bob Duplicate",
                email="bob_dup@example.com",
                username="bob",
                password="Password123!",
                security_question="What is your mother's maiden name?",
                security_answer="Miller"
            )

    def test_authentication(self):
        # Login by email
        auth1 = self.db.authenticate_user("alice@example.com", "Password123!")
        self.assertIsNotNone(auth1)
        self.assertEqual(auth1["full_name"], "Alice Smith")

        # Login by username
        auth2 = self.db.authenticate_user("bob", "Password123!")
        self.assertIsNotNone(auth2)
        self.assertEqual(auth2["full_name"], "Bob Jones")

        # Failed login
        auth3 = self.db.authenticate_user("alice", "WrongPassword")
        self.assertIsNone(auth3)

    def test_password_reset(self):
        # Forgot password recovery
        with self.assertRaises(ValueError):
            # Wrong answer
            self.db.reset_password(
                "alice@example.com", "What is your favorite pet's name?", "WrongAnswer", "NewPass123!")

        # Correct answer
        success = self.db.reset_password(
            "alice@example.com", "What is your favorite pet's name?", "Goldie", "NewPass123!")
        self.assertTrue(success)

        # Authenticate with new password
        auth = self.db.authenticate_user("alice", "NewPass123!")
        self.assertIsNotNone(auth)

    def test_user_isolation(self):
        # Alice manager
        mgr_a = TaskManager(self.data_file_base,
                            db_file=self.db_path, user_id=self.user_a["id"])
        mgr_a.load()
        mgr_a.add_task("Alice Physics Lab", "High", date(
            2026, 7, 1), "Lab work details", "Lab")
        mgr_a.save()

        # Bob manager (should start with empty tasks)
        mgr_b = TaskManager(self.data_file_base,
                            db_file=self.db_path, user_id=self.user_b["id"])
        mgr_b.load()
        self.assertEqual(len(mgr_b.get_all()), 0)

        # Bob adds their own task
        mgr_b.add_task("Bob Math Assignment", "Low", date(
            2026, 7, 2), "Exercise sheet 3", "Assignment")
        mgr_b.save()

        # Reload and check isolation
        reloaded_a = TaskManager(
            self.data_file_base, db_file=self.db_path, user_id=self.user_a["id"])
        reloaded_a.load()
        self.assertEqual(len(reloaded_a.get_all()), 1)
        self.assertEqual(reloaded_a.get_all()[0].title, "Alice Physics Lab")
        self.assertEqual(reloaded_a.get_all()[
                         0].description, "Lab work details")
        self.assertEqual(reloaded_a.get_all()[0].category, "Lab")

        reloaded_b = TaskManager(
            self.data_file_base, db_file=self.db_path, user_id=self.user_b["id"])
        reloaded_b.load()
        self.assertEqual(len(reloaded_b.get_all()), 1)
        self.assertEqual(reloaded_b.get_all()[0].title, "Bob Math Assignment")

    def test_task_crud(self):
        mgr = TaskManager(self.data_file_base,
                          db_file=self.db_path, user_id=self.user_a["id"])
        mgr.load()

        # Create
        task = mgr.add_task("Write Essay", "High", date(
            2026, 7, 5), "English Lit essay", "Study")
        self.assertEqual(task.title, "Write Essay")
        self.assertEqual(task.description, "English Lit essay")
        self.assertEqual(task.priority, "High")
        self.assertEqual(task.category, "Study")
        self.assertEqual(task.status, "Pending")

        # Read / Find
        self.assertIsNotNone(mgr.find_by_id(task.task_id))

        # Update
        mgr.update_task(task.task_id, title="Edit Essay",
                        description="Updated description", category="Exam")
        self.assertEqual(task.title, "Edit Essay")
        self.assertEqual(task.description, "Updated description")
        self.assertEqual(task.category, "Exam")

        # Complete
        mgr.complete_task(task.task_id)
        self.assertTrue(task.is_completed())

        # Delete
        mgr.delete_task(task.task_id)
        self.assertEqual(len(mgr.get_all()), 0)


if __name__ == "__main__":
    unittest.main()
