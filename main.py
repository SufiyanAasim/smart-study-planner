"""
main.py
Main launcher and Terminal-based user interface for the Smart Study Planner.
Author: Mohammad Sufiyan Aasim (SufiyanAasim)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from datetime import date
from models import PRIORITY_LEVELS, DATE_FORMAT
from logic import TaskManager
from database import DatabaseManager
import utils

DATA_FILE = "data/tasks.json"
DB_FILE = "data/planner.db"

SECURITY_QUESTIONS = (
    "What was the name of your first school?",
    "What is your favorite pet's name?",
    "What is your mother's maiden name?",
    "In what city or town was your first job?"
)

# CLI Main Authentication Menu
AUTH_MENU = """
===================== USER AUTHENTICATION =====================
  1. Login
  2. Register new account
  3. Forgot Password
  0. Back to Launcher Menu
==============================================================="""

# CLI Task Manager Menu
PLANNER_MENU = """
==================== SMART STUDY PLANNER ====================
  1. Add a task
  2. View all tasks
  3. Update a task
  4. Mark a task as completed
  5. Delete a task
  6. Search / filter / sort tasks
  7. View dashboard & insights
  8. Save tasks (manual sync)
  0. Logout
============================================================="""


def print_tasks(tasks):
    """Formats and prints our study tasks inside a neat terminal table."""
    if not tasks:
        print("  (No tasks to show.)")
        return
    print(f"  {'ID':<4}{'Title':<25}{'Category':<12}{'Priority':<9}{'Deadline':<12}"
          f"{'Status':<10}{'Days left':<12}")
    print("  " + "-" * 84)
    for task in tasks:
        days_text = str(task.days_left())
        if task.is_overdue():
            days_text += " OVERDUE"
        
        # Clean title & category to prevent tab/newline breakage
        clean_title = task.title.replace('\n', ' ').replace('\t', ' ')
        title = (clean_title[:22] + "...") if len(clean_title) > 25 else clean_title
        
        clean_cat = task.category.replace('\n', ' ').replace('\t', ' ')
        category = (clean_cat[:9] + "...") if len(clean_cat) > 12 else clean_cat

        print(f"  {task.task_id:<4}{title:<25}{category:<12}{task.priority:<9}"
              f"{task.deadline.strftime(DATE_FORMAT):<12}{task.status:<10}{days_text:<12}")


def handle_add(manager):
    """CLI flow for adding a new task after validating inputs."""
    print("\n➕ -- Add a New Task --")
    print("  0. Cancel and return to menu")
    title = utils.get_non_empty_string("  Title (0 to cancel): ", allow_exit=True)
    if title is None:
        print("  (Action cancelled.)")
        return
    description = input("  Description (optional): ").strip()
    priority = utils.get_valid_priority("  Priority", allow_exit=True)
    if priority is None:
        print("  (Action cancelled.)")
        return
    category = utils.get_non_empty_string("  Category (e.g. Study, Exam, Project) [Study]: ", allow_exit=True)
    if category is None:
        print("  (Action cancelled.)")
        return
    if category.strip() == "":
        category = "Study"
    deadline = utils.get_valid_date("  Deadline", allow_exit=True)
    if deadline is None:
        print("  (Action cancelled.)")
        return
    task = manager.add_task(title, priority, deadline, description, category)
    manager.save()
    print(f"  + Task #{task.task_id} added and saved successfully.")


def handle_view(manager):
    """Prints all current tasks in the planner."""
    print("\n📋 -- Current Study Tasks --")
    print_tasks(manager.get_all())


def handle_update(manager):
    """CLI flow for updating task fields. Pressing enter leaves the field unchanged."""
    print("\n📝 -- Update a Task --")
    print("  0. Cancel and return to menu")
    if not manager.get_all():
        print("  (There are no tasks to update.)")
        return
    print_tasks(manager.get_all())
    task_id = utils.get_valid_int("  Enter the ID of the task to update (0 to cancel): ", allow_exit=True)
    if task_id is None:
        print("  (Action cancelled.)")
        return
    task = manager.find_by_id(task_id)
    if task is None:
        print(f"  ! No task found with ID {task_id}.")
        return

    print("  Leave field blank to keep current value.")
    new_title = input(f"  New title [{task.title}]: ").strip()
    new_title = new_title if new_title else None

    new_desc = input(f"  New description [{task.description}]: ").strip()
    new_desc = new_desc if new_desc else None

    new_priority = None
    if utils.confirm("  Change priority?"):
        new_priority = utils.get_valid_priority("  New priority")

    new_cat = input(f"  New category [{task.category}]: ").strip()
    new_cat = new_cat if new_cat else None

    new_deadline = None
    if utils.confirm("  Change deadline?"):
        new_deadline = utils.get_valid_date("  New deadline")

    manager.update_task(task_id, new_title, new_priority, new_deadline, new_desc, new_cat)
    manager.save()
    print(f"  ~ Task #{task_id} updated and saved.")


def handle_complete(manager):
    """CLI flow to complete a pending task."""
    print("\n✔️ -- Complete a Task --")
    print("  0. Cancel and return to menu")
    pending = manager.filter_by_status(False)
    if not pending:
        print("  (There are no pending tasks.)")
        return
    print_tasks(pending)
    task_id = utils.get_valid_int("  Enter the ID of the task to complete (0 to cancel): ", allow_exit=True)
    if task_id is None:
        print("  (Action cancelled.)")
        return
    if manager.complete_task(task_id):
        manager.save()
        print(f"  * Task #{task_id} marked as completed and saved.")
    else:
        print(f"  ! No task found with ID {task_id}.")


def handle_delete(manager):
    """CLI flow to delete a task after user confirmation."""
    print("\n❌ -- Delete a Task --")
    print("  0. Cancel and return to menu")
    if not manager.get_all():
        print("  (There are no tasks to delete.)")
        return
    print_tasks(manager.get_all())
    task_id = utils.get_valid_int("  Enter the ID of the task to delete (0 to cancel): ", allow_exit=True)
    if task_id is None:
        print("  (Action cancelled.)")
        return
    task = manager.find_by_id(task_id)
    if task is None:
        print(f"  ! No task found with ID {task_id}.")
        return
    if utils.confirm(f"  Really delete task #{task_id} ('{task.title}')?"):
        manager.delete_task(task_id)
        manager.save()
        print(f"  - Task #{task_id} deleted and database updated.")
    else:
        print("  (Deletion cancelled.)")


def handle_search_filter_sort(manager):
    """Renders the search, filter, and sort menu."""
    while True:
        print("\n🔍 -- Search, Filter & Sort Tasks --")
        print("  1. Search by keyword (title/description)")
        print("  2. Filter by status (Pending)")
        print("  3. Filter by status (Completed)")
        print("  4. Filter by priority (High/Medium/Low)")
        print("  5. Filter by category")
        print("  6. Sort by deadline")
        print("  7. Sort by priority")
        print("  8. Sort by title")
        print("  9. Sort by category")
        print("  0. Return to main menu")
        
        choice = utils.get_menu_choice("  Choose an option: ",
                                       ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9"))
        if choice == "0":
            break
        elif choice == "1":
            keyword = utils.get_non_empty_string("  Keyword: ")
            print_tasks(manager.search_by_keyword(keyword))
        elif choice == "2":
            print_tasks(manager.filter_by_status(False))
        elif choice == "3":
            print_tasks(manager.filter_by_status(True))
        elif choice == "4":
            priority = utils.get_valid_priority("  Priority")
            print_tasks(manager.filter_by_priority(priority))
        elif choice == "5":
            category = utils.get_non_empty_string("  Category: ")
            print_tasks(manager.filter_by_category(category))
        elif choice == "6":
            print_tasks(manager.sorted_by_deadline())
        elif choice == "7":
            print_tasks(manager.sorted_by_priority())
        elif choice == "8":
            print_tasks(manager.sorted_by_title())
        elif choice == "9":
            print_tasks(manager.sorted_by_category())


def handle_summary(manager):
    """Renders terminal statistics, custom progress bars, and productivity advice."""
    print("\n📊 -- Study Analytics Summary & Insights --")
    summary = manager.get_summary()
    if summary["total"] == 0:
        print("  (No tasks yet — add some to see insights.)")
        return
    print(f"  Total tasks : {summary['total']}")
    print(f"  Completed   : {summary['completed']}  "
          f"{utils.text_bar(summary['completed'], summary['total'])}")
    print(f"  Pending     : {summary['pending']}")
    print(f"  Overdue     : {summary['overdue']}")
    
    # Check for Today's tasks (deadline is today)
    today = date.today()
    todays_tasks = [t for t in manager.get_all() if t.deadline == today and not t.is_completed()]
    print(f"  Today's Tasks pending: {len(todays_tasks)}")
    
    print("\n  By priority :")
    for level in PRIORITY_LEVELS:
        count = summary["by_priority"][level]
        print(f"    {level:<8}: {count}  {utils.text_bar(count, summary['total'])}")
        
    # Category Distribution
    categories = {}
    for task in manager.get_all():
        cat = task.category
        categories[cat] = categories.get(cat, 0) + 1
    print("\n  By category :")
    for cat, count in categories.items():
        print(f"    {cat:<12}: {count}  {utils.text_bar(count, summary['total'])}")

    # Recommendations
    if summary["overdue"] > 0:
        print(f"\n  💡 Recommendation: You have {summary['overdue']} overdue task(s). Consider tackling those first.")
    elif len(todays_tasks) > 0:
        print(f"\n  💡 Recommendation: You have {len(todays_tasks)} study deadline(s) ending today. Review them now!")
    elif summary["pending"] == 0:
        print("\n  🏆 Outstanding: All study milestones have been met!")
    else:
        print("\n  📈 You're on track — no overdue tasks. Keep up the good work!")


def handle_register(db):
    """CLI signup flow with rigorous validations."""
    print("\n📝 -- Register a New Account --")
    
    # Full Name Validation
    while True:
        full_name = input("  Full Name: ").strip()
        if utils.validate_full_name(full_name):
            break
        print("  ! Invalid name. Use letters, spaces, hyphens only (min 2 chars).")

    # Email Validation & Uniqueness
    while True:
        email = input("  Email: ").strip()
        if not utils.validate_email(email):
            print("  ! Invalid email format. Try again.")
            continue
        if db.check_duplicate_email(email):
            print("  ! This email is already registered. Choose another or login.")
            continue
        break

    # Optional Username & Uniqueness
    while True:
        username = input("  Username (optional, press Enter to skip): ").strip()
        if not username:
            username = None
            break
        if db.check_duplicate_username(username):
            print("  ! Username is already taken. Choose another.")
            continue
        break

    # Password Validation
    while True:
        password = input("  Password: ").strip()
        ok, msg = utils.validate_password_strength(password)
        if not ok:
            print(f"  ! {msg}")
            continue
        confirm_pass = input("  Confirm Password: ").strip()
        if password != confirm_pass:
            print("  ! Passwords do not match. Try again.")
            continue
        break

    # Security Question Selection
    print("\n  Please choose a security question for password recovery:")
    for idx, q in enumerate(SECURITY_QUESTIONS, 1):
        print(f"    {idx}. {q}")
    choice_idx = utils.get_valid_int("  Select question (1-4): ")
    while choice_idx not in (1, 2, 3, 4):
        print("  ! Choose a valid question number between 1 and 4.")
        choice_idx = utils.get_valid_int("  Select question (1-4): ")
    security_question = SECURITY_QUESTIONS[choice_idx - 1]
    security_answer = utils.get_non_empty_string("  Security Answer: ")

    try:
        user = db.register_user(full_name, email, username, password, security_question, security_answer)
        print(f"\n  ✅ Registration successful! Welcome, {user['full_name']}.")
        return user
    except ValueError as exc:
        print(f"  ! Registration failed: {exc}")
        return None


def handle_login(db):
    """CLI login flow supporting email or username login."""
    print("\n🔐 -- Login to Smart Study Planner --")
    credential = utils.get_non_empty_string("  Username or Email: ")
    password = utils.get_non_empty_string("  Password: ")
    
    user = db.authenticate_user(credential, password)
    if user is None:
        print("  ! Invalid credentials. Authentication failed.")
        return None
    print(f"\n  ✅ Welcome back, {user['full_name']}!")
    return user


def handle_forgot_password(db):
    """CLI flow to reset password using security question verification."""
    print("\n🔑 -- Forgot Password / Password Reset --")
    email = utils.get_non_empty_string("  Enter registered Email: ")
    
    # Query details first
    security_question = db.get_security_question(email)
    if not security_question:
        print("  ! No account is registered with that email.")
        return
    print(f"\n  Security Question: {security_question}")
    security_answer = utils.get_non_empty_string("  Your Answer: ")

    # Validate new password strength
    while True:
        new_password = input("  Enter New Password: ").strip()
        ok, msg = utils.validate_password_strength(new_password)
        if not ok:
            print(f"  ! {msg}")
            continue
        confirm_pass = input("  Confirm New Password: ").strip()
        if new_password != confirm_pass:
            print("  ! Passwords do not match.")
            continue
        break

    try:
        db.reset_password(email, security_question, security_answer, new_password)
        print("  ✅ Password reset successful! You can now log in.")
    except ValueError as exc:
        print(f"  ! Reset failed: {exc}")


def run_cli_mode():
    """Starts the CLI session manager loop."""
    print("\n💻 Launching Command Line Interface (CLI) Mode...")
    db = DatabaseManager(DB_FILE)
    
    current_user = None
    
    # Outer Authentication loop
    while True:
        if current_user is None:
            print(AUTH_MENU)
            choice = utils.get_menu_choice("  Select option: ", ("0", "1", "2", "3"))
            if choice == "0":
                print("  Returning to launcher menu...")
                break
            elif choice == "1":
                current_user = handle_login(db)
            elif choice == "2":
                current_user = handle_register(db)
            elif choice == "3":
                handle_forgot_password(db)
        else:
            # Planner session is active
            manager = TaskManager(DATA_FILE, db_file=DB_FILE, user_id=current_user["id"])
            manager.load()
            if manager.get_all():
                print(f"  Loaded {len(manager.get_all())} saved task(s).")
            
            while True:
                print(PLANNER_MENU)
                planner_choice = utils.get_menu_choice("  Select option: ", 
                                                       ("0", "1", "2", "3", "4", "5", "6", "7", "8"))
                if planner_choice == "1":
                    handle_add(manager)
                elif planner_choice == "2":
                    handle_view(manager)
                elif planner_choice == "3":
                    handle_update(manager)
                elif planner_choice == "4":
                    handle_complete(manager)
                elif planner_choice == "5":
                    handle_delete(manager)
                elif planner_choice == "6":
                    handle_search_filter_sort(manager)
                elif planner_choice == "7":
                    handle_summary(manager)
                elif planner_choice == "8":
                    manager.save()
                    print("  Tasks synchronized to database.")
                elif planner_choice == "0":
                    manager.save()
                    print(f"  Logged out. Tasks saved for user: {current_user['full_name']}")
                    current_user = None
                    break


def run_gui_mode():
    """Launches the Tkinter Graphical User Interface (GUI) Mode."""
    print("\n🖥️ Launching Graphical User Interface (GUI) Mode...")
    try:
        import gui
        gui.main()
    except Exception as exc:
        print(f"  ! Failed to launch GUI: {exc}")
        import traceback
        traceback.print_exc()


def show_launcher_menu():
    """Main orchestrator launcher menu (original fallback/manual menu)."""
    while True:
        print("\n================== SMART STUDY PLANNER ==================")
        print("  1. Launch CLI Mode (Terminal)")
        print("  2. Launch GUI Mode (Desktop Application)")
        print("  3. Exit")
        print("=========================================================")
        choice = utils.get_menu_choice("  Select launch mode: ", ("1", "2", "3"))
        
        if choice == "1":
            run_cli_mode()
        elif choice == "2":
            run_gui_mode()
        elif choice == "3":
            print("  Thank you for using the Smart Study Planner. Goodbye!")
            sys.exit(0)


def main():
    """Main launcher entry point."""
    # Ensure stdout handles UTF-8 (emojis) correctly on Windows
    if sys.stdout is not None:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    # CLI flag detection
    if "--cli" in sys.argv:
        run_cli_mode()
    elif "--menu" in sys.argv:
        show_launcher_menu()
    else:
        # Default behavior: run GUI directly
        try:
            import gui
            gui.main()
        except Exception as exc:
            if sys.stdout and sys.stdout.isatty():
                print(f"  ! Failed to launch GUI: {exc}")
                print("  Falling back to Launcher Menu...")
                show_launcher_menu()
            else:
                try:
                    from tkinter import messagebox
                    messagebox.showerror("Error", f"Failed to launch Smart Study Planner GUI:\n{exc}")
                except Exception:
                    pass
                sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Interrupted. Exiting...")
        sys.exit(0)
