"""
gui.py
Graphical user interface (GUI) for the Smart Study Planner.
Designed as a modern, responsive single-window Slate Dark/Light dashboard.
Author: Mohammad Sufiyan Aasim (SufiyanAasim)
"""

import tkinter as tk
from tkinter import ttk, simpledialog
from datetime import date, timedelta
from PIL import Image, ImageTk

from models import PRIORITY_LEVELS, DATE_FORMAT
from logic import TaskManager
from utils import (
    parse_date, validate_email, validate_password_strength, validate_full_name,
    play_click_sound, play_success_sound, play_error_sound, play_notify_sound,
    get_resource_path, set_sound_enabled, is_sound_enabled,
    play_soundscape, stop_soundscape
)
import json
import os
from database import DatabaseManager
from translations import TRANSLATIONS
import lan as lan_module

DB_FILE = "data/planner.db"
DATA_FILE_BASE = "data/tasks.json"

SECURITY_QUESTIONS = (
    "What was the name of your first school?",
    "What is your favorite pet's name?",
    "What is your mother's maiden name?",
    "In what city or town was your first job?"
)

# Theme palettes
THEMES = {
    "dark": {
        "bg_main": "#0f172a",       # Slate 900
        "bg_card": "#1e293b",       # Slate 800
        "text_primary": "#f8fafc",   # Slate 50
        "text_muted": "#94a3b8",     # Slate 400
        "border": "#334155",         # Slate 700
        "primary": "#3b82f6",        # Blue 500
        "primary_hover": "#2563eb",  # Blue 600
        "success": "#10b981",        # Emerald 500
        "success_bg": "#064e3b",     # Dark Green
        "success_hover": "#059669",  # Emerald 600
        "danger": "#ef4444",         # Red 500
        "danger_bg": "#7f1d1d",      # Dark Red
        "danger_hover": "#dc2626",   # Red 600
        "warning": "#f59e0b",        # Amber 500
        "warning_hover": "#d97706",  # Amber 600
        "trough": "#1e293b",
        "scroll_thumb": "#475569",
        "scroll_trough": "#0f172a"
    },
    "light": {
        "bg_main": "#f8fafc",       # Slate 50
        "bg_card": "#ffffff",       # White
        "text_primary": "#0f172a",   # Slate 900
        "text_muted": "#64748b",     # Slate 500
        "border": "#e2e8f0",         # Slate 200
        "primary": "#2563eb",        # Blue 600
        "primary_hover": "#1d4ed8",  # Blue 700
        "success": "#16a34a",        # Green 600
        "success_bg": "#dcfce7",     # Light Green
        "success_hover": "#15803d",  # Green 700
        "danger": "#dc2626",         # Red 600
        "danger_bg": "#fee2e2",      # Light Red
        "danger_hover": "#b91c1c",   # Red 700
        "warning": "#ea580c",        # Orange 600
        "warning_hover": "#c2410c",  # Orange 700
        "trough": "#f1f5f9",
        "scroll_thumb": "#cbd5e1",
        "scroll_trough": "#f1f5f9"
    }
}


# --- Premium Slate Custom Messagebox Class ---

class ModernMessageBox(tk.Toplevel):
    """A premium, modern Slate-themed custom modal dialog box."""

    def __init__(self, parent, title, message, box_type="info"):
        # Auto-detect parent if none provided
        if not parent:
            try:
                parent = tk._default_root
            except Exception:
                pass
        super().__init__(parent)
        self.title(title)
        self.result = None

        # Detect active theme from parent
        self.theme_name = "dark"
        if parent:
            # Check if parent is a widget and has a theme set
            if hasattr(parent, "current_theme_name"):
                self.theme_name = parent.current_theme_name
            elif hasattr(parent, "theme") and isinstance(parent.theme, dict):
                if parent.theme.get("bg_main") == "#f8fafc":
                    self.theme_name = "light"
        
        self.theme = THEMES[self.theme_name]

        # Style window
        self.configure(bg=self.theme["bg_card"])
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()

        # Center on parent or screen
        self.update_idletasks()
        if parent:
            try:
                px = parent.winfo_rootx() + (parent.winfo_width() // 2) - 180
                py = parent.winfo_rooty() + (parent.winfo_height() // 2) - 90
                self.geometry(f"360x180+{px}+{py}")
            except Exception:
                # Fallback to screen center
                sw = self.winfo_screenwidth()
                sh = self.winfo_screenheight()
                self.geometry(f"360x180+{sw//2-180}+{sh//2-90}")
        else:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"360x180+{sw//2-180}+{sh//2-90}")

        # Grid config
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Main layout frame
        main_frame = tk.Frame(self, bg=self.theme["bg_card"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=15)
        main_frame.columnconfigure(1, weight=1)

        # Icon based on type
        icons = {
            "info": ("ℹ️", self.theme["primary"]),
            "success": ("✅", self.theme["success"]),
            "error": ("❌", self.theme["danger"]),
            "warning": ("⚠️", self.theme["warning"]),
            "question": ("❓", self.theme["primary"])
        }
        emoji, color = icons.get(box_type, ("ℹ️", self.theme["primary"]))

        # Dynamic emoji adjustment for success chimes
        if box_type == "info" and any(k in message.lower() for k in ["success", "copi", "export", "sav", "sync", "updat"]):
            emoji, color = icons["success"]

        icon_lbl = tk.Label(main_frame, text=emoji, font=("Segoe UI", 26), bg=self.theme["bg_card"], fg=color)
        icon_lbl.grid(row=0, column=0, sticky="nw", padx=(0, 15), pady=10)

        # Message Text
        msg_lbl = tk.Label(main_frame, text=message, font=("Segoe UI", 10), bg=self.theme["bg_card"], fg=self.theme["text_primary"],
                           justify="left", anchor="w", wrap=250)
        msg_lbl.grid(row=0, column=1, sticky="nsew", pady=10)

        # Action Buttons frame
        btn_frame = tk.Frame(main_frame, bg=self.theme["bg_card"])
        btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        if box_type == "question":
            # Yes/No buttons
            yes_btn = create_flat_button(
                btn_frame, "✔️ Yes", self.theme["primary"], "#ffffff", self._on_yes, hover_bg=self.theme["primary_hover"]
            )
            yes_btn.pack(side="left", padx=(0, 10))

            no_btn = create_flat_button(
                btn_frame, "❌ No", self.theme["border"], self.theme["text_primary"], self._on_no, hover_bg=self.theme["bg_main"]
            )
            no_btn.pack(side="right")
        else:
            # OK button
            ok_btn = create_flat_button(
                btn_frame, "OK", self.theme["primary"], "#ffffff", self._on_ok, hover_bg=self.theme["primary_hover"], padx=20
            )
            ok_btn.pack(side="right")

        # Focus button
        self.bind("<Escape>", lambda e: self._on_no() if box_type == "question" else self._on_ok())
        self.bind("<Return>", lambda e: self._on_yes() if box_type == "question" else self._on_ok())

        self.protocol("WM_DELETE_WINDOW", self._on_no if box_type == "question" else self._on_ok)
        self.wait_window()

    def _on_yes(self):
        self.result = True
        self.destroy()

    def _on_no(self):
        self.result = False
        self.destroy()

    def _on_ok(self):
        self.result = True
        self.destroy()

    @classmethod
    def show(cls, parent, title, message, box_type="info"):
        dialog = cls(parent, title, message, box_type)
        return dialog.result


class ModernInputDialog(tk.Toplevel):
    """Themed single-line text-input dialog, consistent with ModernMessageBox."""

    def __init__(self, parent, title, prompt, initialvalue=""):
        if not parent:
            try:
                parent = tk._default_root
            except Exception:
                pass
        super().__init__(parent)
        self.title(title)
        self.result = None

        theme_name = "dark"
        if parent:
            if hasattr(parent, "current_theme_name"):
                theme_name = parent.current_theme_name
            elif hasattr(parent, "theme") and isinstance(parent.theme, dict):
                if parent.theme.get("bg_main") == "#f8fafc":
                    theme_name = "light"
        self.theme = THEMES[theme_name]

        self.configure(bg=self.theme["bg_card"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        w, h = 400, 200
        if parent:
            try:
                px = parent.winfo_rootx() + parent.winfo_width() // 2 - w // 2
                py = parent.winfo_rooty() + parent.winfo_height() // 2 - h // 2
                self.geometry(f"{w}x{h}+{px}+{py}")
            except Exception:
                sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
                self.geometry(f"{w}x{h}+{sw//2 - w//2}+{sh//2 - h//2}")
        else:
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            self.geometry(f"{w}x{h}+{sw//2 - w//2}+{sh//2 - h//2}")

        main = tk.Frame(self, bg=self.theme["bg_card"])
        main.pack(fill="both", expand=True, padx=22, pady=18)

        tk.Label(main, text=prompt, font=("Segoe UI", 10), bg=self.theme["bg_card"],
                 fg=self.theme["text_primary"], justify="left", anchor="w",
                 wraplength=356).pack(anchor="w", pady=(0, 10))

        self._entry = tk.Entry(main, font=("Segoe UI", 10), bg=self.theme["bg_main"],
                               fg=self.theme["text_primary"],
                               insertbackground=self.theme["text_primary"],
                               highlightbackground=self.theme["border"],
                               highlightthickness=1, bd=0, relief="flat")
        self._entry.pack(fill="x", ipady=6)
        if initialvalue:
            self._entry.insert(0, str(initialvalue))
            self._entry.select_range(0, "end")
        bind_focus_highlight(self._entry, self.theme)

        btn_row = tk.Frame(main, bg=self.theme["bg_card"])
        btn_row.pack(fill="x", pady=(16, 0))

        ok_btn = create_flat_button(btn_row, "OK", self.theme["primary"], "#ffffff",
                                    self._on_ok, hover_bg=self.theme["primary_hover"], padx=20)
        ok_btn.pack(side="left", padx=(0, 10))

        cancel_btn = create_flat_button(btn_row, "Cancel", self.theme["border"],
                                        self.theme["text_primary"], self._on_cancel,
                                        hover_bg=self.theme["bg_main"], padx=20)
        cancel_btn.pack(side="left")

        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel())
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self._entry.focus_set()
        self.wait_window()

    def _on_ok(self):
        self.result = self._entry.get()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()

    @classmethod
    def ask(cls, parent, title, prompt, initialvalue=""):
        return cls(parent, title, prompt, initialvalue).result


class messagebox:
    @staticmethod
    def showinfo(title, message, parent=None):
        return ModernMessageBox.show(parent, title, message, "info")

    @staticmethod
    def showerror(title, message, parent=None):
        return ModernMessageBox.show(parent, title, message, "error")

    @staticmethod
    def showwarning(title, message, parent=None):
        return ModernMessageBox.show(parent, title, message, "warning")

    @staticmethod
    def askyesno(title, message, parent=None):
        return ModernMessageBox.show(parent, title, message, "question")


def create_flat_button(parent, text, bg_color, fg_color, command, hover_bg=None, font=("Segoe UI", 10, "bold"), padx=12, pady=6):
    """Creates a flat button with modern styling and hand cursor."""
    def sound_command():
        play_click_sound()
        if command:
            command()

    button = tk.Button(
        parent,
        text=text,
        bg=bg_color,
        fg=fg_color,
        command=sound_command,
        font=font,
        relief="flat",
        activebackground=hover_bg or bg_color,
        activeforeground=fg_color,
        bd=0,
        cursor="hand2",
        padx=padx,
        pady=pady
    )
    # Store the resting/hover colors as mutable attributes so callers (e.g. the
    # sidebar's active-tab highlight) can change the resting colour and have the
    # hover Leave handler restore the NEW colour instead of the creation-time one.
    button._base_bg = bg_color
    button._hover_bg = hover_bg or bg_color
    button.bind("<Enter>", lambda event: button.config(bg=button._hover_bg))
    button.bind("<Leave>", lambda event: button.config(bg=button._base_bg))
    return button


def bind_focus_highlight(widget, theme):
    """Binds focus events to dynamically change border colors for premium focus states."""
    widget.bind("<FocusIn>", lambda e: widget.config(highlightbackground=theme["primary"]))
    widget.bind("<FocusOut>", lambda e: widget.config(highlightbackground=theme["border"]))


def bind_lowercase(entry):
    """Force an Entry's text to lowercase as the user types (usernames are always
    lowercase — no mixed/sentence case)."""
    def _lower(event=None):
        val = entry.get()
        low = val.lower()
        if val != low:
            pos = entry.index("insert")
            entry.delete(0, "end")
            entry.insert(0, low)
            entry.icursor(pos)
    entry.bind("<KeyRelease>", _lower)


def _blend_hex(c1, c2, t):
    """Linear blend of two #rrggbb colors. t=0 -> c1, t=1 -> c2."""
    c1 = c1.lstrip("#"); c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class ParticleCanvas(tk.Canvas):
    """A lightweight, theme-aware animated background: drifting particles linked by
    faint 'constellation' lines, optionally over a base image. Built for low cost:
    a small capped particle count, ~25fps, the loop pauses whenever the widget is
    not mapped, and it self-terminates once the widget is destroyed."""

    def __init__(self, parent, theme, base_image=None, count=26, **kw):
        super().__init__(parent, highlightthickness=0, bd=0, bg=theme["bg_main"], **kw)
        self.theme = theme
        self.base_image_raw = base_image
        self._photo = None
        self.count = count
        self.particles = []
        self._cw, self._ch = 1, 1
        self._seeded = False
        self._after_id = None

        # Pre-blend subtle, alpha-free colors (canvas has no real transparency).
        self.dot_color = _blend_hex(theme["bg_main"], theme["primary"], 0.75)
        self.line_color = _blend_hex(theme["bg_main"], theme["primary"], 0.28)
        self.grad_top = _blend_hex(theme["bg_main"], theme["primary"], 0.10)
        self.grad_bottom = theme["bg_main"]

        self.bind("<Configure>", self._on_configure)
        self._tick()

    def _on_configure(self, event):
        self._cw, self._ch = max(1, event.width), max(1, event.height)
        self._render_base()
        if not self._seeded and self._cw > 2 and self._ch > 2:
            self._seed()
        else:
            # Keep existing particles inside the new bounds on resize.
            for p in self.particles:
                p["x"] = min(p["x"], self._cw)
                p["y"] = min(p["y"], self._ch)

    def _seed(self):
        import random
        self.particles = []
        for _ in range(self.count):
            self.particles.append({
                "x": random.uniform(0, self._cw),
                "y": random.uniform(0, self._ch),
                "vx": random.uniform(-0.45, 0.45) or 0.2,
                "vy": random.uniform(-0.45, 0.45) or 0.2,
                "r": random.uniform(1.5, 3.2),
            })
        self._seeded = True

    def _render_base(self):
        """Draws the static backdrop (base image or vertical gradient) once per resize."""
        self.delete("bg")
        if self.base_image_raw is not None and self._cw > 2 and self._ch > 2:
            img = self.base_image_raw.resize((self._cw, self._ch), Image.Resampling.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)
            self.create_image(0, 0, anchor="nw", image=self._photo, tags="bg")
        else:
            step = 4
            for y in range(0, self._ch, step):
                t = y / max(1, self._ch)
                color = _blend_hex(self.grad_top, self.grad_bottom, t)
                self.create_rectangle(0, y, self._cw, y + step, fill=color, outline="", tags="bg")
        self.tag_lower("bg")

    def _tick(self):
        if not self.winfo_exists():
            return
        try:
            if self.winfo_ismapped() and self._seeded:
                self._step()
        except tk.TclError:
            return
        self._after_id = self.after(40, self._tick)

    def _step(self):
        self.delete("fx")
        pts = self.particles
        w, h = self._cw, self._ch
        for p in pts:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["x"] <= 0 or p["x"] >= w:
                p["vx"] *= -1
                p["x"] = min(max(p["x"], 0), w)
            if p["y"] <= 0 or p["y"] >= h:
                p["vy"] *= -1
                p["y"] = min(max(p["y"], 0), h)

        thresh = 115
        thresh2 = thresh * thresh
        n = len(pts)
        for i in range(n):
            pi = pts[i]
            for j in range(i + 1, n):
                pj = pts[j]
                dx = pi["x"] - pj["x"]
                dy = pi["y"] - pj["y"]
                if dx * dx + dy * dy < thresh2:
                    self.create_line(pi["x"], pi["y"], pj["x"], pj["y"],
                                     fill=self.line_color, width=1, tags="fx")
        for p in pts:
            r = p["r"]
            self.create_oval(p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r,
                             fill=self.dot_color, outline="", tags="fx")


class TaskDialog(simpledialog.Dialog):
    """Sleek modal dialog box for entering or modifying study task details."""

    def __init__(self, parent, title_text, theme, initial=None):
        self.theme = theme
        self.initial = initial or {}
        super().__init__(parent, title_text)

    def body(self, master):
        """Sets up input fields with theme styling."""
        self.configure(bg=self.theme["bg_card"])
        master.configure(bg=self.theme["bg_card"])

        label_font = ("Segoe UI", 10, "bold")
        entry_font = ("Segoe UI", 10)
        
        # Grid Configuration
        master.columnconfigure(1, weight=1)

        # Title
        tk.Label(master, text="Title *:", font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(
            row=0, column=0, sticky="w", pady=6, padx=8)
        self.title_entry = tk.Entry(master, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                    insertbackground=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                    highlightthickness=1, bd=0, width=35)
        self.title_entry.grid(row=0, column=1, pady=6, padx=8, sticky="ew")
        self.title_entry.insert(0, self.initial.get("title", ""))
        bind_focus_highlight(self.title_entry, self.theme)

        # Category
        tk.Label(master, text="Category:", font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(
            row=1, column=0, sticky="w", pady=6, padx=8)
        
        categories = ["Study", "Assignment", "Exam", "Project", "Lab", "Other"]
        self.category_box = ttk.Combobox(master, values=categories, state="normal", font=entry_font, width=33)
        self.category_box.grid(row=1, column=1, pady=6, padx=8, sticky="ew")
        self.category_box.set(self.initial.get("category", "Study"))

        # Priority
        tk.Label(master, text="Priority:", font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(
            row=2, column=0, sticky="w", pady=6, padx=8)
        self.priority_box = ttk.Combobox(master, values=list(PRIORITY_LEVELS), state="readonly", font=entry_font, width=33)
        self.priority_box.grid(row=2, column=1, pady=6, padx=8, sticky="ew")
        self.priority_box.set(self.initial.get("priority", PRIORITY_LEVELS[0]))

        # Deadline
        tk.Label(master, text="Deadline (YYYY-MM-DD) *:", font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(
            row=3, column=0, sticky="w", pady=6, padx=8)
        self.deadline_entry = tk.Entry(master, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                       insertbackground=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, width=35)
        self.deadline_entry.grid(row=3, column=1, pady=6, padx=8, sticky="ew")
        self.deadline_entry.insert(0, self.initial.get("deadline", date.today().strftime(DATE_FORMAT)))
        bind_focus_highlight(self.deadline_entry, self.theme)

        # Description
        tk.Label(master, text="Description:", font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(
            row=4, column=0, sticky="nw", pady=6, padx=8)
        self.description_text = tk.Text(master, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                        insertbackground=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                        highlightthickness=1, bd=0, height=4, width=35, wrap="word")
        self.description_text.grid(row=4, column=1, pady=6, padx=8, sticky="ew")
        self.description_text.insert("1.0", self.initial.get("description", "") or "")
        bind_focus_highlight(self.description_text, self.theme)

        return self.title_entry

    def buttonbox(self):
        """Add styled flat buttons."""
        box = tk.Frame(self, bg=self.theme["bg_card"])

        ok_button = create_flat_button(
            box, "💾 Save Task", self.theme["primary"], "#ffffff", self.ok, hover_bg=self.theme["primary_hover"])
        ok_button.pack(side="left", padx=6, pady=10)

        cancel_button = create_flat_button(
            box, "❌ Cancel", self.theme["border"], self.theme["text_primary"], self.cancel, hover_bg=self.theme["bg_main"])
        cancel_button.pack(side="left", padx=6, pady=10)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(pady=5)

    def validate(self):
        """Validate dialog field inputs."""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Invalid Input", "Title cannot be empty.")
            return False
            
        category = self.category_box.get().strip()
        if not category:
            category = "Study"
            
        priority = self.priority_box.get()
        if priority not in PRIORITY_LEVELS:
            messagebox.showerror("Invalid Input", "Please choose a valid priority level.")
            return False
            
        deadline = parse_date(self.deadline_entry.get())
        if deadline is None:
            messagebox.showerror(
                "Invalid Input",
                "Deadline must be a real calendar date in the format YYYY-MM-DD.")
            return False
            
        desc = self.description_text.get("1.0", "end-1c").strip()
        self._parsed = (title, priority, deadline, desc, category)
        return True

    def apply(self):
        self.result = self._parsed


class AuthFrame(tk.Frame):
    """Integrates Login, Registration, and Forgot Password in a unified styled Panel."""

    def __init__(self, parent, db, app_theme, on_login_success, initial_state=None):
        super().__init__(parent, bg=app_theme["bg_main"])
        self.parent = parent
        self.db = db
        self.theme = app_theme
        self.on_login_success = on_login_success
        self._initial_state = initial_state

        self.mode = "login"  # login, register, forgot
        
        # Animated background: the same theme-aware gradient particle-constellation
        # used on the Focus Timer screen (no static image), so it adapts cleanly to
        # both light and dark themes.
        self.bg_canvas = ParticleCanvas(self, self.theme, base_image=None, count=30)
        self.bg_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)

        # Load custom logo image using PIL
        self.logo_raw = Image.open(get_resource_path("assets/logo.png"))
        self.logo_resized = self.logo_raw.resize((65, 65), Image.Resampling.LANCZOS)
        self.logo_tk = ImageTk.PhotoImage(self.logo_resized)

        self._build_ui()

    def _build_ui(self):
        # Container Card Frame
        self.card = tk.Frame(self, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=430)
        self._restore_initial_state()

    def capture_state(self):
        """Snapshot the current auth view + entered field values so a theme switch
        (which rebuilds this frame) can restore exactly where the user was."""
        state = {"mode": self.mode, "fields": {}}
        try:
            if self.mode == "login":
                state["fields"] = {
                    "cred": self.login_cred_entry.get(),
                    "pwd": self.login_pwd_entry.get(),
                }
            elif self.mode == "register":
                state["fields"] = {
                    "fullname": self.reg_fullname.get(),
                    "email": self.reg_email.get(),
                    "username": self.reg_username.get(),
                    "password": self.reg_password.get(),
                    "confirm": self.reg_confirm.get(),
                    "question": self.reg_question.get(),
                    "answer": self.reg_answer.get(),
                }
            elif self.mode == "forgot":
                state["fields"] = {"email": self.forgot_email_entry.get()}
        except (AttributeError, tk.TclError):
            pass
        return state

    def _restore_initial_state(self):
        """Re-open the view captured before a rebuild, refilling its fields."""
        state = self._initial_state
        if not state:
            self.show_login_view()
            # Faster sign-in: prefill the last identifier used on this machine.
            if getattr(self.parent, "last_login", ""):
                self.login_cred_entry.insert(0, self.parent.last_login)
                self.login_pwd_entry.focus_set()
            return

        mode = state.get("mode", "login")
        fields = state.get("fields", {})
        if mode == "register":
            self.show_register_view()
            self.reg_fullname.insert(0, fields.get("fullname", ""))
            self.reg_email.insert(0, fields.get("email", ""))
            self.reg_username.insert(0, fields.get("username", ""))
            self.reg_password.insert(0, fields.get("password", ""))
            self.reg_confirm.insert(0, fields.get("confirm", ""))
            if fields.get("question"):
                self.reg_question.set(fields["question"])
            self.reg_answer.insert(0, fields.get("answer", ""))
        elif mode == "forgot":
            self.show_forgot_view()
            self.forgot_email_entry.insert(0, fields.get("email", ""))
        else:
            self.show_login_view()
            self.login_cred_entry.insert(0, fields.get("cred", ""))
            self.login_pwd_entry.insert(0, fields.get("pwd", ""))

    # Ordered language list shared by the auth dropdown.
    LANGUAGES = (
        ("English", "en"), ("Deutsch", "de"), ("Español", "es"), ("Français", "fr"),
        ("Русский", "ru"), ("中文", "zh"), ("日本語", "ja"), ("한국어", "ko"),
        ("हिन्दी", "hi"), ("اردو", "ur"), ("العربية", "ar"), ("فارسی", "fa")
    )

    def add_auth_controls(self):
        """Builds an aligned top-right control bar with a proper language dropdown
        and an enhanced light/dark theme toggle. Used on every auth view so the
        controls always line up identically."""
        bar = tk.Frame(self.card, bg=self.theme["bg_card"])
        bar.place(relx=1.0, rely=0.0, anchor="ne", x=-18, y=14)

        name_to_code = {name: code for name, code in self.LANGUAGES}
        code_to_name = {code: name for name, code in self.LANGUAGES}

        # --- Proper language dropdown (themed ttk.Combobox) ---
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Auth.TCombobox",
            fieldbackground=self.theme["bg_main"],
            background=self.theme["bg_main"],
            foreground=self.theme["text_primary"],
            arrowcolor=self.theme["text_primary"],
            bordercolor=self.theme["border"],
            lightcolor=self.theme["border"],
            darkcolor=self.theme["border"],
            relief="flat",
            padding=4
        )
        style.map(
            "Auth.TCombobox",
            fieldbackground=[("readonly", self.theme["bg_main"])],
            foreground=[("readonly", self.theme["text_primary"])],
            selectbackground=[("readonly", self.theme["bg_main"])],
            selectforeground=[("readonly", self.theme["text_primary"])]
        )
        # Style the popdown list to match the active theme.
        self.parent.option_add("*TCombobox*Listbox.background", self.theme["bg_card"])
        self.parent.option_add("*TCombobox*Listbox.foreground", self.theme["text_primary"])
        self.parent.option_add("*TCombobox*Listbox.selectBackground", self.theme["primary"])
        self.parent.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.parent.option_add("*TCombobox*Listbox.font", "{Segoe UI} 9")

        lang_combo = ttk.Combobox(
            bar,
            values=[name for name, _ in self.LANGUAGES],
            state="readonly",
            style="Auth.TCombobox",
            font=("Segoe UI", 9),
            width=9
        )
        lang_combo.set(code_to_name.get(self.parent.current_lang, "English"))
        lang_combo.pack(side="left", padx=(0, 8), ipady=2)
        lang_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: (lang_combo.selection_clear(), self._change_language(name_to_code[lang_combo.get()]))
        )

        # --- Enhanced light/dark theme toggle (pill button with icon) ---
        is_dark = self.parent.current_theme == "dark"
        # Show the mode you will switch TO.
        icon = "☀️" if is_dark else "🌙"
        label = "Light" if is_dark else "Dark"
        accent = self.theme["warning"] if is_dark else self.theme["primary"]

        theme_btn = tk.Button(
            bar,
            text=f"{icon}  {label}",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"],
            fg=accent,
            relief="flat",
            activebackground=self.theme["border"],
            activeforeground=accent,
            highlightbackground=accent,
            highlightcolor=accent,
            highlightthickness=1,
            bd=0,
            cursor="hand2",
            padx=12,
            pady=4,
            command=self._toggle_theme
        )
        theme_btn.pack(side="left")
        theme_btn.bind("<Enter>", lambda e: theme_btn.config(bg=self.theme["border"]))
        theme_btn.bind("<Leave>", lambda e: theme_btn.config(bg=self.theme["bg_main"]))

    def _toggle_theme(self):
        play_click_sound()
        self.parent.toggle_theme()

    def _change_language(self, code):
        play_click_sound()
        self.parent.current_lang = code
        self.redraw_active_view()

    def redraw_active_view(self):
        if self.mode == "login":
            cred = self.login_cred_entry.get()
            pwd = self.login_pwd_entry.get()
            self.show_login_view()
            self.login_cred_entry.insert(0, cred)
            self.login_pwd_entry.insert(0, pwd)
        elif self.mode == "register":
            fullname = self.reg_fullname.get()
            email = self.reg_email.get()
            username = self.reg_username.get()
            pwd = self.reg_password.get()
            confirm = self.reg_confirm.get()
            answer = self.reg_answer.get()
            self.show_register_view()
            self.reg_fullname.insert(0, fullname)
            self.reg_email.insert(0, email)
            self.reg_username.insert(0, username)
            self.reg_password.insert(0, pwd)
            self.reg_confirm.insert(0, confirm)
            self.reg_answer.insert(0, answer)
        elif self.mode == "forgot":
            email = self.forgot_email_entry.get()
            self.show_forgot_view()
            self.forgot_email_entry.insert(0, email)

    def clear_card(self):
        for widget in self.card.winfo_children():
            widget.destroy()

    def toggle_password_visibility(self, entry, button):
        if entry.cget("show") == "*":
            entry.config(show="")
            button.config(text="🙈")
        else:
            entry.config(show="*")
            button.config(text="👁")

    def _quick_pick_account(self, identifier):
        """Prefill the login identifier from a registered-account chip."""
        play_click_sound()
        self.login_cred_entry.delete(0, "end")
        self.login_cred_entry.insert(0, identifier)
        self.login_pwd_entry.delete(0, "end")
        self.login_pwd_entry.focus_set()

    def show_login_view(self):
        self.clear_card()
        self.mode = "login"
        try:
            self._login_accounts = self.db.list_users(limit=6)
        except Exception:
            self._login_accounts = []
        card_h = 600 if self._login_accounts else 540
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=card_h)

        # Aligned language dropdown + theme toggle (top-right)
        self.add_auth_controls()

        # Display Logo
        logo_label = tk.Label(self.card, image=self.logo_tk, bg=self.theme["bg_card"])
        logo_label.pack(pady=(45, 5))

        lang = self.parent.current_lang

        # Title
        tk.Label(self.card, text=TRANSLATIONS[lang]["app_title"], font=("Segoe UI", 14, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(pady=(2, 2))
        tk.Label(self.card, text=TRANSLATIONS[lang]["login_subtitle"], font=("Segoe UI", 9),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 10))

        # Registered accounts quick-pick — click a chip to prefill the identifier.
        if self._login_accounts:
            acc_section = tk.Frame(self.card, bg=self.theme["bg_card"])
            acc_section.pack(fill="x", padx=40, pady=(0, 6))
            tk.Label(acc_section, text=TRANSLATIONS[lang].get("registered_accounts", "Registered accounts"),
                     font=("Segoe UI", 8, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(anchor="w", pady=(0, 3))
            chips = tk.Frame(acc_section, bg=self.theme["bg_card"])
            chips.pack(fill="x")
            for acc in self._login_accounts[:3]:
                ident = acc.get("username") or acc.get("email") or ""
                name = acc.get("full_name") or ident
                disp = (name[:13] + "…") if len(name) > 14 else name
                chip = tk.Button(chips, text=f"👤 {disp}", font=("Segoe UI", 8, "bold"),
                                 bg=self.theme["bg_main"], fg=self.theme["text_primary"], relief="flat",
                                 bd=0, cursor="hand2", padx=8, pady=4, activebackground=self.theme["border"],
                                 command=(lambda i=ident: self._quick_pick_account(i)))
                chip.pack(side="left", padx=(0, 6))
                chip.bind("<Enter>", lambda e, b=chip: b.config(bg=self.theme["border"]))
                chip.bind("<Leave>", lambda e, b=chip: b.config(bg=self.theme["bg_main"]))

        # Username / Email Field
        form_frame = tk.Frame(self.card, bg=self.theme["bg_card"])
        form_frame.pack(fill="x", padx=40)

        tk.Label(form_frame, text=TRANSLATIONS[lang]["username_or_email"], font=("Segoe UI", 10, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(5, 4))
        self.login_cred_entry = tk.Entry(form_frame, font=("Segoe UI", 11), bg=self.theme["bg_main"],
                                         fg=self.theme["text_primary"], insertbackground=self.theme["text_primary"],
                                         highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        self.login_cred_entry.pack(fill="x", ipady=4, pady=(0, 10))
        bind_focus_highlight(self.login_cred_entry, self.theme)

        # Password Field
        tk.Label(form_frame, text=TRANSLATIONS[lang]["password"], font=("Segoe UI", 10, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(5, 4))
        
        pwd_container = tk.Frame(form_frame, bg=self.theme["bg_card"])
        pwd_container.pack(fill="x", pady=(0, 5))
        
        self.login_pwd_entry = tk.Entry(pwd_container, font=("Segoe UI", 11), bg=self.theme["bg_main"], show="*",
                                        fg=self.theme["text_primary"], insertbackground=self.theme["text_primary"],
                                        highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        self.login_pwd_entry.pack(side="left", fill="x", expand=True, ipady=4)
        bind_focus_highlight(self.login_pwd_entry, self.theme)
        
        eye_btn = tk.Button(pwd_container, text="👁", font=("Segoe UI", 10), bg=self.theme["border"], fg=self.theme["text_primary"],
                            relief="flat", activebackground=self.theme["bg_main"], bd=0, cursor="hand2", width=3)
        eye_btn.pack(side="right", fill="y", padx=(2, 0))
        eye_btn.config(command=lambda: self.toggle_password_visibility(self.login_pwd_entry, eye_btn))

        # Forgot Password Link
        forgot_lbl = tk.Label(form_frame, text=TRANSLATIONS[lang]["forgot_pwd_link"], font=("Segoe UI", 9, "underline"),
                              bg=self.theme["bg_card"], fg=self.theme["primary"], cursor="hand2")
        forgot_lbl.pack(anchor="e", pady=(2, 10))
        forgot_lbl.bind("<Button-1>", lambda e: (play_click_sound(), self.show_forgot_view()))

        # Action Buttons
        login_btn = create_flat_button(form_frame, TRANSLATIONS[lang]["login_btn"], self.theme["primary"], "#ffffff",
                                       self._login, hover_bg=self.theme["primary_hover"])
        login_btn.pack(fill="x", ipady=4, pady=(10, 8))

        reg_row = tk.Frame(form_frame, bg=self.theme["bg_card"])
        reg_row.pack(pady=(10, 5))
        
        tk.Label(reg_row, text=TRANSLATIONS[lang]["no_account"], font=("Segoe UI", 9),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(side="left")
        
        reg_link = tk.Label(reg_row, text=TRANSLATIONS[lang]["register_link"], font=("Segoe UI", 9, "bold", "underline"),
                            bg=self.theme["bg_card"], fg=self.theme["success"], cursor="hand2")
        reg_link.pack(side="left", padx=5)
        reg_link.bind("<Button-1>", lambda e: (play_click_sound(), self.show_register_view()))

        exit_app_btn = create_flat_button(form_frame, TRANSLATIONS[lang]["exit_btn"], self.theme["danger"], "#ffffff",
                                          self.parent.confirm_exit, hover_bg=self.theme["danger_hover"])
        exit_app_btn.pack(fill="x", ipady=4, pady=(5, 5))

        # Keyboard Navigation
        self.login_pwd_entry.bind("<Return>", lambda event: self._login())

    def show_register_view(self):
        self.clear_card()
        self.mode = "register"
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=740)

        # Aligned language dropdown + theme toggle (top-right). No back arrow here —
        # the "Back to Login" link at the bottom already covers that navigation.
        self.add_auth_controls()

        lang = self.parent.current_lang

        # Registration Title
        tk.Label(self.card, text=TRANSLATIONS[lang]["create_account_title"], font=("Segoe UI", 14, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(pady=(45, 2))
        tk.Label(self.card, text=TRANSLATIONS[lang]["register_subtitle"], font=("Segoe UI", 9),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 10))

        # Main form container frame (without canvas or scrollbar)
        form_container = tk.Frame(self.card, bg=self.theme["bg_card"])
        form_container.pack(fill="both", expand=True, padx=25, pady=(0, 10))

        label_font = ("Segoe UI", 9, "bold")
        entry_font = ("Segoe UI", 10)

        # Row 1: Full Name and Username
        row1_frame = tk.Frame(form_container, bg=self.theme["bg_card"])
        row1_frame.pack(fill="x", pady=(0, 6))
        row1_frame.columnconfigure(0, weight=1)
        row1_frame.columnconfigure(1, weight=1)

        # Full Name (Column 0)
        fullname_container = tk.Frame(row1_frame, bg=self.theme["bg_card"])
        fullname_container.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(fullname_container, text=TRANSLATIONS[lang]["full_name"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_fullname = tk.Entry(fullname_container, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_fullname.pack(fill="x", ipady=3)
        bind_focus_highlight(self.reg_fullname, self.theme)

        # Username (Column 1)
        username_container = tk.Frame(row1_frame, bg=self.theme["bg_card"])
        username_container.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tk.Label(username_container, text=TRANSLATIONS[lang]["username_opt"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_username = tk.Entry(username_container, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_username.pack(fill="x", ipady=3)
        bind_focus_highlight(self.reg_username, self.theme)
        bind_lowercase(self.reg_username)

        # Email
        tk.Label(form_container, text=TRANSLATIONS[lang]["email"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_email = tk.Entry(form_container, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                  highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_email.pack(fill="x", ipady=3, pady=(0, 6))
        bind_focus_highlight(self.reg_email, self.theme)

        # Row 3: Password and Confirm Password
        row3_frame = tk.Frame(form_container, bg=self.theme["bg_card"])
        row3_frame.pack(fill="x", pady=(0, 6))
        row3_frame.columnconfigure(0, weight=1)
        row3_frame.columnconfigure(1, weight=1)

        # Password (Column 0)
        pwd_container = tk.Frame(row3_frame, bg=self.theme["bg_card"])
        pwd_container.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(pwd_container, text=TRANSLATIONS[lang]["password_req"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        
        pwd_input_frame = tk.Frame(pwd_container, bg=self.theme["bg_card"])
        pwd_input_frame.pack(fill="x")
        self.reg_password = tk.Entry(pwd_input_frame, font=entry_font, bg=self.theme["bg_main"], show="*", fg=self.theme["text_primary"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_password.pack(side="left", fill="x", expand=True, ipady=3)
        bind_focus_highlight(self.reg_password, self.theme)
        eye_btn = tk.Button(pwd_input_frame, text="👁", font=("Segoe UI", 9), bg=self.theme["border"], fg=self.theme["text_primary"],
                            relief="flat", bd=0, cursor="hand2", width=3)
        eye_btn.pack(side="right", fill="y", padx=(2, 0))
        eye_btn.config(command=lambda: self.toggle_password_visibility(self.reg_password, eye_btn))

        # Confirm Password (Column 1)
        pwd_container2 = tk.Frame(row3_frame, bg=self.theme["bg_card"])
        pwd_container2.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tk.Label(pwd_container2, text=TRANSLATIONS[lang]["confirm_password_req"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        
        pwd_input_frame2 = tk.Frame(pwd_container2, bg=self.theme["bg_card"])
        pwd_input_frame2.pack(fill="x")
        self.reg_confirm = tk.Entry(pwd_input_frame2, font=entry_font, bg=self.theme["bg_main"], show="*", fg=self.theme["text_primary"],
                                    highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_confirm.pack(side="left", fill="x", expand=True, ipady=3)
        bind_focus_highlight(self.reg_confirm, self.theme)
        eye_btn2 = tk.Button(pwd_input_frame2, text="👁", font=("Segoe UI", 9), bg=self.theme["border"], fg=self.theme["text_primary"],
                             relief="flat", bd=0, cursor="hand2", width=3)
        eye_btn2.pack(side="right", fill="y", padx=(2, 0))
        eye_btn2.config(command=lambda: self.toggle_password_visibility(self.reg_confirm, eye_btn2))

        # Security Question
        tk.Label(form_container, text=TRANSLATIONS[lang]["security_question_req"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_question = ttk.Combobox(form_container, values=list(SECURITY_QUESTIONS), state="readonly",
                                         style="Auth.TCombobox", font=entry_font)
        self.reg_question.pack(fill="x", pady=(0, 6))
        self.reg_question.set(SECURITY_QUESTIONS[0])

        # Security Answer
        tk.Label(form_container, text=TRANSLATIONS[lang]["security_answer_req"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_answer = tk.Entry(form_container, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                   highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_answer.pack(fill="x", ipady=3, pady=(0, 8))
        bind_focus_highlight(self.reg_answer, self.theme)

        # Academic Info (optional)
        sep_acad = tk.Frame(form_container, bg=self.theme["border"], height=1)
        sep_acad.pack(fill="x", pady=(4, 6))

        acad_hdr = tk.Frame(form_container, bg=self.theme["bg_card"])
        acad_hdr.pack(fill="x", pady=(0, 4))
        tk.Label(acad_hdr, text="Academic Info", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(side="left")
        tk.Label(acad_hdr, text=" — optional", font=("Segoe UI", 8),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(side="left")

        row_acad1 = tk.Frame(form_container, bg=self.theme["bg_card"])
        row_acad1.pack(fill="x", pady=(0, 4))
        row_acad1.columnconfigure(0, weight=1)
        row_acad1.columnconfigure(1, weight=1)

        dept_c = tk.Frame(row_acad1, bg=self.theme["bg_card"])
        dept_c.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(dept_c, text="Department", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_department = tk.Entry(dept_c, font=entry_font, bg=self.theme["bg_main"],
                                       fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_department.pack(fill="x", ipady=3)
        bind_focus_highlight(self.reg_department, self.theme)

        class_c = tk.Frame(row_acad1, bg=self.theme["bg_card"])
        class_c.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tk.Label(class_c, text="Class / Batch", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_class_name = tk.Entry(class_c, font=entry_font, bg=self.theme["bg_main"],
                                       fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_class_name.pack(fill="x", ipady=3)
        bind_focus_highlight(self.reg_class_name, self.theme)

        row_acad2 = tk.Frame(form_container, bg=self.theme["bg_card"])
        row_acad2.pack(fill="x", pady=(0, 10))
        row_acad2.columnconfigure(0, weight=1)
        row_acad2.columnconfigure(1, weight=1)

        sec_c = tk.Frame(row_acad2, bg=self.theme["bg_card"])
        sec_c.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        tk.Label(sec_c, text="Section", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_section = tk.Entry(sec_c, font=entry_font, bg=self.theme["bg_main"],
                                    fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                    highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_section.pack(fill="x", ipady=3)
        bind_focus_highlight(self.reg_section, self.theme)

        batch_c = tk.Frame(row_acad2, bg=self.theme["bg_card"])
        batch_c.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        tk.Label(batch_c, text="Batch Year", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(0, 2))
        self.reg_batch_year = tk.Entry(batch_c, font=entry_font, bg=self.theme["bg_main"],
                                       fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.reg_batch_year.pack(fill="x", ipady=3)
        bind_focus_highlight(self.reg_batch_year, self.theme)

        # Register Button
        reg_btn = create_flat_button(form_container, TRANSLATIONS[lang]["register_btn"], self.theme["success"], "#ffffff",
                                     self._on_register_click, hover_bg=self.theme["success_hover"])
        reg_btn.pack(fill="x", ipady=4, pady=(5, 10))

        # Cancel Link
        cancel_lbl = tk.Label(form_container, text=TRANSLATIONS[lang]["back_to_login"], font=("Segoe UI", 9, "bold", "underline"),
                              bg=self.theme["bg_card"], fg=self.theme["primary"], cursor="hand2")
        cancel_lbl.pack(pady=(0, 5))
        cancel_lbl.bind("<Button-1>", lambda e: (play_click_sound(), self.show_login_view()))

        exit_app_btn = create_flat_button(form_container, TRANSLATIONS[lang]["exit_btn"], self.theme["danger"], "#ffffff",
                                          self.parent.confirm_exit, hover_bg=self.theme["danger_hover"])
        exit_app_btn.pack(fill="x", ipady=4, pady=(5, 5))

    def show_forgot_view(self):
        self.clear_card()
        self.mode = "forgot"
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=360)

        # Aligned language dropdown + theme toggle (top-right)
        self.add_auth_controls()

        # Back button ← (top-left)
        back_btn = tk.Button(
            self.card,
            text="←",
            font=("Segoe UI", 12, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["text_muted"],
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=self.theme["border"],
            activeforeground=self.theme["text_primary"]
        )
        back_btn.place(relx=0.0, rely=0.0, anchor="nw", x=40, y=15)
        back_btn.config(command=lambda: (play_click_sound(), self.show_login_view()))
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg=self.theme["border"], fg=self.theme["text_primary"]))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg=self.theme["bg_card"], fg=self.theme["text_muted"]))

        lang = self.parent.current_lang

        # Forgot Password Title
        tk.Label(self.card, text=TRANSLATIONS[lang]["pwd_recovery_title"], font=("Segoe UI", 15, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(pady=(45, 2))
        tk.Label(self.card, text=TRANSLATIONS[lang]["recovery_subtitle"], font=("Segoe UI", 9),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 15))

        form_frame = tk.Frame(self.card, bg=self.theme["bg_card"])
        form_frame.pack(fill="x", padx=40)

        # Step 1: Input Email
        tk.Label(form_frame, text=TRANSLATIONS[lang]["registered_email"], font=("Segoe UI", 9, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(5, 2))
        self.forgot_email_entry = tk.Entry(form_frame, font=("Segoe UI", 10), bg=self.theme["bg_main"],
                                           fg=self.theme["text_primary"], insertbackground=self.theme["text_primary"],
                                           highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        self.forgot_email_entry.pack(fill="x", ipady=3, pady=(0, 10))
        bind_focus_highlight(self.forgot_email_entry, self.theme)

        # Fetch Security Question Trigger
        fetch_btn = create_flat_button(form_frame, TRANSLATIONS[lang]["load_question_btn"], self.theme["primary"], "#ffffff",
                                       self._forgot_fetch_question, hover_bg=self.theme["primary_hover"])
        fetch_btn.pack(fill="x", ipady=2, pady=5)

        # Divider/Container for Step 2
        self.forgot_step2_frame = tk.Frame(form_frame, bg=self.theme["bg_card"])
        # Hidden initially
        self.forgot_step2_frame.pack_forget()

        # Exit Application Button (at bottom). The top-left ← back arrow already
        # handles returning to login, so no separate "Back to Login" link here.
        self.exit_app_btn = create_flat_button(self.card, TRANSLATIONS[lang]["exit_btn"], self.theme["danger"], "#ffffff",
                                               self.parent.confirm_exit, hover_bg=self.theme["danger_hover"])
        self.exit_app_btn.pack(side="bottom", fill="x", padx=40, pady=(5, 15))

    def _forgot_fetch_question(self):
        email = self.forgot_email_entry.get().strip()
        lang = self.parent.current_lang
        if not email:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_email_required"])
            return

        security_question = self.db.get_security_question(email)
        if not security_question:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_no_user_email"])
            return

        # Show Question, answer input, new password and submit button
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=600)
        self.forgot_step2_frame.pack(fill="x", pady=10)
        self.forgot_email_entry.config(state="disabled") # lock email

        label_font = ("Segoe UI", 9, "bold")
        entry_font = ("Segoe UI", 10)

        # Question label
        tk.Label(self.forgot_step2_frame, text=f"Question: {security_question}", font=("Segoe UI", 9, "italic", "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["warning"], wraplength=350, justify="left").pack(anchor="w", pady=(5, 5))

        # Answer
        tk.Label(self.forgot_step2_frame, text=TRANSLATIONS[lang]["security_answer"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(5, 2))
        self.forgot_ans_entry = tk.Entry(self.forgot_step2_frame, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                         highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.forgot_ans_entry.pack(fill="x", ipady=3, pady=(0, 8))
        bind_focus_highlight(self.forgot_ans_entry, self.theme)

        # New Password
        tk.Label(self.forgot_step2_frame, text=TRANSLATIONS[lang]["new_password"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(5, 2))
        pwd_container = tk.Frame(self.forgot_step2_frame, bg=self.theme["bg_card"])
        pwd_container.pack(fill="x", pady=(0, 8))
        self.forgot_pwd_entry = tk.Entry(pwd_container, font=entry_font, bg=self.theme["bg_main"], show="*", fg=self.theme["text_primary"],
                                         highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.forgot_pwd_entry.pack(side="left", fill="x", expand=True, ipady=3)
        bind_focus_highlight(self.forgot_pwd_entry, self.theme)
        eye_btn = tk.Button(pwd_container, text="👁", font=("Segoe UI", 9), bg=self.theme["border"], fg=self.theme["text_primary"],
                            relief="flat", bd=0, cursor="hand2", width=3)
        eye_btn.pack(side="right", fill="y", padx=(2, 0))
        eye_btn.config(command=lambda: self.toggle_password_visibility(self.forgot_pwd_entry, eye_btn))

        # Confirm Password
        tk.Label(self.forgot_step2_frame, text=TRANSLATIONS[lang]["confirm_new_password"], font=label_font, bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", pady=(5, 2))
        pwd_container2 = tk.Frame(self.forgot_step2_frame, bg=self.theme["bg_card"])
        pwd_container2.pack(fill="x", pady=(0, 15))
        self.forgot_pwd_confirm = tk.Entry(pwd_container2, font=entry_font, bg=self.theme["bg_main"], show="*", fg=self.theme["text_primary"],
                                           highlightbackground=self.theme["border"], highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"])
        self.forgot_pwd_confirm.pack(side="left", fill="x", expand=True, ipady=3)
        bind_focus_highlight(self.forgot_pwd_confirm, self.theme)
        eye_btn2 = tk.Button(pwd_container2, text="👁", font=("Segoe UI", 9), bg=self.theme["border"], fg=self.theme["text_primary"],
                             relief="flat", bd=0, cursor="hand2", width=3)
        eye_btn2.pack(side="right", fill="y", padx=(2, 0))
        eye_btn2.config(command=lambda: self.toggle_password_visibility(self.forgot_pwd_confirm, eye_btn2))

        # Reset Submit Button
        reset_btn = create_flat_button(self.forgot_step2_frame, "🔒 Reset Password", self.theme["primary"], "#ffffff",
                                       self._forgot_submit_reset, hover_bg=self.theme["primary_hover"])
        reset_btn.pack(fill="x", ipady=3, pady=5)

    def _forgot_submit_reset(self):
        email = self.forgot_email_entry.get().strip()
        answer = self.forgot_ans_entry.get().strip()
        new_pwd = self.forgot_pwd_entry.get().strip()
        confirm_pwd = self.forgot_pwd_confirm.get().strip()
        lang = self.parent.current_lang

        if not answer or not new_pwd or not confirm_pwd:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_missing_fields"])
            return

        ok, msg = validate_password_strength(new_pwd)
        if not ok:
            play_error_sound()
            messagebox.showerror("Error", msg)
            return

        if new_pwd != confirm_pwd:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_pwd_match_err"])
            return

        # Fetch question
        question = self.db.get_security_question(email)
        if not question:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_no_user_email"])
            return
        try:
            self.db.reset_password(email, question, answer, new_pwd)
            play_success_sound()
            messagebox.showinfo("Success", TRANSLATIONS[lang]["msg_pwd_reset_success"])
            self.show_login_view()
        except ValueError as exc:
            play_error_sound()
            messagebox.showerror("Error", str(exc))

    def _login(self):
        credential = self.login_cred_entry.get().strip()
        password = self.login_pwd_entry.get().strip()
        lang = self.parent.current_lang

        if not credential or not password:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_fields_required"])
            return

        user = self.db.authenticate_user(credential, password)
        if user is None:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_auth_err"])
            return

        play_success_sound()
        self.on_login_success(user)

    def _on_register_click(self):
        full_name = self.reg_fullname.get().strip()
        email = self.reg_email.get().strip()
        username = self.reg_username.get().strip().lower()
        password = self.reg_password.get().strip()
        confirm = self.reg_confirm.get().strip()
        question = self.reg_question.get()
        answer = self.reg_answer.get().strip()
        lang = self.parent.current_lang

        if not full_name or not email or not password or not confirm or not question or not answer:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_missing_fields"])
            return

        if not validate_full_name(full_name):
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_invalid_name"])
            return

        if not validate_email(email):
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_invalid_email"])
            return

        if username and len(username) < 3:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_invalid_username"])
            return

        ok, msg = validate_password_strength(password)
        if not ok:
            play_error_sound()
            messagebox.showerror("Error", msg)
            return

        if password != confirm:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_pwd_match_err"])
            return

        try:
            user = self.db.register_user(full_name, email, username if username else None, password, question, answer)
            if self.parent.current_lang != "en":
                self.db.change_language(user["id"], self.parent.current_lang)
                user["language"] = self.parent.current_lang
            # Save optional academic info
            dept = getattr(self, "reg_department", None)
            cls_entry = getattr(self, "reg_class_name", None)
            sec_entry = getattr(self, "reg_section", None)
            bat_entry = getattr(self, "reg_batch_year", None)
            dept_val = dept.get().strip() if dept else ""
            cls_val = cls_entry.get().strip() if cls_entry else ""
            sec_val = sec_entry.get().strip() if sec_entry else ""
            bat_val = bat_entry.get().strip() if bat_entry else ""
            if any([dept_val, cls_val, sec_val, bat_val]):
                self.db.update_academic_profile(user["id"], dept_val, cls_val, sec_val, bat_val)
            user["department"] = dept_val
            user["class_name"] = cls_val
            user["section"] = sec_val
            user["batch_year"] = bat_val
            play_success_sound()
            messagebox.showinfo("Success", TRANSLATIONS[lang]["msg_reg_success"])
            self.on_login_success(user)
        except ValueError as exc:
            play_error_sound()
            messagebox.showerror("Error", str(exc))


class PlannerFrame(tk.Frame):
    """Main task manager workspace with responsive sidebar and tab switching."""

    def __init__(self, parent, user, db, app_theme, on_logout_trigger, toggle_theme_callback, current_theme_name, initial_tab="tasks"):
        super().__init__(parent, bg=app_theme["bg_main"])
        self.parent = parent
        self.current_user = user
        self.db = db
        self.theme = app_theme
        self.on_logout_trigger = on_logout_trigger
        self.toggle_theme_callback = toggle_theme_callback
        self.current_theme_name = current_theme_name
        self._initial_tab = initial_tab

        self.manager = TaskManager(DATA_FILE_BASE, db_file=DB_FILE, user_id=self.current_user["id"])
        self.manager.load()

        # Pomodoro Timer State
        self.timer_seconds = 25 * 60
        self.timer_running = False
        self.timer_after_id = None
        self.timer_mode = "Work"  # Work or Break
        self.timer_soundscape = "Silence"
        self.timer_volume = 70
        self.soundscape_playing = False

        # Study Assistant State
        self.ai_conversation = []

        # Study Groups State
        self.selected_group_id = None

        # Create demo study groups for the user if none exist
        self.db.create_demo_groups_for_user_if_none(self.current_user["id"])

        self.active_tab = self._initial_tab # tasks, insights, settings
        self._build_layout()
        self._refresh_tasks_table()

        # Keyboard shortcuts and double-click events for interactive control
        self.tree.bind("<Double-1>", lambda e: self._on_edit_task())
        self.tree.bind("<Delete>", lambda e: self._on_delete_task())
        self.tree.bind("<space>", lambda e: self._on_complete_task() if self.tree.selection() else None)
        
        self.bind_all("<Control-n>", lambda e: self._on_add_task() if self.active_tab == "tasks" else None)
        self.bind_all("<Control-f>", lambda e: self.search_entry.focus_set() if self.active_tab == "tasks" else None)
        self.bind_all("<Control-l>", lambda e: self._logout())

    def _build_layout(self):
        # Grid configs for overall frame
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Frame
        self.sidebar = tk.Frame(self, bg=self.theme["bg_card"], width=230, highlightbackground=self.theme["border"],
                                highlightthickness=1, bd=0)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        # User profile area in sidebar
        avatar = tk.Label(self.sidebar, text="🎓", font=("Segoe UI", 36), bg=self.theme["bg_card"])
        avatar.pack(pady=(15, 2))

        user_name_lbl = tk.Label(self.sidebar, text=self.current_user["full_name"], font=("Segoe UI", 11, "bold"),
                                 bg=self.theme["bg_card"], fg=self.theme["text_primary"], wraplength=210)
        user_name_lbl.pack(padx=10)

        user_email_lbl = tk.Label(self.sidebar, text=self.current_user["email"], font=("Segoe UI", 9),
                                  bg=self.theme["bg_card"], fg=self.theme["text_muted"], wraplength=210)
        user_email_lbl.pack(padx=10, pady=(2, 2))

        _acad_parts = [p for p in [
            self.current_user.get("department", ""),
            self.current_user.get("class_name", ""),
            self.current_user.get("section", ""),
        ] if p]
        if _acad_parts:
            tk.Label(self.sidebar, text=" · ".join(_acad_parts), font=("Segoe UI", 8),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"], wraplength=210).pack(padx=10, pady=(0, 10))
        else:
            tk.Frame(self.sidebar, bg=self.theme["bg_card"], height=10).pack()

        lang = self.parent.current_lang

        # Sidebar navigation tabs
        self.btn_tasks = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_tasks"], self.theme["primary"], "#ffffff",
                                            lambda: self.switch_tab("tasks"), hover_bg=self.theme["primary_hover"])
        self.btn_tasks.pack(fill="x", padx=15, pady=3)

        self.btn_timetable = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_timetable"], self.theme["bg_card"], self.theme["text_primary"],
                                                lambda: self.switch_tab("timetable"), hover_bg=self.theme["border"])
        self.btn_timetable.pack(fill="x", padx=15, pady=3)

        self.btn_timer = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_timer"], self.theme["bg_card"], self.theme["text_primary"],
                                            lambda: self.switch_tab("timer"), hover_bg=self.theme["border"])
        self.btn_timer.pack(fill="x", padx=15, pady=3)

        self.btn_ai = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_ai"], self.theme["bg_card"], self.theme["text_primary"],
                                         lambda: self.switch_tab("ai"), hover_bg=self.theme["border"])
        self.btn_ai.pack(fill="x", padx=15, pady=3)

        self.btn_groups = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_groups"], self.theme["bg_card"], self.theme["text_primary"],
                                             lambda: self.switch_tab("groups"), hover_bg=self.theme["border"])
        self.btn_groups.pack(fill="x", padx=15, pady=3)

        self.btn_insights = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_insights"], self.theme["bg_card"], self.theme["text_primary"],
                                               lambda: self.switch_tab("insights"), hover_bg=self.theme["border"])
        self.btn_insights.pack(fill="x", padx=15, pady=3)

        self.btn_settings = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_settings"], self.theme["bg_card"], self.theme["text_primary"],
                                               lambda: self.switch_tab("settings"), hover_bg=self.theme["border"])
        self.btn_settings.pack(fill="x", padx=15, pady=3)

        self.btn_scratchpad = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_scratchpad"], self.theme["bg_card"], self.theme["text_primary"],
                                                 lambda: self.switch_tab("scratchpad"), hover_bg=self.theme["border"])
        self.btn_scratchpad.pack(fill="x", padx=15, pady=3)

        self.btn_credits = create_flat_button(self.sidebar, TRANSLATIONS[lang]["sidebar_credits"], self.theme["bg_card"], self.theme["text_primary"],
                                              lambda: self.switch_tab("credits"), hover_bg=self.theme["border"])
        self.btn_credits.pack(fill="x", padx=15, pady=3)

        # Bottom components (Logout, theme toggle)
        bottom_frame = tk.Frame(self.sidebar, bg=self.theme["bg_card"])
        bottom_frame.pack(side="bottom", fill="x", pady=10)

        theme_text = TRANSLATIONS[lang]["sidebar_light_mode"] if self.current_theme_name == "dark" else TRANSLATIONS[lang]["sidebar_dark_mode"]
        theme_btn = create_flat_button(bottom_frame, theme_text, self.theme["border"], self.theme["text_primary"],
                                       self.toggle_theme_callback, hover_bg=self.theme["bg_main"], font=("Segoe UI", 9, "bold"))
        theme_btn.pack(fill="x", padx=25, pady=(0, 10))

        # Log Out uses the amber "warning" colour so it stays prominent but is
        # clearly distinct from the red Exit button below it.
        logout_btn = create_flat_button(bottom_frame, TRANSLATIONS[lang]["sidebar_logout"], self.theme["warning"], "#ffffff",
                                         self._logout, hover_bg=self.theme["warning_hover"])
        logout_btn.pack(fill="x", padx=25, pady=(0, 8))

        # Exit (closing the whole app) is the destructive red action; asks first.
        exit_btn = create_flat_button(bottom_frame, TRANSLATIONS[lang].get("exit_btn", "Exit Application"),
                                      self.theme["danger"], "#ffffff",
                                      self.parent.confirm_exit, hover_bg=self.theme["danger_hover"])
        exit_btn.pack(fill="x", padx=25)

        # 2. Main Workspace Content Area
        self.content_frame = tk.Frame(self, bg=self.theme["bg_main"])
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        # Default header (updates dynamically)
        self.header_frame = tk.Frame(self.content_frame, bg=self.theme["bg_main"])
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.header_title = tk.Label(self.header_frame, text=TRANSLATIONS[lang]["workspace_title"], font=("Segoe UI", 16, "bold"),
                                     bg=self.theme["bg_main"], fg=self.theme["text_primary"])
        self.header_title.pack(anchor="w")
        self.header_desc = tk.Label(self.header_frame, text=TRANSLATIONS[lang]["workspace_desc"],
                                    font=("Segoe UI", 9), bg=self.theme["bg_main"], fg=self.theme["text_muted"])
        self.header_desc.pack(anchor="w")

        # Container for changing panels
        self.panel_container = tk.Frame(self.content_frame, bg=self.theme["bg_main"])
        self.panel_container.grid(row=1, column=0, sticky="nsew")
        self.panel_container.grid_columnconfigure(0, weight=1)
        self.panel_container.grid_rowconfigure(0, weight=1)

        # Build individual view widgets inside container
        self._build_tasks_panel()
        self._build_timetable_panel()
        self._build_timer_panel()
        self._build_ai_panel()
        self._build_groups_panel()
        self._build_insights_panel()
        self._build_settings_panel()
        self._build_scratchpad_panel()
        self._build_credits_panel()

        # Set default (or restored) tab
        self.switch_tab(self._initial_tab)

    def switch_tab(self, tab_name):
        # Save scratchpad if navigating away from it
        if getattr(self, "active_tab", None) == "scratchpad" and tab_name != "scratchpad":
            try:
                self._save_scratchpad_notes()
            except Exception:
                pass

        # Stop any ambient soundscape when navigating away from the Focus Timer.
        if tab_name != "timer" and getattr(self, "soundscape_playing", False):
            self._stop_soundscape()

        # Stop LAN discovery when leaving the Groups panel.
        if tab_name != "groups" and getattr(self, "_lan_manager", None) is not None:
            self._stop_lan_discovery()
        self.active_tab = tab_name
        lang = self.parent.current_lang
        
        # Reset sidebar highlights
        buttons = [
            (self.btn_tasks, "tasks"),
            (self.btn_timetable, "timetable"),
            (self.btn_timer, "timer"),
            (self.btn_ai, "ai"),
            (self.btn_groups, "groups"),
            (self.btn_insights, "insights"),
            (self.btn_settings, "settings"),
            (self.btn_scratchpad, "scratchpad"),
            (self.btn_credits, "credits")
        ]
        for btn, name in buttons:
            if name == tab_name:
                # Update the mutable resting colours too, so a hover Leave keeps the
                # active highlight (otherwise it reset to bg_card -> white-on-white).
                btn._base_bg = self.theme["primary"]
                btn._hover_bg = self.theme["primary_hover"]
                btn.config(bg=self.theme["primary"], fg="#ffffff")
            else:
                btn._base_bg = self.theme["bg_card"]
                btn._hover_bg = self.theme["border"]
                btn.config(bg=self.theme["bg_card"], fg=self.theme["text_primary"])

        # Unpack everything in container
        self.tasks_panel.grid_forget()
        self.timetable_panel.grid_forget()
        self.timer_panel.grid_forget()
        self.ai_panel.grid_forget()
        self.groups_panel.grid_forget()
        self.insights_panel.grid_forget()
        self.settings_panel.grid_forget()
        self.scratchpad_panel.grid_forget()
        self.credits_panel.grid_forget()

        if tab_name == "tasks":
            self.header_title.config(text=TRANSLATIONS[lang]["workspace_title"])
            self.header_desc.config(text=TRANSLATIONS[lang]["workspace_desc"])
            self.tasks_panel.grid(row=0, column=0, sticky="nsew")
            self._refresh_tasks_table()
        elif tab_name == "timetable":
            self.header_title.config(text=TRANSLATIONS[lang]["timetable_title"])
            self.header_desc.config(text=TRANSLATIONS[lang]["timetable_desc"])
            self.timetable_panel.grid(row=0, column=0, sticky="nsew")
            self._draw_timetable_content()
        elif tab_name == "timer":
            self.header_title.config(text="FOCUS POMODORO TIMER")
            self.header_desc.config(text="Manage study sessions with structured work/breaks and ambient soundscapes")
            self.timer_panel.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "ai":
            self.header_title.config(text="STUDY ASSISTANT")
            self.header_desc.config(text="Interactive local assistant to explain concepts, summarize tasks, or generate practice material")
            self.ai_panel.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "groups":
            self.header_title.config(text="STUDY GROUPS WORKSPACE")
            self.header_desc.config(text="Collaborative groups dashboard for tracking group tasks and study sessions")
            self.groups_panel.grid(row=0, column=0, sticky="nsew")
            self._refresh_groups_tab()
        elif tab_name == "insights":
            self.header_title.config(text=TRANSLATIONS[lang]["insights_title"])
            self.header_desc.config(text=TRANSLATIONS[lang]["insights_desc"])
            self.insights_panel.grid(row=0, column=0, sticky="nsew")
            self._draw_insights()
        elif tab_name == "settings":
            self.header_title.config(text=TRANSLATIONS[lang]["settings_title"])
            self.header_desc.config(text=TRANSLATIONS[lang]["settings_desc"])
            self.settings_panel.grid(row=0, column=0, sticky="nsew")
        elif tab_name == "scratchpad":
            self.header_title.config(text=TRANSLATIONS[lang]["scratchpad_title"])
            self.header_desc.config(text=TRANSLATIONS[lang]["scratchpad_desc"])
            self.scratchpad_panel.grid(row=0, column=0, sticky="nsew")
            # Set focus to text widget on load
            try:
                self.scratchpad_text.focus_set()
            except Exception:
                pass
        elif tab_name == "credits":
            self.header_title.config(text=TRANSLATIONS[lang]["credits_title"])
            self.header_desc.config(text=TRANSLATIONS[lang]["credits_desc"])
            self.credits_panel.grid(row=0, column=0, sticky="nsew")

    # --- TASKS TAB WORKSPACE ---

    def _build_tasks_panel(self):
        self.tasks_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.tasks_panel.grid_columnconfigure(0, weight=1)
        self.tasks_panel.grid_rowconfigure(1, weight=1)

        lang = self.parent.current_lang

        # Search and Filter Top Bar Card
        bar_card = tk.Frame(self.tasks_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                            highlightthickness=1, bd=0)
        bar_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        p_frame = tk.Frame(bar_card, bg=self.theme["bg_card"])
        p_frame.pack(fill="x", padx=15, pady=12)

        # Keyword
        tk.Label(p_frame, text=TRANSLATIONS[lang]["search"], font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(p_frame, textvariable=self.search_var, width=16, font=("Segoe UI", 10),
                                     bg=self.theme["bg_main"], fg=self.theme["text_primary"], insertbackground=self.theme["text_primary"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        self.search_entry.pack(side="left", padx=(0, 10), ipady=2)
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_tasks_table())
        bind_focus_highlight(self.search_entry, self.theme)

        # Status Filter
        tk.Label(p_frame, text=TRANSLATIONS[lang]["status"], font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(side="left", padx=(0, 4))
        self.filter_status_var = tk.StringVar(value="All")
        self.filter_status_box = ttk.Combobox(p_frame, textvariable=self.filter_status_var, values=["All", "Pending", "Completed", "Overdue"],
                                              state="readonly", width=10, font=("Segoe UI", 9))
        self.filter_status_box.pack(side="left", padx=(0, 10))
        self.filter_status_box.bind("<<ComboboxSelected>>", lambda e: self._refresh_tasks_table())

        # Priority Filter
        tk.Label(p_frame, text=TRANSLATIONS[lang]["priority"], font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(side="left", padx=(0, 4))
        self.filter_priority_var = tk.StringVar(value="All")
        self.filter_priority_box = ttk.Combobox(p_frame, textvariable=self.filter_priority_var, values=["All"] + list(PRIORITY_LEVELS),
                                                state="readonly", width=8, font=("Segoe UI", 9))
        self.filter_priority_box.pack(side="left", padx=(0, 10))
        self.filter_priority_box.bind("<<ComboboxSelected>>", lambda e: self._refresh_tasks_table())

        # Sort Order
        tk.Label(p_frame, text=TRANSLATIONS[lang]["sort_by"], font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(side="left", padx=(0, 4))
        self.sort_var = tk.StringVar(value="Due Date")
        self.sort_box = ttk.Combobox(p_frame, textvariable=self.sort_var, values=["Due Date", "Priority", "Title", "Category"],
                                     state="readonly", width=10, font=("Segoe UI", 9))
        self.sort_box.pack(side="left", padx=(0, 10))
        self.sort_box.bind("<<ComboboxSelected>>", lambda e: self._refresh_tasks_table())

        # Reset button
        clear_btn = create_flat_button(p_frame, TRANSLATIONS[lang]["clear"], self.theme["border"], self.theme["text_primary"],
                                       self._clear_filters, hover_bg=self.theme["bg_main"], font=("Segoe UI", 9, "bold"), padx=10, pady=3)
        clear_btn.pack(side="right")

        # Treeview grid display
        grid_card = tk.Frame(self.tasks_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        grid_card.grid(row=1, column=0, sticky="nsew", pady=5)
        grid_card.grid_columnconfigure(0, weight=1)
        grid_card.grid_rowconfigure(0, weight=1)

        # Style Treeview widget specifically
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure overall treeview appearance
        style.configure("Treeview",
                        background=self.theme["bg_card"],
                        foreground=self.theme["text_primary"],
                        rowheight=35,
                        fieldbackground=self.theme["bg_card"],
                        font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                        background=self.theme["border"],
                        foreground=self.theme["text_primary"],
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[("active", self.theme["primary"]), ("!active", self.theme["border"])],
                  foreground=[("active", "#ffffff"), ("!active", self.theme["text_primary"])])
        style.map("Treeview",
                  background=[("selected", self.theme["primary"])],
                  foreground=[("selected", "#ffffff")])

        # Scrollbar mapping
        style.layout("Vertical.TScrollbar", [
            ('vertical.Scrollbar.trough', {
                'children': [
                    ('vertical.Scrollbar.thumb', {
                        'expand': '1',
                        'sticky': 'nswe'
                    })
                ],
                'sticky': 'ns'
            })
        ])
        style.configure("Vertical.TScrollbar",
                        background=self.theme["scroll_thumb"],
                        troughcolor=self.theme["scroll_trough"],
                        borderwidth=0,
                        bordercolor=self.theme["scroll_trough"],
                        lightcolor=self.theme["scroll_thumb"],
                        darkcolor=self.theme["scroll_thumb"])

        columns = ("id", "title", "category", "priority", "deadline", "status", "days")
        headings = {
            "id": TRANSLATIONS[lang]["col_id"],
            "title": TRANSLATIONS[lang]["col_title"],
            "category": TRANSLATIONS[lang]["col_category"],
            "priority": TRANSLATIONS[lang]["col_priority"],
            "deadline": TRANSLATIONS[lang]["col_deadline"],
            "status": TRANSLATIONS[lang]["col_status"],
            "days": TRANSLATIONS[lang]["days"]
        }
        widths = {"id": 35, "title": 220, "category": 90, "priority": 75, "deadline": 95,
                  "status": 85, "days": 100}

        self.tree = ttk.Treeview(grid_card, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.tree.heading(col, text=headings[col], anchor="w")
            self.tree.column(col, width=widths[col], anchor="w")

        scrollbar = ttk.Scrollbar(grid_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Color row tags
        self.tree.tag_configure("completed", background=self.theme["success_bg"], foreground="#ffffff" if self.current_theme_name == "dark" else "#064e3b")
        self.tree.tag_configure("overdue", background=self.theme["danger_bg"], foreground="#ffffff" if self.current_theme_name == "dark" else "#7f1d1d")

        # Empty-state overlay (shown when the table has no rows). Placed centered
        # over the tree area; toggled in _refresh_tasks_table.
        self.tasks_empty_frame = tk.Frame(grid_card, bg=self.theme["bg_card"])
        tk.Label(self.tasks_empty_frame, text="🗒️", font=("Segoe UI", 40),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack()
        self.tasks_empty_title = tk.Label(self.tasks_empty_frame, text="", font=("Segoe UI", 13, "bold"),
                                          bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        self.tasks_empty_title.pack(pady=(6, 2))
        self.tasks_empty_hint = tk.Label(self.tasks_empty_frame, text="", font=("Segoe UI", 9),
                                         bg=self.theme["bg_card"], fg=self.theme["text_muted"])
        self.tasks_empty_hint.pack()

        # Action Buttons bottom row
        actions_card = tk.Frame(self.tasks_panel, bg=self.theme["bg_main"])
        actions_card.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        create_flat_button(actions_card, TRANSLATIONS[lang]["add_task"], self.theme["primary"], "#ffffff",
                           self._on_add_task, hover_bg=self.theme["primary_hover"]).pack(side="left", padx=(0, 8))
        create_flat_button(actions_card, TRANSLATIONS[lang]["edit_task"], self.theme["warning"], "#ffffff",
                           self._on_edit_task, hover_bg=self.theme["warning_hover"]).pack(side="left", padx=8)
        create_flat_button(actions_card, TRANSLATIONS[lang]["complete_task"], self.theme["success"], "#ffffff",
                           self._on_complete_task, hover_bg=self.theme["success_hover"]).pack(side="left", padx=8)
        create_flat_button(actions_card, TRANSLATIONS[lang]["delete_task"], self.theme["danger"], "#ffffff",
                           self._on_delete_task, hover_bg=self.theme["danger_hover"]).pack(side="left", padx=8)

        # Task counter summary in status label
        self.status_lbl = tk.Label(actions_card, text="0 Tasks loaded.", font=("Segoe UI", 9, "bold"),
                                   bg=self.theme["bg_main"], fg=self.theme["text_muted"])
        self.status_lbl.pack(side="right")

    def _get_filtered_tasks(self):
        tasks = self.manager.get_all()

        # Keyword filter (search title + desc)
        kw = self.search_var.get().strip().lower()
        if kw:
            tasks = [t for t in tasks if kw in t.title.lower() or kw in t.description.lower()]

        # Status filter
        status = self.filter_status_var.get()
        if status == "Pending":
            tasks = [t for t in tasks if not t.is_completed()]
        elif status == "Completed":
            tasks = [t for t in tasks if t.is_completed()]
        elif status == "Overdue":
            tasks = [t for t in tasks if t.is_overdue()]

        # Priority filter
        pri = self.filter_priority_var.get()
        if pri != "All":
            tasks = [t for t in tasks if t.priority == pri]

        # Sorting order
        s_mode = self.sort_var.get()
        if s_mode == "Due Date":
            tasks = sorted(tasks, key=lambda t: t.deadline)
        elif s_mode == "Priority":
            order = {level: index for index, level in enumerate(PRIORITY_LEVELS)}
            tasks = sorted(tasks, key=lambda t: order[t.priority])
        elif s_mode == "Title":
            tasks = sorted(tasks, key=lambda t: t.title.lower())
        elif s_mode == "Category":
            tasks = sorted(tasks, key=lambda t: t.category.lower())

        return tasks

    def _refresh_tasks_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        lang = self.parent.current_lang
        filtered = self._get_filtered_tasks()
        for t in filtered:
            tag = ""
            days_txt = str(t.days_left())
            if t.is_completed():
                tag = "completed"
                days_txt = TRANSLATIONS[lang]["completed_status"]
            elif t.is_overdue():
                tag = "overdue"
                days_txt = TRANSLATIONS[lang]["days_overdue"].format(abs(t.days_left()))
            else:
                days_txt = TRANSLATIONS[lang]["days_left"].format(t.days_left())

            self.tree.insert("", "end", values=(
                t.task_id, t.title, t.category, t.priority,
                t.deadline.strftime(DATE_FORMAT), t.status, days_txt
            ), tags=(tag,))

        total = self.manager.get_summary()["total"]
        completed = self.manager.get_summary()["completed"]
        self.status_lbl.config(text=TRANSLATIONS[lang]["shown_summary"].format(len(filtered), completed, total))

        # Empty-state: distinguish "no tasks yet" from "no matches for filters".
        if not filtered:
            if total == 0:
                self.tasks_empty_title.config(text=TRANSLATIONS[lang].get("empty_tasks_title", "No tasks yet"))
                self.tasks_empty_hint.config(text=TRANSLATIONS[lang].get(
                    "empty_tasks_hint", "Click “Add New Task” to create your first study task."))
            else:
                self.tasks_empty_title.config(text=TRANSLATIONS[lang].get("empty_filter_title", "No matching tasks"))
                self.tasks_empty_hint.config(text=TRANSLATIONS[lang].get(
                    "empty_filter_hint", "Try adjusting your search or filters, or click Clear."))
            self.tasks_empty_frame.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.tasks_empty_frame.place_forget()

    def _clear_filters(self):
        self.search_var.set("")
        self.filter_status_var.set("All")
        self.filter_priority_var.set("All")
        self.sort_var.set("Due Date")
        self._refresh_tasks_table()

    def _get_selected_task_id(self):
        sel = self.tree.selection()
        if not sel:
            play_error_sound()
            messagebox.showwarning("Warning", "Please select a task first.")
            return None
        return int(self.tree.item(sel[0], "values")[0])

    def _on_add_task(self):
        dialog = TaskDialog(self, "Add Study Task", self.theme)
        if getattr(dialog, "result", None) is None:
            return
        title, priority, deadline, desc, category = dialog.result
        self.manager.add_task(title, priority, deadline, desc, category)
        self.manager.save()
        self._refresh_tasks_table()

    def _on_edit_task(self):
        task_id = self._get_selected_task_id()
        if task_id is None:
            return
        task = self.manager.find_by_id(task_id)
        if not task:
            return

        initial = {
            "title": task.title,
            "category": task.category,
            "priority": task.priority,
            "deadline": task.deadline.strftime(DATE_FORMAT),
            "description": task.description
        }
        dialog = TaskDialog(self, "Edit Task Details", self.theme, initial)
        if getattr(dialog, "result", None) is None:
            return
        title, priority, deadline, desc, category = dialog.result
        self.manager.update_task(task_id, title, priority, deadline, desc, category)
        self.manager.save()
        self._refresh_tasks_table()

    def _on_complete_task(self):
        task_id = self._get_selected_task_id()
        if task_id is None:
            return
        self.manager.complete_task(task_id)
        self.manager.save()
        self._refresh_tasks_table()

    def _on_delete_task(self):
        task_id = self._get_selected_task_id()
        if task_id is None:
            return
        task = self.manager.find_by_id(task_id)
        if not task:
            return
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task #{task_id} ('{task.title}')?"):
            self.manager.delete_task(task_id)
            self.manager.save()
            self._refresh_tasks_table()

    # --- INSIGHTS PANEL ---

    def _build_insights_panel(self):
        self.insights_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.insights_panel.grid_columnconfigure(0, weight=1)
        self.insights_panel.grid_columnconfigure(1, weight=1)
        self.insights_panel.grid_rowconfigure(0, weight=1)
        self.insights_panel.grid_rowconfigure(1, weight=1)

        # 4 blocks in grid
        self.canvas_completion = tk.Canvas(self.insights_panel, bg=self.theme["bg_card"], bd=0, highlightthickness=0)
        self.canvas_completion.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        self.canvas_priority = tk.Canvas(self.insights_panel, bg=self.theme["bg_card"], bd=0, highlightthickness=0)
        self.canvas_priority.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        self.canvas_category = tk.Canvas(self.insights_panel, bg=self.theme["bg_card"], bd=0, highlightthickness=0)
        self.canvas_category.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        self.canvas_trends = tk.Canvas(self.insights_panel, bg=self.theme["bg_card"], bd=0, highlightthickness=0)
        self.canvas_trends.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")

    def _draw_insights(self):
        summary = self.manager.get_summary()
        tasks = self.manager.get_all()
        # Charts always render their headings and default 0 values, even with no
        # tasks yet, so the dashboard never looks blank.

        # Canvas dims sizing safety
        self.update_idletasks()
        
        # 1. Completion Circle Gauge (Donut chart)
        c = self.canvas_completion
        c.delete("all")
        w, h = max(c.winfo_width(), 180), max(c.winfo_height(), 180)
        c.create_text(w/2, 22, text="🎯 Task Completion", font=("Segoe UI", 11, "bold"), fill=self.theme["text_primary"])
        
        rate = int((summary["completed"] / summary["total"]) * 100) if summary["total"] > 0 else 0
        
        # Draw Ring
        center_x, center_y = w/2, h/2 + 5
        r = min(w, h) / 4
        c.create_oval(center_x-r, center_y-r, center_x+r, center_y+r, outline=self.theme["border"], width=12)
        if rate > 0:
            extent_angle = -int((rate / 100.0) * 360)
            c.create_arc(center_x-r, center_y-r, center_x+r, center_y+r, start=90, extent=extent_angle, outline=self.theme["success"], width=12, style="arc")
            
        c.create_text(center_x, center_y, text=f"{rate}%", font=("Segoe UI", 18, "bold"), fill=self.theme["text_primary"])
        c.create_text(center_x, center_y + 22, text=f"{summary['completed']}/{summary['total']} Tasks", font=("Segoe UI", 8), fill=self.theme["text_muted"])

        # 2. Priority Breakdown Chart
        c = self.canvas_priority
        c.delete("all")
        w, h = max(c.winfo_width(), 180), max(c.winfo_height(), 180)
        c.create_text(w/2, 22, text="⚡ Priority Distribution", font=("Segoe UI", 11, "bold"), fill=self.theme["text_primary"])

        priorities = [
            ("High", self.theme["danger"], summary["by_priority"].get("High", 0)),
            ("Medium", self.theme["warning"], summary["by_priority"].get("Medium", 0)),
            ("Low", self.theme["primary"], summary["by_priority"].get("Low", 0))
        ]
        
        y_offset = h/2 - 35
        total_p = sum(count for name, color, count in priorities)
        for name, color, count in priorities:
            c.create_text(30, y_offset + 8, text=name, font=("Segoe UI", 9, "bold"), fill=self.theme["text_primary"], anchor="w")
            # Bar back
            c.create_rectangle(90, y_offset, w - 80, y_offset + 14, fill=self.theme["bg_main"], outline="")
            if total_p > 0 and count > 0:
                bar_max = w - 170
                bar_w = int((count / float(total_p)) * bar_max)
                c.create_rectangle(90, y_offset, 90 + bar_w, y_offset + 14, fill=color, outline="")
            c.create_text(w - 70, y_offset + 8, text=f"{count} tasks", font=("Segoe UI", 9), fill=self.theme["text_muted"], anchor="w")
            y_offset += 26

        # 3. Category breakdown Bar Chart
        c = self.canvas_category
        c.delete("all")
        w, h = max(c.winfo_width(), 180), max(c.winfo_height(), 180)
        c.create_text(w/2, 22, text="📂 Category Breakdown", font=("Segoe UI", 11, "bold"), fill=self.theme["text_primary"])

        cats = {}
        for t in tasks:
            cats[t.category] = cats.get(t.category, 0) + 1
        
        cats_sorted = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:5] # top 5
        
        if not cats_sorted:
            c.create_text(w/2, h/2, text="No tasks to classify", font=("Segoe UI", 9, "italic"), fill=self.theme["text_muted"])
        else:
            y_offset = h/2 - 40
            max_count = max(count for name, count in cats_sorted)
            for name, count in cats_sorted:
                # Truncate category name
                disp_name = (name[:10] + "..") if len(name) > 12 else name
                c.create_text(30, y_offset + 8, text=disp_name, font=("Segoe UI", 9, "bold"), fill=self.theme["text_primary"], anchor="w")
                
                c.create_rectangle(90, y_offset, w - 80, y_offset + 14, fill=self.theme["bg_main"], outline="")
                if max_count > 0 and count > 0:
                    bar_max = w - 170
                    bar_w = int((count / float(max_count)) * bar_max)
                    c.create_rectangle(90, y_offset, 90 + bar_w, y_offset + 14, fill=self.theme["primary"], outline="")
                c.create_text(w - 70, y_offset + 8, text=f"{count} tasks", font=("Segoe UI", 9), fill=self.theme["text_muted"], anchor="w")
                y_offset += 20

        # 4. Weekly Productivity Trends (tasks due inside -3 to +3 days)
        c = self.canvas_trends
        c.delete("all")
        w, h = max(c.winfo_width(), 180), max(c.winfo_height(), 180)
        c.create_text(w/2, 22, text="📈 Study Schedule Load (Next 5 Days)", font=("Segoe UI", 11, "bold"), fill=self.theme["text_primary"])

        # Count tasks due on each of the next 5 days
        today = date.today()
        days = [today + timedelta(days=i) for i in range(5)]
        day_labels = [d.strftime("%m/%d") for d in days]
        counts = []
        for d in days:
            counts.append(sum(1 for t in tasks if t.deadline == d and not t.is_completed()))

        if max(counts, default=0) == 0:
            c.create_text(w/2, h/2, text="No pending tasks due in the next 5 days", font=("Segoe UI", 9, "italic"), fill=self.theme["text_muted"], justify="center", width=180)
        else:
            # Draw line graph
            padding_x = 45
            padding_y = 45
            graph_w = w - (padding_x * 2)
            graph_h = h - (padding_y * 2) - 10
            
            max_val = max(counts)
            if max_val == 0:
                max_val = 1
                
            points = []
            for i, count in enumerate(counts):
                x = padding_x + (i * (graph_w / 4.0))
                y = h - padding_y - (count * (graph_h / float(max_val)))
                points.append((x, y))

            # Draw axes
            c.create_line(padding_x, h - padding_y, w - padding_x, h - padding_y, fill=self.theme["border"], width=1)
            c.create_line(padding_x, padding_y, padding_x, h - padding_y, fill=self.theme["border"], width=1)

            # Draw line & points
            for i in range(len(points) - 1):
                c.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=self.theme["primary"], width=2)
            
            for i, (x, y) in enumerate(points):
                c.create_oval(x-3, y-3, x+3, y+3, fill=self.theme["warning"], outline="")
                # Label date under axis
                c.create_text(x, h - padding_y + 12, text=day_labels[i], font=("Segoe UI", 8), fill=self.theme["text_muted"])
                # Label value above point
                c.create_text(x, y - 10, text=str(counts[i]), font=("Segoe UI", 8, "bold"), fill=self.theme["text_primary"])

    # --- PROFILE SETTINGS TAB ---

    def _build_settings_panel(self):
        self.settings_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.settings_panel.grid_columnconfigure(0, weight=1)

        lang = self.parent.current_lang
        label_font = ("Segoe UI", 9, "bold")
        entry_font = ("Segoe UI", 10)

        # Update Profile Card (name, username, email)
        profile_card = tk.Frame(self.settings_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                                highlightthickness=1, bd=0)
        profile_card.grid(row=0, column=0, sticky="ew", pady=10, padx=5)

        tk.Label(profile_card, text=TRANSLATIONS[lang].get("profile_card", "👤 Update Profile"),
                 font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        profile_form = tk.Frame(profile_card, bg=self.theme["bg_card"])
        profile_form.pack(fill="x", padx=20, pady=(0, 20))
        # Fixed label column so fields/buttons line up with the Password card below.
        profile_form.columnconfigure(0, minsize=170)

        # Full Name
        tk.Label(profile_form, text=TRANSLATIONS[lang].get("full_name_label", "Full Name"), font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", pady=5)
        self.set_fullname = tk.Entry(profile_form, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0,
                                     insertbackground=self.theme["text_primary"], width=30)
        self.set_fullname.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.set_fullname.insert(0, self.current_user.get("full_name", ""))
        bind_focus_highlight(self.set_fullname, self.theme)

        # Username (forced lowercase)
        tk.Label(profile_form, text=TRANSLATIONS[lang].get("username_label", "Username"), font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=1, column=0, sticky="w", pady=5)
        self.set_username = tk.Entry(profile_form, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0,
                                     insertbackground=self.theme["text_primary"], width=30)
        self.set_username.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.set_username.insert(0, self.current_user.get("username") or "")
        bind_focus_highlight(self.set_username, self.theme)
        bind_lowercase(self.set_username)

        # Email
        tk.Label(profile_form, text=TRANSLATIONS[lang].get("email_label", "Email"), font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=2, column=0, sticky="w", pady=5)
        self.set_email = tk.Entry(profile_form, font=entry_font, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                  highlightbackground=self.theme["border"], highlightthickness=1, bd=0,
                                  insertbackground=self.theme["text_primary"], width=30)
        self.set_email.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.set_email.insert(0, self.current_user.get("email", ""))
        bind_focus_highlight(self.set_email, self.theme)

        save_profile_btn = create_flat_button(profile_form, TRANSLATIONS[lang].get("update_profile_btn", "💾 Save Profile"),
                                               self.theme["primary"], "#ffffff", self._on_update_profile,
                                               hover_bg=self.theme["primary_hover"])
        save_profile_btn.grid(row=3, column=1, sticky="w", padx=10, pady=15)

        # Academic Profile Card
        acad_card = tk.Frame(self.settings_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        acad_card.grid(row=1, column=0, sticky="ew", pady=10, padx=5)

        tk.Label(acad_card, text="🎓 Academic Profile", font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        acad_form = tk.Frame(acad_card, bg=self.theme["bg_card"])
        acad_form.pack(fill="x", padx=20, pady=(0, 20))
        acad_form.columnconfigure(0, minsize=170)

        tk.Label(acad_form, text="Department", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", pady=5)
        self.set_department = tk.Entry(acad_form, font=entry_font, bg=self.theme["bg_main"],
                                       fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"], width=30)
        self.set_department.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.set_department.insert(0, self.current_user.get("department", ""))
        bind_focus_highlight(self.set_department, self.theme)

        tk.Label(acad_form, text="Class / Batch", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=1, column=0, sticky="w", pady=5)
        self.set_class_name = tk.Entry(acad_form, font=entry_font, bg=self.theme["bg_main"],
                                       fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"], width=30)
        self.set_class_name.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        self.set_class_name.insert(0, self.current_user.get("class_name", ""))
        bind_focus_highlight(self.set_class_name, self.theme)

        tk.Label(acad_form, text="Section", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=2, column=0, sticky="w", pady=5)
        self.set_section = tk.Entry(acad_form, font=entry_font, bg=self.theme["bg_main"],
                                    fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                    highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"], width=30)
        self.set_section.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        self.set_section.insert(0, self.current_user.get("section", ""))
        bind_focus_highlight(self.set_section, self.theme)

        tk.Label(acad_form, text="Batch Year", font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=3, column=0, sticky="w", pady=5)
        self.set_batch_year = tk.Entry(acad_form, font=entry_font, bg=self.theme["bg_main"],
                                       fg=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                       highlightthickness=1, bd=0, insertbackground=self.theme["text_primary"], width=30)
        self.set_batch_year.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        self.set_batch_year.insert(0, self.current_user.get("batch_year", ""))
        bind_focus_highlight(self.set_batch_year, self.theme)

        save_acad_btn = create_flat_button(acad_form, "💾 Save Academic Info", self.theme["primary"], "#ffffff",
                                           self._on_update_academic_profile, hover_bg=self.theme["primary_hover"])
        save_acad_btn.grid(row=4, column=1, sticky="w", padx=10, pady=15)

        # Change Password Card
        pwd_card = tk.Frame(self.settings_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                            highlightthickness=1, bd=0)
        pwd_card.grid(row=2, column=0, sticky="ew", pady=10, padx=5)

        tk.Label(pwd_card, text=TRANSLATIONS[lang]["change_pwd_card"], font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        form_frame = tk.Frame(pwd_card, bg=self.theme["bg_card"])
        form_frame.pack(fill="x", padx=20, pady=(0, 20))
        # Same fixed label column as the Profile card so fields/buttons line up.
        form_frame.columnconfigure(0, minsize=170)

        self.set_pwd_old = self._make_pw_field(form_frame, 0, TRANSLATIONS[lang]["current_password"], eye=False)
        self.set_pwd_new = self._make_pw_field(form_frame, 1, TRANSLATIONS[lang]["new_password_label"])
        self.set_pwd_confirm = self._make_pw_field(form_frame, 2, TRANSLATIONS[lang]["confirm_new_pwd_label"])

        # Submit change password button (aligned with the Save Profile button above)
        change_btn = create_flat_button(form_frame, TRANSLATIONS[lang]["update_pwd_btn"], self.theme["primary"], "#ffffff",
                                        self._on_change_password, hover_bg=self.theme["primary_hover"])
        change_btn.grid(row=3, column=1, sticky="w", padx=10, pady=15)

        # Language Settings Card
        lang_card = tk.Frame(self.settings_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        lang_card.grid(row=3, column=0, sticky="ew", pady=10, padx=5)

        tk.Label(lang_card, text=TRANSLATIONS[lang]["lang_pref_card"], font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        lang_frame = tk.Frame(lang_card, bg=self.theme["bg_card"])
        lang_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(lang_frame, text=TRANSLATIONS[lang]["lang_pref_label"], font=label_font,
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", pady=5)
        
        # Proper themed dropdown language selector (consistent with the auth screen).
        languages = [
            ("English", "en"), ("Deutsch", "de"), ("Español", "es"), ("Français", "fr"),
            ("Русский", "ru"), ("中文", "zh"), ("日本語", "ja"), ("한국어", "ko"),
            ("हिन्दी", "hi"), ("اردو", "ur"), ("العربية", "ar"), ("فارسی", "fa")
        ]
        code_to_name = {code: name for name, code in languages}
        name_to_code = {name: code for name, code in languages}

        self._style_settings_combobox()
        self.lang_setting_combo = ttk.Combobox(
            lang_frame,
            values=[name for name, _ in languages],
            state="readonly",
            style="Settings.TCombobox",
            font=entry_font,
            width=16
        )
        self.lang_setting_combo.set(code_to_name.get(self.parent.current_lang, "English"))
        self.lang_setting_combo.grid(row=0, column=1, sticky="w", padx=10, pady=5, ipady=2)
        self.lang_setting_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: (self.lang_setting_combo.selection_clear(),
                       self._update_language_setting(name_to_code[self.lang_setting_combo.get()]))
        )

        # Preferences Card (Sound effects toggle)
        pref_card = tk.Frame(self.settings_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        pref_card.grid(row=4, column=0, sticky="ew", pady=10, padx=5)

        tk.Label(pref_card, text=TRANSLATIONS[lang].get("sound_pref_card", "🔊 Sound & Feedback"),
                 font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        pref_frame = tk.Frame(pref_card, bg=self.theme["bg_card"])
        pref_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.sound_enabled_var = tk.BooleanVar(value=is_sound_enabled())
        sound_chk = tk.Checkbutton(
            pref_frame,
            text=TRANSLATIONS[lang].get("sound_toggle_label", "Enable interface sound effects"),
            variable=self.sound_enabled_var,
            command=self._on_toggle_sound,
            font=("Segoe UI", 10),
            bg=self.theme["bg_card"], fg=self.theme["text_primary"],
            activebackground=self.theme["bg_card"], activeforeground=self.theme["text_primary"],
            selectcolor=self.theme["bg_main"],
            highlightthickness=0, bd=0, cursor="hand2", anchor="w"
        )
        sound_chk.pack(anchor="w")

        # Data Management & Academic Reports Card
        data_card = tk.Frame(self.settings_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        data_card.grid(row=5, column=0, sticky="ew", pady=10, padx=5)

        tk.Label(data_card, text="📊 Academic Reports & Data Export", font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(anchor="w", padx=20, pady=(15, 10))

        data_frame = tk.Frame(data_card, bg=self.theme["bg_card"])
        data_frame.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(data_frame, text="Generate detailed progress reports or export your task records to standard CSV files:", font=("Segoe UI", 9),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(anchor="w", pady=(0, 10))

        btn_row = tk.Frame(data_frame, bg=self.theme["bg_card"])
        btn_row.pack(fill="x")

        # Export CSV Button
        export_btn = create_flat_button(
            btn_row, 
            TRANSLATIONS[lang]["export_csv_btn"], 
            self.theme["primary"], 
            "#ffffff",
            self._export_tasks_csv, 
            hover_bg=self.theme["primary_hover"]
        )
        export_btn.pack(side="left", padx=(0, 10))

        # Generate Summary Button
        summary_btn = create_flat_button(
            btn_row, 
            TRANSLATIONS[lang]["gen_summary_btn"], 
            self.theme["success"], 
            "#ffffff",
            self._generate_study_summary, 
            hover_bg=self.theme["success_hover"]
        )
        summary_btn.pack(side="left", padx=10)

    def _build_scratchpad_panel(self):
        self.scratchpad_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.scratchpad_panel.grid_columnconfigure(0, weight=1)
        self.scratchpad_panel.grid_rowconfigure(0, weight=1)

        # Main wrapper card
        card = tk.Frame(self.scratchpad_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                        highlightthickness=1, bd=0)
        card.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        lang = self.parent.current_lang

        # Top Button controls bar inside card
        controls_frame = tk.Frame(card, bg=self.theme["bg_card"])
        controls_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        # Statistics Label
        self.stats_var = tk.StringVar(value=TRANSLATIONS[lang]["scratchpad_stats"].format(0, 0, 0))
        stats_lbl = tk.Label(controls_frame, textvariable=self.stats_var, font=("Segoe UI", 9, "bold"),
                             bg=self.theme["bg_card"], fg=self.theme["text_muted"])
        stats_lbl.pack(side="left")

        # Action Buttons on Right
        export_btn = create_flat_button(
            controls_frame,
            TRANSLATIONS[lang]["scratchpad_export_btn"],
            self.theme["success"],
            "#ffffff",
            self._export_scratchpad_note,
            hover_bg=self.theme["success_hover"]
        )
        export_btn.pack(side="right", padx=(10, 0))

        clear_btn = create_flat_button(
            controls_frame,
            TRANSLATIONS[lang]["scratchpad_clear_btn"],
            self.theme["danger"],
            "#ffffff",
            self._clear_scratchpad_note,
            hover_bg=self.theme["danger_hover"]
        )
        clear_btn.pack(side="right")

        # Text Area with scrollbar
        text_container = tk.Frame(card, bg=self.theme["bg_card"])
        text_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        text_container.grid_columnconfigure(0, weight=1)
        text_container.grid_rowconfigure(0, weight=1)

        # Custom scrollbar style
        scrollbar = tk.Scrollbar(text_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.scratchpad_text = tk.Text(
            text_container,
            font=("Consolas", 11) if self.current_theme_name == "dark" else ("Segoe UI", 11),
            bg=self.theme["bg_main"],
            fg=self.theme["text_primary"],
            insertbackground=self.theme["text_primary"],
            highlightbackground=self.theme["border"],
            highlightthickness=1,
            bd=0,
            yscrollcommand=scrollbar.set,
            wrap="word",
            padx=10,
            pady=10
        )
        self.scratchpad_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.scratchpad_text.yview)
        bind_focus_highlight(self.scratchpad_text, self.theme)

        # Load existing notes
        notes_content = self.db.get_scratchpad(self.current_user["id"])
        if notes_content:
            self.scratchpad_text.insert("1.0", notes_content)
        else:
            # Show localized placeholder
            placeholder = TRANSLATIONS[lang]["scratchpad_placeholder"]
            self.scratchpad_text.insert("1.0", placeholder)
            self.scratchpad_text.config(fg=self.theme["text_muted"])
            self.scratchpad_placeholder_active = True

        # Event binds for statistics and auto-save
        self.scratchpad_text.bind("<KeyRelease>", self._on_scratchpad_key)
        self.scratchpad_text.bind("<FocusIn>", self._on_scratchpad_focus_in)
        self.scratchpad_text.bind("<FocusOut>", self._on_scratchpad_focus_out)

        # Track if placeholder is active
        if not notes_content:
            self.scratchpad_placeholder_active = True
        else:
            self.scratchpad_placeholder_active = False
            self._update_scratchpad_stats()

    def _on_scratchpad_focus_in(self, event=None):
        if getattr(self, "scratchpad_placeholder_active", False):
            self.scratchpad_text.delete("1.0", "end-1c")
            self.scratchpad_text.config(fg=self.theme["text_primary"])
            self.scratchpad_placeholder_active = False

    def _on_scratchpad_focus_out(self, event=None):
        content = self.scratchpad_text.get("1.0", "end-1c").strip()
        if not content:
            lang = self.parent.current_lang
            placeholder = TRANSLATIONS[lang]["scratchpad_placeholder"]
            self.scratchpad_text.delete("1.0", "end-1c")
            self.scratchpad_text.insert("1.0", placeholder)
            self.scratchpad_text.config(fg=self.theme["text_muted"])
            self.scratchpad_placeholder_active = True
        else:
            self._save_scratchpad_notes()

    def _on_scratchpad_key(self, event=None):
        if getattr(self, "scratchpad_placeholder_active", False):
            return
        self._update_scratchpad_stats()
        self._save_scratchpad_notes()

    def _update_scratchpad_stats(self):
        if getattr(self, "scratchpad_placeholder_active", False):
            word_count = 0
            char_count = 0
            para_count = 0
        else:
            text = self.scratchpad_text.get("1.0", "end-1c")
            char_count = len(text)
            words = text.split()
            word_count = len(words)
            paras = [p for p in text.split("\n") if p.strip()]
            para_count = len(paras)

        lang = self.parent.current_lang
        self.stats_var.set(TRANSLATIONS[lang]["scratchpad_stats"].format(word_count, char_count, para_count))

    def _save_scratchpad_notes(self):
        if getattr(self, "scratchpad_placeholder_active", False):
            content = ""
        else:
            content = self.scratchpad_text.get("1.0", "end-1c")
        self.db.save_scratchpad(self.current_user["id"], content)

    def _clear_scratchpad_note(self):
        lang = self.parent.current_lang
        title = TRANSLATIONS[lang]["scratchpad_clear_confirm_title"]
        msg = TRANSLATIONS[lang]["scratchpad_clear_confirm_msg"]
        play_click_sound()
        if messagebox.askyesno(title, msg, parent=self):
            self.scratchpad_text.delete("1.0", "end")
            placeholder = TRANSLATIONS[lang]["scratchpad_placeholder"]
            self.scratchpad_text.insert("1.0", placeholder)
            self.scratchpad_text.config(fg=self.theme["text_muted"])
            self.scratchpad_placeholder_active = True
            self._update_scratchpad_stats()
            self._save_scratchpad_notes()
            play_success_sound()

    def _export_scratchpad_note(self):
        play_click_sound()
        if getattr(self, "scratchpad_placeholder_active", False):
            content = ""
        else:
            content = self.scratchpad_text.get("1.0", "end-1c")
        if not content.strip():
            play_error_sound()
            return

        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Export Study Note"
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                play_success_sound()
                lang = self.parent.current_lang
                messagebox.showinfo("Export Success", TRANSLATIONS[lang]["scratchpad_save_success"], parent=self)
            except Exception as exc:
                play_error_sound()
                messagebox.showerror("Error", f"Failed to export note: {exc}", parent=self)

    def _build_credits_panel(self):
        self.credits_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.credits_panel.grid_columnconfigure(0, weight=1)
        self.credits_panel.grid_rowconfigure(0, weight=1)

        self._add_particle_bg(self.credits_panel)

        lang = self.parent.current_lang

        card = tk.Frame(self.credits_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                        highlightthickness=1, bd=0)
        card.grid(row=0, column=0)

        inner = tk.Frame(card, bg=self.theme["bg_card"])
        inner.pack(padx=56, pady=40)

        # App identity
        tk.Label(inner, text="Smart Study Planner", font=("Segoe UI", 26, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(pady=(0, 4))
        tk.Label(inner, text='Version 1.2.5 "Apex"', font=("Segoe UI", 11, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(pady=(0, 6))
        tk.Label(inner,
                 text="A secure, dual-interface desktop planner for managing\n"
                      "academic coursework, deadlines, exams, and milestones.",
                 font=("Segoe UI", 10), justify="center",
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 18))

        tk.Frame(inner, bg=self.theme["border"], height=1, width=560).pack(pady=(0, 18))

        tk.Label(inner, text="CONTRIBUTORS", font=("Segoe UI", 10, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 14))

        # 2x2 contributor grid
        CONTRIBUTORS = [
            {
                "name": "Mohammad Sufiyan Aasim",
                "handle": "@SufiyanAasim",
                "role": "System Architect · AI/MLOps · Documentation",
                "email": "sufiyanaasim@outlook.com",
                "github": "https://github.com/SufiyanAasim",
            },
            {
                "name": "Fahad Bin Nasir",
                "handle": "@FahadBinNasir",
                "role": "Back-end Development",
                "email": "fahadabbasi17025@gmail.com",
                "github": "https://github.com/FahadBinNasir",
            },
            {
                "name": "Ifrahim Yousuf",
                "handle": "@ifrahim-yousaf",
                "role": "UI/UX Designer · Front-end Development",
                "email": "ifrahimsf@gmail.com",
                "github": "https://github.com/ifrahim-yousaf",
            },
            {
                "name": "Taha Siddiqui",
                "handle": "@13eeCoder",
                "role": "Networking & Cyber Security",
                "email": "tahasiddiqui2100@gmail.com",
                "github": "https://github.com/13eeCoder",
            },
        ]

        grid_frame = tk.Frame(inner, bg=self.theme["bg_card"])
        grid_frame.pack()

        for idx, contributor in enumerate(CONTRIBUTORS):
            row, col = divmod(idx, 2)

            cell = tk.Frame(grid_frame, bg=self.theme["bg_card"],
                            highlightbackground=self.theme["border"], highlightthickness=1)
            cell.grid(row=row, column=col, padx=10, pady=8, sticky="nsew", ipadx=22, ipady=18)

            tk.Label(cell, text=contributor["name"], font=("Segoe UI", 14, "bold"),
                     bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(pady=(0, 3))
            tk.Label(cell, text=contributor["role"], font=("Segoe UI", 9, "italic"),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 10))

            email_lbl = tk.Label(cell, text=contributor["email"],
                                 font=("Segoe UI", 10, "underline"),
                                 bg=self.theme["bg_card"], fg=self.theme["primary"], cursor="hand2")
            email_lbl.pack(pady=(0, 3))
            email_lbl.bind("<Button-1>", lambda e, em=contributor["email"]: self._copy_email(em))

            tk.Label(cell, text=TRANSLATIONS[lang]["credits_copy_hint"], font=("Segoe UI", 8),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 10))

            create_flat_button(
                cell,
                TRANSLATIONS[lang]["credits_github_btn"],
                self.theme["success"], "#ffffff",
                lambda url=contributor["github"]: self._open_url(url),
                hover_bg=self.theme["success_hover"],
                font=("Segoe UI", 9, "bold"), padx=14, pady=6
            ).pack()

        tk.Frame(inner, bg=self.theme["border"], height=1, width=560).pack(pady=(20, 12))
        tk.Label(inner, text="MIT License © 2026 Smart Study Planner Contributors",
                 font=("Segoe UI", 9), bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack()

    def _copy_email(self, email):
        self.parent.clipboard_clear()
        self.parent.clipboard_append(email)
        self.parent.update()
        play_success_sound()
        messagebox.showinfo("Clipboard", TRANSLATIONS[self.parent.current_lang]["credits_email_copied"])

    def _open_url(self, url):
        import webbrowser
        webbrowser.open_new_tab(url)

    def _build_timetable_panel(self):
        self.timetable_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.timetable_panel.grid_columnconfigure(0, weight=1)
        self.timetable_panel.grid_rowconfigure(1, weight=1)

        lang = self.parent.current_lang

        # Top Bar: Segment Control & Action Button
        top_bar = tk.Frame(self.timetable_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                           highlightthickness=1, bd=0)
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        bar_frame = tk.Frame(top_bar, bg=self.theme["bg_card"])
        bar_frame.pack(fill="x", padx=15, pady=10)

        self.timetable_view_mode = "week" # default
        
        self.btn_view_week = create_flat_button(
            bar_frame, 
            TRANSLATIONS[lang]["view_week"], 
            self.theme["primary"], 
            "#ffffff",
            lambda: self._switch_timetable_view("week"),
            font=("Segoe UI", 9, "bold")
        )
        self.btn_view_week.pack(side="left", padx=5)

        self.btn_view_month = create_flat_button(
            bar_frame, 
            TRANSLATIONS[lang]["view_month"], 
            self.theme["bg_card"], 
            self.theme["text_primary"],
            lambda: self._switch_timetable_view("month"),
            hover_bg=self.theme["border"],
            font=("Segoe UI", 9, "bold")
        )
        self.btn_view_month.pack(side="left", padx=5)

        self.btn_view_6month = create_flat_button(
            bar_frame, 
            TRANSLATIONS[lang]["view_6month"], 
            self.theme["bg_card"], 
            self.theme["text_primary"],
            lambda: self._switch_timetable_view("6month"),
            hover_bg=self.theme["border"],
            font=("Segoe UI", 9, "bold")
        )
        self.btn_view_6month.pack(side="left", padx=5)

        gen_btn = create_flat_button(
            bar_frame,
            TRANSLATIONS[lang]["timetable_gen_btn"],
            self.theme["success"],
            "#ffffff",
            self._generate_timetable_schedule,
            hover_bg=self.theme["success_hover"]
        )
        gen_btn.pack(side="right", padx=5)

        export_ics_btn = create_flat_button(
            bar_frame,
            "Export Calendar (ICS)",
            self.theme["primary"],
            "#ffffff",
            self._export_timetable_ics,
            hover_bg=self.theme["primary_hover"]
        )
        export_ics_btn.pack(side="right", padx=5)

        self.timetable_canvas = tk.Canvas(self.timetable_panel, bg=self.theme["bg_main"], bd=0, highlightthickness=0)
        self.timetable_scrollbar = ttk.Scrollbar(self.timetable_panel, orient="vertical", command=self.timetable_canvas.yview)
        
        self.timetable_scrollable_frame = tk.Frame(self.timetable_canvas, bg=self.theme["bg_main"])
        self.timetable_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.timetable_canvas.configure(scrollregion=self.timetable_canvas.bbox("all"))
        )
        
        self.timetable_canvas_window = self.timetable_canvas.create_window((0, 0), window=self.timetable_scrollable_frame, anchor="nw")
        self.timetable_canvas.configure(yscrollcommand=self.timetable_scrollbar.set)
        
        self.timetable_canvas.grid(row=1, column=0, sticky="nsew")
        self.timetable_scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.timetable_canvas.bind("<Configure>", lambda e: self.timetable_canvas.itemconfig(self.timetable_canvas_window, width=e.width))

        def _on_mousewheel(event):
            self.timetable_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        def _bind_mousewheel(event):
            self.timetable_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            self.timetable_canvas.unbind_all("<MouseWheel>")
            
        self.timetable_canvas.bind("<Enter>", _bind_mousewheel)
        self.timetable_canvas.bind("<Leave>", _unbind_mousewheel)

    def _switch_timetable_view(self, mode):
        self.timetable_view_mode = mode
        play_click_sound()
        
        for btn, m in [(self.btn_view_week, "week"), (self.btn_view_month, "month"), (self.btn_view_6month, "6month")]:
            if m == mode:
                btn.config(bg=self.theme["primary"], fg="#ffffff")
            else:
                btn.config(bg=self.theme["bg_card"], fg=self.theme["text_primary"])
                
        self._draw_timetable_content()

    def _generate_timetable_schedule(self):
        play_success_sound()
        messagebox.showinfo("Success", "Study plan generated successfully! Distributed study sessions across daily slots and monthly milestones based on task priorities.")
        self._draw_timetable_content()

    def _export_timetable_ics(self):
        play_click_sound()
        tasks = [t for t in self.manager.tasks if t.status != "Completed"]
        if not tasks:
            messagebox.showwarning("No Tasks", "No active tasks available to export to calendar.")
            return

        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar Files", "*.ics")],
            title="Export Calendar (ICS)"
        )
        if not file_path:
            return

        import datetime
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Smart Study Planner//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

        for t in tasks:
            dl = t.deadline
            # deadline is a date object; tolerate a string fallback just in case.
            if hasattr(dl, "strftime"):
                dl_date = dl
            else:
                try:
                    dl_date = datetime.datetime.strptime(str(dl), "%Y-%m-%d").date()
                except Exception:
                    dl_date = datetime.date.today()

            clean_dl = dl_date.strftime("%Y%m%d")
            next_dl = (dl_date + datetime.timedelta(days=1)).strftime("%Y%m%d")

            desc = t.description or ""
            desc = desc.replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")
            title = t.title.replace(",", "\\,").replace(";", "\\;")

            prio_num = "5"
            if t.priority == "High":
                prio_num = "1"
            elif t.priority == "Medium":
                prio_num = "5"
            elif t.priority == "Low":
                prio_num = "9"

            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:task_{t.task_id}_{clean_dl}@smartstudyplanner.local",
                f"DTSTAMP:{now_str}",
                f"DTSTART;VALUE=DATE:{clean_dl}",
                f"DTEND;VALUE=DATE:{next_dl}",
                f"SUMMARY:{title} [{t.category}]",
                f"DESCRIPTION:{desc}\\nPriority: {t.priority}",
                f"PRIORITY:{prio_num}",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

        ics_lines.append("END:VCALENDAR")
        ics_content = "\n".join(ics_lines)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(ics_content)
            play_success_sound()
            messagebox.showinfo("Success", f"Calendar successfully exported to {file_path}!")
        except Exception as e:
            play_error_sound()
            messagebox.showerror("Error", f"Failed to export calendar: {e}")

    def _draw_timetable_content(self):
        for widget in self.timetable_scrollable_frame.winfo_children():
            widget.destroy()

        pending_tasks = [t for t in self.manager.tasks if t.status != "Completed"]
        
        if not pending_tasks:
            lang = self.parent.current_lang
            # Empty-state card (icon + title + hint), consistent with other panels.
            no_task_card = tk.Frame(self.timetable_scrollable_frame, bg=self.theme["bg_card"], highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
            no_task_card.pack(fill="x", padx=15, pady=20)
            tk.Label(no_task_card, text="🗓️", font=("Segoe UI", 40),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(28, 4))
            tk.Label(no_task_card, text=TRANSLATIONS[lang].get("empty_timetable_title", "Nothing scheduled yet"),
                     font=("Segoe UI", 13, "bold"),
                     bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack()
            tk.Label(no_task_card, text=TRANSLATIONS[lang].get(
                        "empty_timetable_hint", "Add active tasks in the Tasks Workspace to build your study timetable."),
                     font=("Segoe UI", 9),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(2, 28))
            return

        priority_val = {"High": 0, "Medium": 1, "Low": 2}
        pending_tasks.sort(key=lambda t: (priority_val.get(t.priority, 3), t.deadline))

        if self.timetable_view_mode == "week":
            day_tasks = {i: [] for i in range(7)}
            for idx, task in enumerate(pending_tasks):
                day_idx = idx % 7
                day_tasks[day_idx].append(task)

            for i in range(7):
                day_date = date.today() + timedelta(days=i)
                day_name = day_date.strftime("%A, %b %d")
                
                day_card = tk.Frame(self.timetable_scrollable_frame, bg=self.theme["bg_card"],
                                    highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
                day_card.pack(fill="x", padx=15, pady=8)
                
                header_frame = tk.Frame(day_card, bg=self.theme["bg_card"])
                header_frame.pack(fill="x", padx=15, pady=8)
                
                tk.Label(header_frame, text=day_name, font=("Segoe UI", 11, "bold"),
                         bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(side="left")
                
                tasks_list = day_tasks[i]
                if not tasks_list:
                    tk.Label(day_card, text="No tasks scheduled. Recommend review of general lectures.", font=("Segoe UI", 9, "italic"),
                             bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(anchor="w", padx=15, pady=(0, 10))
                else:
                    for t in tasks_list:
                        t_frame = tk.Frame(day_card, bg=self.theme["bg_card"])
                        t_frame.pack(fill="x", padx=15, pady=4)
                        
                        hours = 3 if t.priority == "High" else (2 if t.priority == "Medium" else 1)
                        
                        info_lbl = tk.Label(t_frame, text=f"• Study '{t.title}' ({t.category}) — Suggested: {hours} hour(s)",
                                            font=("Segoe UI", 10), bg=self.theme["bg_card"], fg=self.theme["text_primary"])
                        info_lbl.pack(side="left")
                        
                        due_days = (t.deadline - day_date).days
                        if due_days == 0:
                            tk.Label(t_frame, text="DEADLINE TODAY", font=("Segoe UI", 8, "bold"),
                                     bg=self.theme["danger_bg"], fg=self.theme["danger"], padx=5).pack(side="right")
                        elif 0 < due_days <= 2:
                            tk.Label(t_frame, text=f"Due in {due_days}d", font=("Segoe UI", 8, "bold"),
                                     bg=self.theme["border"], fg=self.theme["warning"], padx=5).pack(side="right")

        elif self.timetable_view_mode == "month":
            for w in range(4):
                week_start = w * 7
                week_end = (w + 1) * 7
                
                week_card = tk.Frame(self.timetable_scrollable_frame, bg=self.theme["bg_card"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
                week_card.pack(fill="x", padx=15, pady=8)
                
                header_frame = tk.Frame(week_card, bg=self.theme["bg_card"])
                header_frame.pack(fill="x", padx=15, pady=8)
                
                tk.Label(header_frame, text=f"Week {w+1} Milestones (Days {week_start+1}-{week_end})", font=("Segoe UI", 11, "bold"),
                         bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(side="left")
                
                week_tasks = [t for t in pending_tasks if week_start <= (t.deadline - date.today()).days < week_end]
                
                if not week_tasks:
                    tk.Label(week_card, text="No coursework deliverables due. Review basic course materials.", font=("Segoe UI", 9, "italic"),
                             bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(anchor="w", padx=15, pady=(0, 10))
                else:
                    for t in week_tasks:
                        t_frame = tk.Frame(week_card, bg=self.theme["bg_card"])
                        t_frame.pack(fill="x", padx=15, pady=4)
                        
                        tk.Label(t_frame, text=f"• Deliverable: '{t.title}' ({t.category}) — Due {t.deadline.strftime('%b %d')}",
                                 font=("Segoe UI", 10), bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(side="left")
                        
                        p_color = self.theme["danger"] if t.priority == "High" else (self.theme["warning"] if t.priority == "Medium" else self.theme["success"])
                        tk.Label(t_frame, text=t.priority, font=("Segoe UI", 8, "bold"),
                                 fg=p_color, bg=self.theme["bg_card"]).pack(side="right")

        elif self.timetable_view_mode == "6month":
            milestones = {
                0: "Semester Start: Establish lecture notes structure and confirm course resources.",
                1: "Mid-Term Prep: Complete initial course projects and practice mid-term questions.",
                2: "Mid-Term Review: Complete project submissions and midterm exams.",
                3: "Post-Midterm Coursework: Start final thesis/project drafts and complex labs.",
                4: "Final Exam Prep: Finalize all pending homework; start revision of early topics.",
                5: "Final Exams & Term Completion: Final exam block and submission of final term papers."
            }
            for m in range(6):
                month_start = m * 30
                month_end = (m + 1) * 30
                
                month_card = tk.Frame(self.timetable_scrollable_frame, bg=self.theme["bg_card"],
                                     highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
                month_card.pack(fill="x", padx=15, pady=8)
                
                header_frame = tk.Frame(month_card, bg=self.theme["bg_card"])
                header_frame.pack(fill="x", padx=15, pady=8)
                
                tk.Label(header_frame, text=f"Month {m+1} Curriculum Milestones", font=("Segoe UI", 11, "bold"),
                         bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(side="left")
                
                guide_lbl = tk.Label(month_card, text=milestones[m], font=("Segoe UI", 9, "italic"),
                                     bg=self.theme["bg_card"], fg=self.theme["text_muted"], wraplength=700, justify="left")
                guide_lbl.pack(anchor="w", padx=15, pady=(0, 10))
                
                month_tasks = [t for t in pending_tasks if month_start <= (t.deadline - date.today()).days < month_end]
                
                if month_tasks:
                    divider = tk.Frame(month_card, height=1, bg=self.theme["border"])
                    divider.pack(fill="x", padx=15, pady=5)
                    
                    for t in month_tasks:
                        t_frame = tk.Frame(month_card, bg=self.theme["bg_card"])
                        t_frame.pack(fill="x", padx=15, pady=4)
                        
                        tk.Label(t_frame, text=f"• Major Deliverable: '{t.title}' ({t.category}) — Due {t.deadline.strftime('%b %d, %Y')}",
                                 font=("Segoe UI", 10), bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(side="left")

    def _export_tasks_csv(self):
        from tkinter import filedialog
        import csv
        
        lang = self.parent.current_lang
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Tasks"
        )
        if not file_path:
            return
            
        try:
            tasks = self.manager.get_all()
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Title", "Category", "Priority", "Deadline", "Completed", "Created At", "Description"])
                for t in tasks:
                    writer.writerow([
                        t.task_id,
                        t.title,
                        t.category,
                        t.priority,
                        t.deadline.strftime("%Y-%m-%d"),
                        "Yes" if t.is_completed() else "No",
                        t.created_at.strftime("%Y-%m-%d"),
                        t.description or ""
                    ])
            play_success_sound()
            messagebox.showinfo("Success", TRANSLATIONS[lang]["msg_export_success"])
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", f"Failed to export: {exc}")

    def _generate_study_summary(self):
        summary = self.manager.get_summary()
        tasks = self.manager.get_all()

        total = summary["total"]
        completed = summary["completed"]
        pending = summary["pending"]
        overdue = summary["overdue"]
        rate = int((completed / total) * 100) if total > 0 else 0
        
        report = []
        report.append("==========================================")
        report.append("        SMART STUDY PLANNER REPORT        ")
        report.append("==========================================")
        report.append(f"Generated on: {date.today().strftime('%Y-%m-%d')}")
        report.append(f"User Email: {self.current_user['email']}")
        report.append("------------------------------------------")
        report.append(f"Total Tasks: {total}")
        report.append(f"Completed Tasks: {completed} ({rate}%)")
        report.append(f"Pending Tasks: {pending}")
        report.append(f"Overdue Tasks: {overdue}")
        report.append("------------------------------------------")
        report.append("PRIORITY BREAKDOWN:")
        for level in PRIORITY_LEVELS:
            count = summary["by_priority"].get(level, 0)
            report.append(f"  - {level}: {count}")
        report.append("------------------------------------------")
        
        cats = {}
        for t in tasks:
            cats[t.category] = cats.get(t.category, 0) + 1
        report.append("CATEGORY BREAKDOWN:")
        for cat, count in cats.items():
            report.append(f"  - {cat}: {count}")
        report.append("------------------------------------------")
        
        report.append("ACADEMIC ADVICE & RECOMMENDATIONS:")
        if overdue > 0:
            report.append(f"  💡 You have {overdue} overdue task(s). Focus on clearing these immediately to stay on track!")
        elif pending > 0:
            report.append("  📈 You are on track. Keep up the good work and finish your pending assignments before deadlines.")
        else:
            report.append("  🏆 Outstanding! All your study tasks are fully completed. Keep up this high standard!")
        report.append("==========================================")
        
        report_text = "\n".join(report)
        self._show_report_popup(report_text)

    def _show_report_popup(self, report_text):
        popup = tk.Toplevel(self)
        popup.title("Academic Progress Summary")
        popup.geometry("500x520")
        popup.configure(bg=self.theme["bg_card"])
        popup.resizable(False, False)
        popup.grab_set()
        
        tk.Label(popup, text="Academic Progress Summary", font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(pady=(15, 10))
                 
        txt_frame = tk.Frame(popup, bg=self.theme["bg_card"])
        txt_frame.pack(padx=20, pady=5, fill="both", expand=True)
        
        text_widget = tk.Text(txt_frame, font=("Consolas", 10), bg=self.theme["bg_main"],
                              fg=self.theme["text_primary"], bd=0, highlightthickness=1,
                              highlightbackground=self.theme["border"], wrap="word")
        text_widget.pack(side="left", fill="both", expand=True)
        text_widget.insert("1.0", report_text)
        text_widget.config(state="disabled")
        
        scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        
        btn_frame = tk.Frame(popup, bg=self.theme["bg_card"])
        btn_frame.pack(pady=15)
        
        def save_report():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("Markdown Files", "*.md"), ("All Files", "*.*")],
                title="Save Report"
            )
            if file_path:
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(report_text)
                    play_success_sound()
                    messagebox.showinfo("Success", "Report saved successfully!", parent=popup)
                except Exception as exc:
                    play_error_sound()
                    messagebox.showerror("Error", f"Failed to save: {exc}", parent=popup)
                    
        create_flat_button(btn_frame, "💾 Save to File", self.theme["primary"], "#ffffff",
                           save_report, hover_bg=self.theme["primary_hover"]).pack(side="left", padx=10)
                           
        create_flat_button(btn_frame, "✕ Close", self.theme["border"], self.theme["text_primary"],
                           popup.destroy, hover_bg=self.theme["bg_main"]).pack(side="left", padx=10)

    def _update_language_setting(self, selected_lang):
        self.parent.current_lang = selected_lang
        self.db.change_language(self.current_user["id"], selected_lang)
        self.current_user["language"] = selected_lang
        play_success_sound()
        # Rebuild in-place but stay on the Settings tab the user is viewing.
        self.parent._show_planner_panel(restore_tab="settings")

    def _style_settings_combobox(self):
        """Themes the Settings language dropdown (field + popup list)."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Settings.TCombobox",
            fieldbackground=self.theme["bg_main"],
            background=self.theme["bg_main"],
            foreground=self.theme["text_primary"],
            arrowcolor=self.theme["text_primary"],
            bordercolor=self.theme["border"],
            lightcolor=self.theme["border"],
            darkcolor=self.theme["border"],
            relief="flat",
            padding=4
        )
        style.map(
            "Settings.TCombobox",
            fieldbackground=[("readonly", self.theme["bg_main"])],
            foreground=[("readonly", self.theme["text_primary"])],
            selectbackground=[("readonly", self.theme["bg_main"])],
            selectforeground=[("readonly", self.theme["text_primary"])]
        )
        self.parent.option_add("*TCombobox*Listbox.background", self.theme["bg_card"])
        self.parent.option_add("*TCombobox*Listbox.foreground", self.theme["text_primary"])
        self.parent.option_add("*TCombobox*Listbox.selectBackground", self.theme["primary"])
        self.parent.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
        self.parent.option_add("*TCombobox*Listbox.font", "{Segoe UI} 10")

    def _on_toggle_sound(self):
        enabled = bool(self.sound_enabled_var.get())
        set_sound_enabled(enabled)
        self.parent.set_pref("sound_enabled", enabled)
        if enabled:
            play_success_sound()

    def _toggle_pw(self, entry, btn):
        """Show/hide a settings password field."""
        if entry.cget("show") == "*":
            entry.config(show="")
            btn.config(text="🙈")
        else:
            entry.config(show="*")
            btn.config(text="👁")

    def _make_pw_field(self, parent, row, label_text, eye=True):
        """Build a label + password entry on the given grid row, returning the entry.
        An eye toggle is added only when ``eye`` is True."""
        tk.Label(parent, text=label_text, font=("Segoe UI", 9, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=row, column=0, sticky="w", pady=5)
        wrap = tk.Frame(parent, bg=self.theme["bg_card"])
        wrap.grid(row=row, column=1, sticky="w", padx=10, pady=5)
        entry = tk.Entry(wrap, font=("Segoe UI", 10), show="*", bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                         highlightbackground=self.theme["border"], highlightthickness=1, bd=0,
                         insertbackground=self.theme["text_primary"], width=26)
        entry.pack(side="left", ipady=1)
        bind_focus_highlight(entry, self.theme)
        if eye:
            eye_btn = tk.Button(wrap, text="👁", font=("Segoe UI", 9), bg=self.theme["border"], fg=self.theme["text_primary"],
                                relief="flat", activebackground=self.theme["bg_main"], bd=0, cursor="hand2", width=3)
            eye_btn.pack(side="left", fill="y", padx=(2, 0))
            eye_btn.config(command=lambda: self._toggle_pw(entry, eye_btn))
        return entry

    def _on_update_profile(self):
        full_name = self.set_fullname.get().strip()
        username = self.set_username.get().strip().lower()
        email = self.set_email.get().strip()
        lang = self.parent.current_lang

        if not full_name or not email:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_missing_fields"])
            return
        if not validate_full_name(full_name):
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_invalid_name"])
            return
        if not validate_email(email):
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_invalid_email"])
            return
        if username and len(username) < 3:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_invalid_username"])
            return

        try:
            updated = self.db.update_user_profile(self.current_user["id"], full_name, email, username or None)
            # Keep the in-memory user (and remembered login) in sync.
            self.current_user.update(updated)
            self.parent.current_user = self.current_user
            if self.parent.last_login:
                self.parent.set_pref("last_login", updated.get("username") or updated.get("email", ""))
                self.parent.last_login = updated.get("username") or updated.get("email", "")
            play_success_sound()
            messagebox.showinfo("Success", TRANSLATIONS[lang].get("msg_profile_updated", "Profile updated successfully!"))
            # Rebuild so the sidebar name/email refresh, staying on Settings.
            self.parent._show_planner_panel(restore_tab="settings")
        except ValueError as exc:
            play_error_sound()
            messagebox.showerror("Error", str(exc))

    def _on_update_academic_profile(self):
        dept = self.set_department.get().strip()
        cls_name = self.set_class_name.get().strip()
        section = self.set_section.get().strip()
        batch_year = self.set_batch_year.get().strip()
        self.db.update_academic_profile(self.current_user["id"], dept, cls_name, section, batch_year)
        self.current_user["department"] = dept
        self.current_user["class_name"] = cls_name
        self.current_user["section"] = section
        self.current_user["batch_year"] = batch_year
        self.parent.current_user = self.current_user
        play_success_sound()
        messagebox.showinfo("Saved", "Academic profile updated successfully.")
        self.parent._show_planner_panel(restore_tab="settings")

    def _on_change_password(self):
        old_pwd = self.set_pwd_old.get().strip()
        new_pwd = self.set_pwd_new.get().strip()
        confirm_pwd = self.set_pwd_confirm.get().strip()
        lang = self.parent.current_lang

        if not old_pwd or not new_pwd or not confirm_pwd:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_missing_fields"])
            return

        # Authenticate current credentials
        user_verified = self.db.authenticate_user(self.current_user["email"], old_pwd)
        if not user_verified:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_auth_err"])
            return

        ok, msg = validate_password_strength(new_pwd)
        if not ok:
            play_error_sound()
            messagebox.showerror("Error", msg)
            return

        if new_pwd != confirm_pwd:
            play_error_sound()
            messagebox.showerror("Error", TRANSLATIONS[lang]["msg_pwd_match_err"])
            return

        # Update password
        try:
            self.db.change_password(self.current_user["id"], new_pwd)
            play_success_sound()
            messagebox.showinfo("Success", TRANSLATIONS[lang]["msg_change_pwd_success"])
            self.set_pwd_old.delete(0, "end")
            self.set_pwd_new.delete(0, "end")
            self.set_pwd_confirm.delete(0, "end")
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", f"Failed: {exc}")

    # --- FOCUS POMODORO TIMER ---

    def _add_particle_bg(self, panel, count=22):
        """Adds an animated particle background filling ``panel``, lowered behind
        any cards. Used on sparse 'hero' screens; data-dense screens stay clean."""
        canvas = ParticleCanvas(panel, self.theme, base_image=None, count=count)
        canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        # Misc.lower (Canvas.lower is aliased to canvas-item lowering) pushes the
        # whole widget behind the card in the sibling stacking order.
        tk.Misc.lower(canvas)
        return canvas

    def _build_timer_panel(self):
        self.timer_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.timer_panel.grid_columnconfigure(0, weight=1)
        self.timer_panel.grid_rowconfigure(0, weight=1)

        self._add_particle_bg(self.timer_panel)

        card = tk.Frame(self.timer_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                        highlightthickness=1, bd=0, width=560, height=560)
        # Grid-centering (not place) so the card is positioned against the panel's
        # final, grid-allocated size — place-centering computed against the panel's
        # initial 1x1 size and pushed the card off-screen (blank timer panel).
        card.grid(row=0, column=0)
        card.grid_propagate(False)

        title_lbl = tk.Label(card, text="Focus Pomodoro Timer", font=("Segoe UI", 16, "bold"),
                             bg=self.theme["bg_card"], fg=self.theme["text_primary"])
        title_lbl.pack(pady=(25, 5))

        desc_lbl = tk.Label(card, text="Boost productivity with study soundscapes & structured breaks", font=("Segoe UI", 9),
                            bg=self.theme["bg_card"], fg=self.theme["text_muted"])
        desc_lbl.pack(pady=(0, 20))

        self.timer_label = tk.Label(card, text="25:00", font=("Segoe UI", 48, "bold"),
                                    bg=self.theme["bg_card"], fg=self.theme["primary"])
        self.timer_label.pack(pady=10)
        self._update_timer_display()

        mode_frame = tk.Frame(card, bg=self.theme["bg_card"])
        mode_frame.pack(pady=10)

        self.btn_mode_work = create_flat_button(mode_frame, "Work Session", self.theme["primary"], "#ffffff",
                                                lambda: self._set_timer_mode("Work"), font=("Segoe UI", 9, "bold"))
        self.btn_mode_work.pack(side="left", padx=5)

        self.btn_mode_break = create_flat_button(mode_frame, "Short Break", self.theme["bg_main"], self.theme["text_primary"],
                                                 lambda: self._set_timer_mode("Break"), font=("Segoe UI", 9, "bold"))
        self.btn_mode_break.pack(side="left", padx=5)

        sound_frame = tk.Frame(card, bg=self.theme["bg_card"])
        sound_frame.pack(pady=(12, 4))

        tk.Label(sound_frame, text="Ambient Soundscape:", font=("Segoe UI", 10, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(side="left", padx=5)

        self._style_settings_combobox()
        self.sound_combobox = ttk.Combobox(
            sound_frame,
            values=["Silence", "Lo-Fi Beats", "Rainforest", "White Noise", "Ocean Waves", "Warm Fireplace"],
            state="readonly",
            style="Settings.TCombobox",
            font=("Segoe UI", 9),
            width=15
        )
        self.sound_combobox.set(self.timer_soundscape)
        self.sound_combobox.pack(side="left", padx=5, ipady=2)
        self.sound_combobox.bind("<<ComboboxSelected>>", self._on_soundscape_change)

        # Play / Pause soundscape
        self.btn_scape = create_flat_button(sound_frame, "▶ Play", self.theme["success"], "#ffffff",
                                            self._toggle_soundscape, hover_bg=self.theme["success_hover"],
                                            font=("Segoe UI", 9, "bold"), padx=10, pady=4)
        self.btn_scape.pack(side="left", padx=5)

        # Volume control
        vol_frame = tk.Frame(card, bg=self.theme["bg_card"])
        vol_frame.pack(pady=(2, 4))
        tk.Label(vol_frame, text="🔉 Volume", font=("Segoe UI", 9, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack(side="left", padx=(5, 8))
        self.volume_scale = tk.Scale(
            vol_frame, from_=0, to=100, orient="horizontal", length=240, showvalue=True,
            bg=self.theme["bg_card"], fg=self.theme["text_muted"], troughcolor=self.theme["bg_main"],
            highlightthickness=0, bd=0, sliderrelief="flat", activebackground=self.theme["primary"],
            font=("Segoe UI", 7), command=lambda v: setattr(self, "timer_volume", int(float(v)))
        )
        self.volume_scale.set(self.timer_volume)
        self.volume_scale.pack(side="left")
        self.volume_scale.bind("<ButtonRelease-1>", lambda e: self._apply_volume())

        self.visualizer_canvas = tk.Canvas(card, bg=self.theme["bg_card"], width=300, height=40, bd=0, highlightthickness=0)
        self.visualizer_canvas.pack(pady=5)
        self._draw_static_visualizer()

        control_frame = tk.Frame(card, bg=self.theme["bg_card"])
        control_frame.pack(pady=20)

        self.btn_timer_toggle = create_flat_button(control_frame, "Start", self.theme["success"], "#ffffff",
                                                   self._toggle_timer, hover_bg=self.theme["success_hover"], font=("Segoe UI", 10, "bold"))
        self.btn_timer_toggle.pack(side="left", padx=10)

        btn_timer_reset = create_flat_button(control_frame, "Reset", self.theme["border"], self.theme["text_primary"],
                                             self._reset_timer, hover_bg=self.theme["bg_main"], font=("Segoe UI", 10, "bold"))
        btn_timer_reset.pack(side="left", padx=10)

    def _update_timer_display(self):
        mins = self.timer_seconds // 60
        secs = self.timer_seconds % 60
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

    def _toggle_timer(self):
        play_click_sound()
        if self.timer_running:
            self.timer_running = False
            self.btn_timer_toggle.config(text="Start", bg=self.theme["success"], activebackground=self.theme["success_hover"])
            if self.timer_after_id:
                self.parent.after_cancel(self.timer_after_id)
                self.timer_after_id = None
        else:
            self.timer_running = True
            self.btn_timer_toggle.config(text="Pause", bg=self.theme["warning"], activebackground=self.theme["warning_hover"])
            self._timer_tick()

    def _reset_timer(self):
        play_click_sound()
        self.timer_running = False
        if self.timer_after_id:
            self.parent.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.btn_timer_toggle.config(text="Start", bg=self.theme["success"], activebackground=self.theme["success_hover"])
        self.timer_seconds = 25 * 60 if self.timer_mode == "Work" else 5 * 60
        self._update_timer_display()
        self._draw_static_visualizer()

    def _timer_tick(self):
        if not self.timer_running:
            return
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self._update_timer_display()
            self.timer_after_id = self.parent.after(1000, self._timer_tick)
        else:
            self.timer_running = False
            self.btn_timer_toggle.config(text="Start", bg=self.theme["success"], activebackground=self.theme["success_hover"])
            self.timer_after_id = None

            play_notify_sound()

            if self.timer_mode == "Work":
                messagebox.showinfo("Timer Alert", "Great job! Work session completed. Time for a short break.")
                self._set_timer_mode("Break")
            else:
                messagebox.showinfo("Timer Alert", "Break ended! Let's get back to studying.")
                self._set_timer_mode("Work")

    def _set_timer_mode(self, mode):
        play_click_sound()
        self.timer_mode = mode
        if self.timer_after_id:
            self.parent.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.timer_running = False
        self.btn_timer_toggle.config(text="Start", bg=self.theme["success"], activebackground=self.theme["success_hover"])
        
        if mode == "Work":
            self.timer_seconds = 25 * 60
            self.btn_mode_work.config(bg=self.theme["primary"], fg="#ffffff")
            self.btn_mode_break.config(bg=self.theme["bg_main"], fg=self.theme["text_primary"])
        else:
            self.timer_seconds = 5 * 60
            self.btn_mode_break.config(bg=self.theme["primary"], fg="#ffffff")
            self.btn_mode_work.config(bg=self.theme["bg_main"], fg=self.theme["text_primary"])
            
        self._update_timer_display()
        self._draw_static_visualizer()

    def _on_soundscape_change(self, event=None):
        self.timer_soundscape = self.sound_combobox.get()
        if self.soundscape_playing:
            if self.timer_soundscape == "Silence":
                self._stop_soundscape()
            else:
                play_soundscape(self.timer_soundscape, self.timer_volume)
                self._animate_visualizer()

    def _toggle_soundscape(self):
        """Play or pause the selected ambient soundscape."""
        if self.soundscape_playing:
            self._stop_soundscape()
            return
        name = self.sound_combobox.get()
        self.timer_soundscape = name
        if name == "Silence":
            messagebox.showinfo("Soundscape", "Select a soundscape other than 'Silence' to play audio.")
            return
        if play_soundscape(name, self.timer_volume):
            self.soundscape_playing = True
            self.btn_scape.config(text="⏸ Pause", bg=self.theme["warning"],
                                  activebackground=self.theme["warning_hover"])
            self.btn_scape._base_bg = self.theme["warning"]
            self.btn_scape._hover_bg = self.theme["warning_hover"]
            self._animate_visualizer()

    def _stop_soundscape(self):
        stop_soundscape()
        self.soundscape_playing = False
        if hasattr(self, "btn_scape") and self.btn_scape.winfo_exists():
            self.btn_scape.config(text="▶ Play", bg=self.theme["success"],
                                  activebackground=self.theme["success_hover"])
            self.btn_scape._base_bg = self.theme["success"]
            self.btn_scape._hover_bg = self.theme["success_hover"]
        if hasattr(self, "visualizer_canvas") and self.visualizer_canvas.winfo_exists():
            self._draw_static_visualizer()

    def _apply_volume(self):
        """Re-render the looping soundscape at the new volume (on slider release)."""
        if self.soundscape_playing and self.timer_soundscape != "Silence":
            play_soundscape(self.timer_soundscape, self.timer_volume)

    def _draw_static_visualizer(self):
        self.visualizer_canvas.delete("all")
        w, h = 300, 40
        num_bars = 20
        bar_w = 8
        gap = 4
        start_x = (w - (num_bars * (bar_w + gap) - gap)) / 2
        for i in range(num_bars):
            x0 = start_x + i * (bar_w + gap)
            y0 = h - 5
            x1 = x0 + bar_w
            y1 = h - 8
            self.visualizer_canvas.create_rectangle(x0, y0, x1, y1, fill=self.theme["border"], outline="")

    def _animate_visualizer(self):
        # Stop the loop if the canvas was destroyed (theme switch / logout) so the
        # self-rescheduling after() callback can't fire against a dead widget.
        if not self.visualizer_canvas.winfo_exists():
            return
        if not self.soundscape_playing or self.timer_soundscape == "Silence":
            self._draw_static_visualizer()
            return

        self.visualizer_canvas.delete("all")
        import random
        w, h = 300, 40
        num_bars = 20
        bar_w = 8
        gap = 4
        start_x = (w - (num_bars * (bar_w + gap) - gap)) / 2
        color = self.theme["primary"]
        
        for i in range(num_bars):
            bar_h = random.randint(5, 32)
            x0 = start_x + i * (bar_w + gap)
            y0 = h - bar_h
            x1 = x0 + bar_w
            y1 = h - 2
            self.visualizer_canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            
        self.parent.after(150, self._animate_visualizer)

    # --- STUDY ASSISTANT ---

    def _build_ai_panel(self):
        self.ai_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.ai_panel.grid_columnconfigure(0, weight=1)
        self.ai_panel.grid_rowconfigure(1, weight=1)

        prompts_frame = tk.Frame(self.ai_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                                 highlightthickness=1, bd=0)
        prompts_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        btn_explain = create_flat_button(prompts_frame, "Explain Concept", self.theme["primary"], "#ffffff",
                                         lambda: self._on_ai_quick_prompt("explain"), font=("Segoe UI", 9, "bold"))
        btn_explain.pack(side="left", padx=10, pady=10)

        btn_summarize = create_flat_button(prompts_frame, "Summarize Tasks", self.theme["success"], "#ffffff",
                                           lambda: self._on_ai_quick_prompt("summarize"), font=("Segoe UI", 9, "bold"))
        btn_summarize.pack(side="left", padx=5, pady=10)

        btn_practice = create_flat_button(prompts_frame, "Practice Questions", self.theme["warning"], "#ffffff",
                                          lambda: self._on_ai_quick_prompt("practice"), font=("Segoe UI", 9, "bold"))
        btn_practice.pack(side="left", padx=5, pady=10)

        chat_card = tk.Frame(self.ai_panel, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                             highlightthickness=1, bd=0)
        chat_card.grid(row=1, column=0, sticky="nsew")
        chat_card.grid_columnconfigure(0, weight=1)
        chat_card.grid_rowconfigure(0, weight=1)

        self.chat_history = tk.Text(chat_card, bg=self.theme["bg_card"], fg=self.theme["text_primary"],
                                    insertbackground=self.theme["text_primary"], bd=0, highlightthickness=0,
                                    font=("Segoe UI", 10), wrap="word", padx=15, pady=15)
        self.chat_history.grid(row=0, column=0, sticky="nsew")
        self.chat_history.config(state="disabled")

        scrollbar = ttk.Scrollbar(chat_card, orient="vertical", command=self.chat_history.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_history.config(yscrollcommand=scrollbar.set)

        self.chat_history.tag_config("user_sender", foreground=self.theme["primary"], font=("Segoe UI", 10, "bold"))
        self.chat_history.tag_config("ai_sender", foreground=self.theme["success"], font=("Segoe UI", 10, "bold"))
        self.chat_history.tag_config("user_msg", foreground=self.theme["text_primary"])
        self.chat_history.tag_config("ai_msg", foreground=self.theme["text_primary"])
        self.chat_history.tag_config("system_msg", foreground=self.theme["text_muted"], font=("Segoe UI", 9, "italic"))

        input_frame = tk.Frame(self.ai_panel, bg=self.theme["bg_main"])
        input_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        input_frame.grid_columnconfigure(0, weight=1)

        self.ai_input = tk.Entry(input_frame, bg=self.theme["bg_card"], fg=self.theme["text_primary"],
                                 insertbackground=self.theme["text_primary"], highlightbackground=self.theme["border"],
                                 highlightthickness=1, bd=0, font=("Segoe UI", 10))
        self.ai_input.grid(row=0, column=0, sticky="ew", ipady=8, padx=(0, 10))
        bind_focus_highlight(self.ai_input, self.theme)

        self.ai_input.bind("<Return>", lambda e: self._send_ai_chat())

        btn_send = create_flat_button(input_frame, "Send", self.theme["primary"], "#ffffff",
                                      self._send_ai_chat, hover_bg=self.theme["primary_hover"], font=("Segoe UI", 10, "bold"), padx=20, pady=6)
        btn_send.grid(row=0, column=1, sticky="e")

        self._append_to_chat("Assistant", "Hello! I am your Study Assistant. Click one of the quick action buttons above or type below to ask me academic questions, explain concepts, summarize tasks, or generate practice material based on your schedule.", "ai_msg")

    def _send_ai_chat(self):
        query = self.ai_input.get().strip()
        if not query:
            return
        self.ai_input.delete(0, "end")
        self._append_to_chat("User", query, "user_msg")
        
        self.parent.after(400, lambda: self._generate_ai_response(query))

    def _append_to_chat(self, sender, text, tag):
        self.chat_history.config(state="normal")
        sender_tag = "user_sender" if sender == "User" else "ai_sender"
        self.chat_history.insert("end", f"\n{sender}: ", sender_tag)
        
        if sender == "Assistant" and tag == "ai_msg":
            self.chat_history.config(state="disabled")
            self._typewriter_effect(text, 0)
        else:
            self.chat_history.insert("end", text, tag)
            self.chat_history.insert("end", "\n")
            self.chat_history.see("end")
            self.chat_history.config(state="disabled")

    def _typewriter_effect(self, text, index):
        # Abort if the chat widget was destroyed mid-animation (theme switch,
        # logout, tab rebuild). Otherwise queued after() callbacks fire against a
        # dead widget and raise TclError spam.
        if not self.chat_history.winfo_exists():
            return
        if index < len(text):
            self.chat_history.config(state="normal")
            self.chat_history.insert("end", text[index], "ai_msg")
            self.chat_history.see("end")
            self.chat_history.config(state="disabled")
            self.parent.after(8, lambda: self._typewriter_effect(text, index + 1))
        else:
            self.chat_history.config(state="normal")
            self.chat_history.insert("end", "\n")
            self.chat_history.see("end")
            self.chat_history.config(state="disabled")

    def _on_ai_quick_prompt(self, action):
        play_click_sound()
        if action == "explain":
            concept = ModernInputDialog.ask(self.parent, "Explain Concept", "What scientific, math, or study concept should I explain?")
            if concept and concept.strip():
                self._append_to_chat("User", f"Explain the concept of: {concept.strip()}", "user_msg")
                self.parent.after(400, lambda: self._generate_ai_response(f"explain {concept.strip()}"))
        elif action == "summarize":
            self._append_to_chat("User", "Generate a summary of my active task load.", "user_msg")
            self.parent.after(400, lambda: self._generate_ai_response("summarize"))
        elif action == "practice":
            subject = ModernInputDialog.ask(self.parent, "Practice Questions", "Enter subject category (e.g. Physics, Calculus, Coding):")
            if subject and subject.strip():
                self._append_to_chat("User", f"Generate practice questions for: {subject.strip()}", "user_msg")
                self.parent.after(400, lambda: self._generate_ai_response(f"practice {subject.strip()}"))

    def _generate_ai_response(self, query):
        q_lower = query.lower()
        
        if q_lower.startswith("explain "):
            concept = query[8:].strip()
            response = (
                f"Here is an educational explanation for the concept of '{concept}':\n\n"
                f"1. Core Definition: '{concept}' represents a key principle in academic courses. Understanding its foundational mechanisms is essential for solving complex exam questions.\n"
                f"2. Practical Application: This concept is frequently applied to break down theoretical problems into actionable steps.\n"
                f"3. Study Advice: I recommend creating a conceptual mind-map and summarizing this topic in your own words. Write down 3 real-world scenarios where this applies, and review the related course notes at least twice this week."
            )
        elif q_lower == "summarize":
            pending = [t for t in self.manager.tasks if t.status != "Completed"]
            high_prio = [t for t in pending if t.priority == "High"]
            
            if not pending:
                response = "You currently have no pending tasks in your Study Planner database! Keep up the excellent work! You are all caught up."
            else:
                task_items = []
                for idx, t in enumerate(pending[:5]):
                    task_items.append(f"  - [{t.priority}] {t.title} (Due: {t.deadline})")
                if len(pending) > 5:
                    task_items.append(f"  - ... and {len(pending) - 5} more tasks.")
                
                tasks_text = "\n".join(task_items)
                response = (
                    f"Here is a comprehensive summary of your active workload:\n\n"
                    f"• Total Pending Tasks: {len(pending)}\n"
                    f"• High Priority Deadlines: {len(high_prio)}\n\n"
                    f"Top Deliverables Scheduled:\n{tasks_text}\n\n"
                    f"Assistant Recommendations:\n"
                    f"- Prioritize your {len(high_prio)} High Priority task(s) first using Pomodoro Focus sessions.\n"
                    f"- Try to complete at least one medium or low task tomorrow to maintain study momentum."
                )
        elif q_lower.startswith("practice "):
            subject = query[9:].strip()
            response = (
                f"Here are 5 custom review practice questions generated for '{subject}':\n\n"
                f"Q1: Formulate the primary equation/rule of '{subject}' and describe how it applies to experimental configurations.\n"
                f"Q2: Differentiate between the primary variables and dependent structures inside a typical '{subject}' problem.\n"
                f"Q3: Suppose a parameters shift of 20% occurs. Predict the mathematical/structural outcome using '{subject}' guidelines.\n"
                f"Q4: Identify three common theoretical misconceptions that students encounter when studying '{subject}'.\n"
                f"Q5: Detail a step-by-step methodology to solve a composite exam scenario in this subject area."
            )
        elif any(greeting in q_lower for greeting in ["hello", "hi", "hey", "greetings"]):
            response = "Hello there! How can I assist you with your academic study plan today? Feel free to ask about tasks, concepts, or request practice questions."
        elif any(kw in q_lower for kw in ["help", "capabilities", "what can you do"]):
            response = (
                "I can perform the following study assistance actions:\n"
                "1. Explain Concepts: Type 'explain [concept name]' or click the quick action button above.\n"
                "2. Summarize Workload: Type 'summarize' or click 'Summarize Tasks' to analyze your schedule.\n"
                "3. Generate Questions: Type 'practice [subject]' or click 'Practice Questions' for revision exams.\n"
                "4. Answer general study-advice queries."
            )
        else:
            response = (
                "I've received your query about studying. While I am a localized offline assistant, "
                "I suggest focusing on structuring study milestones for this topic. Here is some general advice:\n\n"
                "- Break the topic down into 3 sub-sections.\n"
                "- Spend 25 minutes studying the first section (using the Focus Timer!), then take a 5-minute break.\n"
                "- Let me know if you would like me to explain a specific concept (type 'explain [topic]') or generate review questions!"
            )
            
        self._append_to_chat("Assistant", response, "ai_msg")

    # --- STUDY GROUPS DASHBOARD ---

    def _build_groups_panel(self):
        self.groups_panel = tk.Frame(self.panel_container, bg=self.theme["bg_main"])
        self.groups_panel.grid_columnconfigure(0, weight=1)
        self.groups_panel.grid_rowconfigure(1, weight=1)

        # LAN manager instance (created when LAN tab is opened)
        self._lan_manager = None
        self._lan_discovered: dict = {}
        self._lan_selected_ip = None
        self._active_groups_tab = "my_groups"

        # Tab strip
        tab_bar = tk.Frame(self.groups_panel, bg=self.theme["bg_card"],
                           highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._tab_btns = {}
        for tab_key, label in [("my_groups", "My Study Groups"), ("lan_rooms", "🌐 LAN Study Rooms")]:
            btn = tk.Button(tab_bar, text=label, font=("Segoe UI", 10, "bold"),
                            bg=self.theme["bg_card"], fg=self.theme["text_muted"],
                            relief="flat", bd=0, padx=18, pady=10, cursor="hand2",
                            command=lambda k=tab_key: self._switch_groups_tab(k))
            btn.pack(side="left")
            self._tab_btns[tab_key] = btn

        # Content frames (stacked at row=1)
        self._groups_content = tk.Frame(self.groups_panel, bg=self.theme["bg_main"])
        self._groups_content.grid(row=1, column=0, sticky="nsew")
        self._groups_content.grid_columnconfigure(0, weight=0, minsize=240)
        self._groups_content.grid_columnconfigure(1, weight=1)
        self._groups_content.grid_rowconfigure(0, weight=1)

        self._lan_content = tk.Frame(self.groups_panel, bg=self.theme["bg_main"])
        self._lan_content.grid_columnconfigure(0, weight=0, minsize=240)
        self._lan_content.grid_columnconfigure(1, weight=1)
        self._lan_content.grid_rowconfigure(0, weight=1)

        # Build My Groups content (into self._groups_content)
        left_pane = tk.Frame(self._groups_content, bg=self.theme["bg_card"],
                             highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        left_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_pane.grid_rowconfigure(1, weight=1)
        left_pane.grid_columnconfigure(0, weight=1)

        tk.Label(left_pane, text="My Study Groups", font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", padx=15, pady=15)

        self.groups_listbox = tk.Listbox(left_pane, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                         selectbackground=self.theme["primary"], selectforeground="#ffffff",
                                         highlightthickness=0, bd=0, font=("Segoe UI", 10))
        self.groups_listbox.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        self.groups_listbox.bind("<<ListboxSelect>>", self._on_group_select)

        btn_create_grp = create_flat_button(left_pane, "Create New Group", self.theme["primary"], "#ffffff",
                                            self._create_new_group, hover_bg=self.theme["primary_hover"],
                                            font=("Segoe UI", 9, "bold"))
        btn_create_grp.grid(row=2, column=0, sticky="ew", padx=15, pady=(15, 4))

        self.btn_delete_grp = create_flat_button(left_pane, "🗑 Delete Group", self.theme["danger"], "#ffffff",
                                                 self._delete_selected_group, hover_bg=self.theme["danger_hover"],
                                                 font=("Segoe UI", 9, "bold"))
        self.btn_delete_grp.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.btn_delete_grp.grid_remove()

        self.group_details_frame = tk.Frame(self._groups_content, bg=self.theme["bg_main"])
        self.group_details_frame.grid(row=0, column=1, sticky="nsew")
        self.group_details_frame.grid_columnconfigure(0, weight=1)
        self.group_details_frame.grid_rowconfigure(0, weight=1)

        self._draw_group_details_placeholder()

        # Build LAN content (into self._lan_content)
        self._build_lan_content()

        # Start on My Groups tab
        self._switch_groups_tab("my_groups")

    def _switch_groups_tab(self, tab_key):
        self._active_groups_tab = tab_key
        for key, btn in self._tab_btns.items():
            if key == tab_key:
                btn.config(fg=self.theme["primary"], font=("Segoe UI", 10, "bold"))
            else:
                btn.config(fg=self.theme["text_muted"], font=("Segoe UI", 10))

        if tab_key == "my_groups":
            self._lan_content.grid_remove()
            self._groups_content.grid(row=1, column=0, sticky="nsew")
            self._stop_lan_discovery()
        else:
            self._groups_content.grid_remove()
            self._lan_content.grid(row=1, column=0, sticky="nsew")
            self._start_lan_discovery()

    # ── LAN Study Rooms ──────────────────────────────────────────────

    def _build_lan_content(self):
        # Left pane: discovered rooms list + host button
        lan_left = tk.Frame(self._lan_content, bg=self.theme["bg_card"],
                            highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        lan_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        lan_left.grid_rowconfigure(2, weight=1)
        lan_left.grid_columnconfigure(0, weight=1)

        tk.Label(lan_left, text="LAN Study Rooms", font=("Segoe UI", 12, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 2))

        self._lan_status_lbl = tk.Label(lan_left, text="Searching on local network…",
                                        font=("Segoe UI", 8), bg=self.theme["bg_card"],
                                        fg=self.theme["text_muted"])
        self._lan_status_lbl.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 6))

        self._lan_listbox = tk.Listbox(lan_left, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                       selectbackground=self.theme["primary"], selectforeground="#ffffff",
                                       highlightthickness=0, bd=0, font=("Segoe UI", 10))
        self._lan_listbox.grid(row=2, column=0, sticky="nsew", padx=15, pady=(0, 10))
        self._lan_listbox.bind("<<ListboxSelect>>", self._on_lan_room_select)

        self._lan_host_btn = create_flat_button(lan_left, "📡 Host a Study Room", self.theme["success"], "#ffffff",
                                                self._on_host_room_clicked, hover_bg=self.theme["success_hover"],
                                                font=("Segoe UI", 9, "bold"))
        self._lan_host_btn.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))

        # Right pane: selected room details
        self._lan_detail_frame = tk.Frame(self._lan_content, bg=self.theme["bg_main"])
        self._lan_detail_frame.grid(row=0, column=1, sticky="nsew")
        self._lan_detail_frame.grid_columnconfigure(0, weight=1)
        self._lan_detail_frame.grid_rowconfigure(0, weight=1)

        self._draw_lan_placeholder()

    def _draw_lan_placeholder(self):
        for w in self._lan_detail_frame.winfo_children():
            w.destroy()
        tk.Label(self._lan_detail_frame,
                 text="Select a room from the list, or host your own study room for others to join.",
                 font=("Segoe UI", 11, "italic"), bg=self.theme["bg_main"],
                 fg=self.theme["text_muted"], wraplength=400, justify="center").pack(expand=True)

    def _draw_lan_hosting_view(self, room_name):
        for w in self._lan_detail_frame.winfo_children():
            w.destroy()
        card = tk.Frame(self._lan_detail_frame, bg=self.theme["bg_card"],
                        highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(card, text="📡  You are hosting", font=("Segoe UI", 11),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(30, 6))
        tk.Label(card, text=room_name, font=("Segoe UI", 18, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(pady=(0, 10))

        u = self.current_user
        info_parts = [p for p in [u.get("department", ""), u.get("class_name", ""), u.get("section", "")] if p]
        if info_parts:
            tk.Label(card, text=" · ".join(info_parts), font=("Segoe UI", 10),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(0, 20))

        tk.Label(card, text="Peers on the same network can discover and join this room.",
                 font=("Segoe UI", 9), bg=self.theme["bg_card"],
                 fg=self.theme["text_muted"], wraplength=340).pack(pady=(0, 30))

        stop_btn = create_flat_button(card, "■  Stop Hosting", self.theme["danger"], "#ffffff",
                                      self._on_stop_hosting_clicked, hover_bg=self.theme["danger_hover"])
        stop_btn.pack(ipadx=10, ipady=6)

    def _draw_lan_room_detail(self, info):
        for w in self._lan_detail_frame.winfo_children():
            w.destroy()
        card = tk.Frame(self._lan_detail_frame, bg=self.theme["bg_card"],
                        highlightbackground=self.theme["border"], highlightthickness=1, bd=0)
        card.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(card, text=info.get("room", "Study Room"), font=("Segoe UI", 18, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(pady=(30, 6))
        tk.Label(card, text=f"Host: {info.get('host', '—')}", font=("Segoe UI", 11),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).pack()

        dept = info.get("department", "")
        cls = info.get("class", "")
        sec = info.get("section", "")
        detail_parts = [p for p in [dept, cls, sec] if p]
        if detail_parts:
            tk.Label(card, text=" · ".join(detail_parts), font=("Segoe UI", 10),
                     bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(4, 0))

        tk.Label(card, text=f"IP: {info.get('_ip', '?')}", font=("Segoe UI", 8),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(pady=(4, 24))

        tk.Label(card, text="This room is broadcasting live on your local network.\nYou can coordinate over chat (voice/messaging app) while studying together.",
                 font=("Segoe UI", 9), bg=self.theme["bg_card"],
                 fg=self.theme["text_muted"], wraplength=340, justify="center").pack()

    def _start_lan_discovery(self):
        if self._lan_manager is not None:
            return
        self._lan_manager = lan_module.LANManager()
        self._lan_manager.start_discovery(self._on_lan_rooms_updated_bg)

    def _stop_lan_discovery(self):
        if self._lan_manager is not None:
            self._lan_manager.stop()
            self._lan_manager = None

    def _on_lan_rooms_updated_bg(self, rooms: dict):
        # Called from the discovery background thread — schedule UI update on main thread.
        try:
            self.parent.after(0, lambda r=rooms: self._refresh_lan_listbox(r))
        except Exception:
            pass

    def _refresh_lan_listbox(self, rooms: dict):
        self._lan_discovered = rooms
        self._lan_listbox.delete(0, "end")
        if not rooms:
            self._lan_status_lbl.config(text="No rooms found yet — searching…")
        else:
            n = len(rooms)
            self._lan_status_lbl.config(text=f"{n} room{'s' if n != 1 else ''} found on your network")
        for ip, info in rooms.items():
            label = f"{info.get('room', '?')}  —  {info.get('host', ip)}"
            dept = info.get("department", "")
            cls = info.get("class", "")
            if dept or cls:
                label += f"  [{' · '.join(p for p in [dept, cls] if p)}]"
            self._lan_listbox.insert("end", label)
        # Keep detail pane in sync
        if self._lan_selected_ip and self._lan_selected_ip not in rooms:
            self._lan_selected_ip = None
            if not (self._lan_manager and self._lan_manager.is_hosting):
                self._draw_lan_placeholder()

    def _on_lan_room_select(self, event=None):
        sel = self._lan_listbox.curselection()
        if not sel:
            return
        ips = list(self._lan_discovered.keys())
        idx = sel[0]
        if idx >= len(ips):
            return
        self._lan_selected_ip = ips[idx]
        self._draw_lan_room_detail(self._lan_discovered[self._lan_selected_ip])

    def _on_host_room_clicked(self):
        if self._lan_manager and self._lan_manager.is_hosting:
            messagebox.showinfo("Already Hosting",
                                "You are already hosting a study room. Stop the current room first.")
            return
        room_name = ModernInputDialog.ask(self.parent, "Host Study Room",
                                          "Enter a name for your study room:\n(e.g. 'OS Mid-term Prep')")
        if not room_name or not room_name.strip():
            return
        room_name = room_name.strip()
        u = self.current_user
        if self._lan_manager is None:
            self._lan_manager = lan_module.LANManager()
            self._lan_manager.start_discovery(self._on_lan_rooms_updated_bg)
        self._lan_manager.host_room(
            room_name,
            u.get("full_name", u.get("username", "Unknown")),
            u.get("department", ""),
            u.get("class_name", ""),
            u.get("section", ""),
        )
        self._lan_host_btn.config(text="■ Stop Hosting", bg=self.theme["danger"],
                                  command=self._on_stop_hosting_clicked)
        self._lan_status_lbl.config(text=f"Hosting '{room_name}'")
        play_success_sound()
        self._draw_lan_hosting_view(room_name)

    def _on_stop_hosting_clicked(self):
        if self._lan_manager:
            self._lan_manager.stop_hosting()
        self._lan_host_btn.config(text="📡 Host a Study Room", bg=self.theme["success"],
                                  command=self._on_host_room_clicked)
        self._lan_status_lbl.config(text="Searching on local network…")
        self._draw_lan_placeholder()

    def _draw_group_details_placeholder(self):
        for w in self.group_details_frame.winfo_children():
            w.destroy()
            
        placeholder = tk.Label(self.group_details_frame, text="Select a study group from the list to view tasks & members",
                               font=("Segoe UI", 11, "italic"), bg=self.theme["bg_main"], fg=self.theme["text_muted"])
        placeholder.pack(expand=True)

    def _refresh_groups_tab(self):
        self.groups_listbox.delete(0, "end")
        self.user_groups = self.db.get_user_groups(self.current_user["id"])
        for grp in self.user_groups:
            self.groups_listbox.insert("end", grp["name"])

        self._draw_group_details_placeholder()
        self.selected_group_id = None
        self.btn_delete_grp.grid_remove()  # nothing selected -> hide delete

    def _on_group_select(self, event=None):
        selection = self.groups_listbox.curselection()
        if not selection:
            self.selected_group_id = None
            self.btn_delete_grp.grid_remove()
            return

        idx = selection[0]
        group = self.user_groups[idx]
        self.selected_group_id = group["id"]

        self.btn_delete_grp.grid()  # a group is selected -> show delete
        self._draw_group_details(group)

    def _delete_selected_group(self):
        if self.selected_group_id is None:
            return
        group = next((g for g in self.user_groups if g["id"] == self.selected_group_id), None)
        name = group["name"] if group else "this group"
        if not messagebox.askyesno(
                "Delete Group",
                f"Delete the study group '{name}'?\n\nThis removes all its shared tasks and members and cannot be undone."):
            return
        try:
            self.db.delete_study_group(self.selected_group_id, self.current_user["id"])
            play_success_sound()
            messagebox.showinfo("Deleted", f"Study group '{name}' was deleted.")
            self.selected_group_id = None
            self._refresh_groups_tab()
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", str(exc))

    def _draw_group_details(self, group):
        for w in self.group_details_frame.winfo_children():
            w.destroy()
            
        self.group_details_frame.grid_columnconfigure(0, weight=1)
        self.group_details_frame.grid_columnconfigure(1, weight=1)
        self.group_details_frame.grid_rowconfigure(1, weight=1)
        self.group_details_frame.grid_rowconfigure(2, weight=1)

        header = tk.Frame(self.group_details_frame, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                          highlightthickness=1, bd=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        tk.Label(header, text=group["name"], font=("Segoe UI", 14, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["primary"]).pack(anchor="w", padx=15, pady=(10, 2))
        tk.Label(header, text=f"Created on: {group['created_at']}", font=("Segoe UI", 9),
                 bg=self.theme["bg_card"], fg=self.theme["text_muted"]).pack(anchor="w", padx=15, pady=(0, 10))

        members_card = tk.Frame(self.group_details_frame, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                                highlightthickness=1, bd=0)
        members_card.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))
        members_card.grid_rowconfigure(1, weight=1)
        members_card.grid_columnconfigure(0, weight=1)

        tk.Label(members_card, text="Group Members", font=("Segoe UI", 11, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", padx=15, pady=10)

        members_list = tk.Listbox(members_card, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                  highlightthickness=0, bd=0, font=("Segoe UI", 9))
        members_list.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))

        members = self.db.get_group_members(group["id"])
        for mem in members:
            members_list.insert("end", f"{mem['full_name']} ({mem['email']})")

        btn_add_mem = create_flat_button(members_card, "Add Member Email", self.theme["primary"], "#ffffff",
                                         self._add_group_member, hover_bg=self.theme["primary_hover"], font=("Segoe UI", 9, "bold"))
        btn_add_mem.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

        tasks_card = tk.Frame(self.group_details_frame, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                              highlightthickness=1, bd=0)
        tasks_card.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))
        tasks_card.grid_rowconfigure(1, weight=1)
        tasks_card.grid_columnconfigure(0, weight=1)

        tk.Label(tasks_card, text="Collaborative Study Tasks", font=("Segoe UI", 11, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", padx=15, pady=10)

        columns = ("title", "priority", "deadline", "status")
        tasks_tree = ttk.Treeview(tasks_card, columns=columns, show="headings", height=8)
        tasks_tree.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))

        tasks_tree.heading("title", text="Task Title")
        tasks_tree.heading("priority", text="Priority")
        tasks_tree.heading("deadline", text="Deadline")
        tasks_tree.heading("status", text="Status")

        tasks_tree.column("title", width=130, anchor="w")
        tasks_tree.column("priority", width=70, anchor="center")
        tasks_tree.column("deadline", width=80, anchor="center")
        tasks_tree.column("status", width=80, anchor="center")

        g_tasks = self.db.get_group_tasks(group["id"])
        for gt in g_tasks:
            tasks_tree.insert("", "end", values=(gt["title"], gt["priority"], gt["deadline"], gt["status"]))

        btn_add_tsk = create_flat_button(tasks_card, "Add Group Task", self.theme["success"], "#ffffff",
                                         self._add_group_task, hover_bg=self.theme["success_hover"], font=("Segoe UI", 9, "bold"))
        btn_add_tsk.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

        sessions_card = tk.Frame(self.group_details_frame, bg=self.theme["bg_card"], highlightbackground=self.theme["border"],
                                 highlightthickness=1, bd=0)
        sessions_card.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(5, 0))
        sessions_card.grid_rowconfigure(1, weight=1)
        sessions_card.grid_columnconfigure(0, weight=1)

        tk.Label(sessions_card, text="Scheduled Group Study Sessions", font=("Segoe UI", 11, "bold"),
                 bg=self.theme["bg_card"], fg=self.theme["text_primary"]).grid(row=0, column=0, sticky="w", padx=15, pady=10)

        sessions_list = tk.Listbox(sessions_card, bg=self.theme["bg_main"], fg=self.theme["text_primary"],
                                   highlightthickness=0, bd=0, font=("Segoe UI", 9))
        sessions_list.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))

        sessions = [gt for gt in g_tasks if gt["category"] == "Study" and gt["title"].startswith("Study Session:")]
        if not sessions:
            sessions_list.insert("end", "No virtual study sessions scheduled yet.")
        else:
            for s in sessions:
                sessions_list.insert("end", f"{s['title']} — Scheduled Date: {s['deadline']} (Status: {s['status']})")

        btn_sched_session = create_flat_button(sessions_card, "Schedule Study Session", self.theme["warning"], "#ffffff",
                                               self._schedule_group_study_session, hover_bg=self.theme["warning_hover"], font=("Segoe UI", 9, "bold"))
        btn_sched_session.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

    def _create_new_group(self):
        play_click_sound()
        name = ModernInputDialog.ask(self.parent, "Create Group", "Enter the name of your new study group:")
        if not name or not name.strip():
            return
            
        try:
            self.db.create_study_group(name.strip(), self.current_user["id"])
            play_success_sound()
            messagebox.showinfo("Success", f"Group '{name.strip()}' created successfully!")
            self._refresh_groups_tab()
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", f"Failed to create group: {exc}")

    def _add_group_member(self):
        play_click_sound()
        if not self.selected_group_id:
            return
            
        email = ModernInputDialog.ask(self.parent, "Add Member", "Enter student email address to add:")
        if not email or not email.strip():
            return
            
        email = email.strip()
        if not validate_email(email):
            play_error_sound()
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            success = self.db.add_group_member_by_email(self.selected_group_id, email)
            if success:
                play_success_sound()
                messagebox.showinfo("Success", f"Student '{email}' added to group successfully!")
                group = [g for g in self.user_groups if g["id"] == self.selected_group_id][0]
                self._draw_group_details(group)
            else:
                play_error_sound()
                messagebox.showerror("Error", "User not found with that email address.")
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", f"Failed to add member: {exc}")

    def _add_group_task(self):
        play_click_sound()
        if not self.selected_group_id:
            return
            
        title = ModernInputDialog.ask(self.parent, "Group Task", "Enter task title:")
        if not title or not title.strip():
            return

        priority = ModernInputDialog.ask(self.parent, "Group Task", "Priority (High, Medium, Low):", initialvalue="Medium")
        if priority not in ("High", "Medium", "Low"):
            priority = "Medium"

        deadline = ModernInputDialog.ask(self.parent, "Group Task", "Deadline (YYYY-MM-DD):", initialvalue=date.today().strftime("%Y-%m-%d"))
        if not deadline:
            return
        if not parse_date(deadline):
            play_error_sound()
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        category = ModernInputDialog.ask(self.parent, "Group Task", "Category (e.g. Study, Assignment, Project):", initialvalue="Study")
        if not category:
            category = "Study"

        try:
            self.db.add_group_task(self.selected_group_id, title.strip(), priority, deadline, category)
            play_success_sound()
            messagebox.showinfo("Success", "Group task added successfully!")
            
            group = [g for g in self.user_groups if g["id"] == self.selected_group_id][0]
            self._draw_group_details(group)
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", f"Failed to add task: {exc}")

    def _schedule_group_study_session(self):
        play_click_sound()
        if not self.selected_group_id:
            return
            
        topic = ModernInputDialog.ask(self.parent, "Schedule Study Session", "Enter study session topic:")
        if not topic or not topic.strip():
            return

        session_date = ModernInputDialog.ask(self.parent, "Schedule Study Session", "Date (YYYY-MM-DD):", initialvalue=date.today().strftime("%Y-%m-%d"))
        if not session_date:
            return
        if not parse_date(session_date):
            play_error_sound()
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        session_time = ModernInputDialog.ask(self.parent, "Schedule Study Session", "Time (e.g., 14:00, 16:30):", initialvalue="15:00")
        if not session_time:
            session_time = "15:00"

        title = f"Study Session: {topic.strip()} at {session_time}"

        try:
            self.db.add_group_task(self.selected_group_id, title, "Medium", session_date, "Study")
            play_success_sound()
            messagebox.showinfo("Success", f"Study Session on '{topic}' scheduled successfully!")
            
            group = [g for g in self.user_groups if g["id"] == self.selected_group_id][0]
            self._draw_group_details(group)
        except Exception as exc:
            play_error_sound()
            messagebox.showerror("Error", f"Failed to schedule study session: {exc}")

    # --- SESSION MANAGEMENT ---

    def _logout(self):
        lang = self.parent.current_lang
        if messagebox.askyesno("Log Out", TRANSLATIONS[lang]["msg_logout_confirm"]):
            stop_soundscape()
            if getattr(self, "_lan_manager", None) is not None:
                self._stop_lan_discovery()
            self.manager.save()
            self.on_logout_trigger()


class StudyPlannerGUI(tk.Tk):
    """Main Application Controller Frame."""

    PREFS_FILE = "data/app_prefs.json"

    def __init__(self):
        super().__init__()
        self.title("Smart Study Planner")
        self.geometry("960x650")
        self.minsize(920, 600)

        # Application/taskbar icon (works in dev and in the PyInstaller build).
        try:
            self.iconbitmap(get_resource_path("assets/icon.ico"))
        except Exception:
            pass

        self.current_theme = "dark" # default slate dark theme
        self.current_lang = "en" # default language preference
        self.configure(bg=THEMES[self.current_theme]["bg_main"])

        self.db = DatabaseManager(DB_FILE)
        self.current_user = None

        # Lightweight, non-sensitive preferences (last login id, sound on/off).
        self._prefs = self._load_prefs()
        self.last_login = self._prefs.get("last_login", "")
        set_sound_enabled(self._prefs.get("sound_enabled", True))

        # Confirm before closing via the window's X button.
        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        self.active_frame = None
        self._show_auth_panel()

    # --- Preferences persistence (last login + sound toggle) ---

    def _load_prefs(self):
        try:
            with open(self.PREFS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _save_prefs(self):
        try:
            os.makedirs(os.path.dirname(self.PREFS_FILE), exist_ok=True)
            with open(self.PREFS_FILE, "w", encoding="utf-8") as fh:
                json.dump(self._prefs, fh)
        except OSError:
            pass

    def set_pref(self, key, value):
        self._prefs[key] = value
        self._save_prefs()

    def _clear_active_frame(self):
        if self.active_frame is not None:
            self.active_frame.destroy()
            self.active_frame = None

    def _show_auth_panel(self, restore_state=None):
        self._clear_active_frame()
        self.current_user = None

        self.active_frame = AuthFrame(self, self.db, THEMES[self.current_theme],
                                      self._on_login_success, initial_state=restore_state)
        self.active_frame.pack(fill="both", expand=True)

    def _on_login_success(self, user):
        self.current_user = user
        self.current_lang = user.get("language", "en")
        # Remember the identifier the user logged in with for faster next sign-in.
        self.last_login = user.get("username") or user.get("email", "")
        self.set_pref("last_login", self.last_login)
        self._show_planner_panel()

    def _show_planner_panel(self, restore_tab="tasks"):
        self._clear_active_frame()
        self.active_frame = PlannerFrame(
            self,
            self.current_user,
            self.db,
            THEMES[self.current_theme],
            self._show_auth_panel,
            self.toggle_theme,
            self.current_theme,
            initial_tab=restore_tab
        )
        self.active_frame.pack(fill="both", expand=True)

    def toggle_theme(self):
        # Stop any ambient loop before tearing down/rebuilding the frame.
        stop_soundscape()
        # Swap theme name
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.configure(bg=THEMES[self.current_theme]["bg_main"])

        # Reload frames with new colors while preserving navigation + form state,
        # so a theme switch never bounces the user back to a different screen.
        if self.current_user:
            current_tab = getattr(self.active_frame, "active_tab", "tasks")
            self._show_planner_panel(restore_tab=current_tab)
        else:
            state = self.active_frame.capture_state() if self.active_frame else None
            self._show_auth_panel(restore_state=state)

    def confirm_exit(self):
        """Ask for confirmation before closing to prevent accidental data loss."""
        lang = self.current_lang
        title = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get("exit_confirm_title", "Exit Application")
        msg = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(
            "exit_confirm_msg", "Are you sure you want to exit Smart Study Planner?")
        play_click_sound()
        if messagebox.askyesno(title, msg):
            stop_soundscape()
            self.destroy()


def main():
    app = StudyPlannerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
