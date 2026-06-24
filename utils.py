"""
utils.py
Helper functions for reading user inputs safely from the terminal, validating dates
and priorities, displaying text-based progress bars, and security utilities.
Author: Mohammad Sufiyan Aasim (msufiyanpk)
"""

import hashlib
import os
import re
import secrets
from datetime import datetime
from models import PRIORITY_LEVELS, DATE_FORMAT


# --- Security & Hashing Utilities ---

def hash_password(password, salt=None):
    """Hashes a password using PBKDF2 with SHA-256 and a random salt."""
    if not salt:
        salt = secrets.token_hex(16)
    # Convert password and salt to bytes
    password_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    
    # Hash password using PBKDF2 HMAC SHA-256
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", password_bytes, salt_bytes, 100000
    )
    return salt, hash_bytes.hex()


def validate_email(email):
    """Checks if an email follows a standard valid format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password_strength(password):
    """Enforces secure passwords: >=8 chars, uppercase, lowercase, number, special character."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?`~" for c in password):
        return False, "Password must contain at least one special character."
    return True, ""


def validate_full_name(name):
    """Validates that a full name has at least 2 words or letters and only basic characters."""
    clean_name = name.strip()
    if len(clean_name) < 2:
        return False
    # Permit letters, spaces, hyphens, and apostrophes
    return re.match(r"^[a-zA-Z\s'-]+$", clean_name) is not None


# --- Input Reading & CLI Utilities ---

def get_non_empty_string(prompt, allow_exit=False):
    """Repeatedly prompts the user until they enter a non-empty string."""
    while True:
        value = input(prompt).strip()
        if allow_exit and value == "0":
            return None
        if value:
            return value
        print("  ! Input cannot be empty. Please try again.")


def get_valid_int(prompt, allow_exit=False):
    """Prompts the user until they enter a valid whole number."""
    while True:
        raw = input(prompt).strip()
        if allow_exit and raw == "0":
            return None
        try:
            return int(raw)
        except ValueError:
            print("  ! Please enter a valid whole number.")


def get_menu_choice(prompt, valid_choices):
    """Enforces that the user picks an option that exists in our menu list."""
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"  ! Invalid option. Choose one of: {', '.join(valid_choices)}")


def get_valid_priority(prompt, allow_exit=False):
    """Prompts for and returns a valid priority (High, Medium, Low), auto-correcting casing."""
    options = " / ".join(PRIORITY_LEVELS)
    while True:
        value = input(f"{prompt} ({options}): ").strip().capitalize()
        if allow_exit and value == "0":
            return None
        if value in PRIORITY_LEVELS:
            return value
        print(f"  ! Priority must be one of: {options}")


def parse_date(text):
    """Tries to convert a YYYY-MM-DD string into a datetime.date object. Returns None if it fails."""
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).date()
    except (ValueError, AttributeError):
        return None


def get_valid_date(prompt, allow_exit=False):
    """Prompts for a date until the user inputs a valid YYYY-MM-DD calendar date."""
    while True:
        raw = input(f"{prompt} (YYYY-MM-DD): ").strip()
        if allow_exit and raw == "0":
            return None
        result = parse_date(raw)
        if result is not None:
            return result
        print("  ! Invalid date. Use the format YYYY-MM-DD, e.g. 2026-07-15.")


def confirm(prompt):
    """Simple yes/no confirmation utility."""
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer in ("y", "yes")


def text_bar(count, total, width=20):
    """Creates a terminal-friendly progress bar (e.g. [#####-----] 50%)."""
    if total == 0:
        percent = 0
    else:
        percent = int((count / total) * 100)
    filled = int((percent / 100) * width)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {percent}%"


# --- Audio Feedback ---
# Global toggle so users can silence the app from Settings. Respected by every
# play_* helper below; the OS still governs the actual output volume.
_SOUND_ENABLED = True

# Bespoke, synthesized sound effects bundled in assets/sounds/. Each helper plays
# its custom .wav and gracefully falls back to a Windows system alias if the file
# is missing or audio is unavailable.
_SOUND_FILES = {
    "click": "assets/sounds/click.wav",
    "success": "assets/sounds/success.wav",
    "error": "assets/sounds/error.wav",
    "notify": "assets/sounds/notify.wav",
}
_SYSTEM_FALLBACK = {
    "click": "SystemDefault",
    "success": "SystemAsterisk",
    "error": "SystemHand",
    "notify": "SystemExclamation",
}


# Looping ambient soundscapes for the Focus Timer. winsound has a single output
# channel, so while a soundscape loops we suppress the short UI cues (a click would
# otherwise stop the loop). Volume is applied by re-rendering a scaled temp copy.
_SOUNDSCAPE_FILES = {
    "Lo-Fi Beats": "assets/sounds/scape_lofi.wav",
    "Rainforest": "assets/sounds/scape_rain.wav",
    "White Noise": "assets/sounds/scape_white.wav",
    "Ocean Waves": "assets/sounds/scape_ocean.wav",
    "Warm Fireplace": "assets/sounds/scape_fire.wav",
}
_SOUNDSCAPE_ACTIVE = False
_soundscape_tmp = None


def set_sound_enabled(enabled):
    """Enable or disable all application sound effects."""
    global _SOUND_ENABLED
    _SOUND_ENABLED = bool(enabled)


def is_sound_enabled():
    """Returns whether application sound effects are currently enabled."""
    return _SOUND_ENABLED


def is_soundscape_active():
    """Returns whether an ambient soundscape loop is currently playing."""
    return _SOUNDSCAPE_ACTIVE


def play_soundscape(name, volume=70):
    """Loop the named ambient soundscape at ``volume`` (0-100). Returns True on success."""
    global _SOUNDSCAPE_ACTIVE, _soundscape_tmp
    stop_soundscape()
    rel = _SOUNDSCAPE_FILES.get(name)
    if not rel:
        return False
    base = get_resource_path(rel)
    if not os.path.exists(base):
        return False
    try:
        import wave
        import array
        import tempfile
        import winsound
        with wave.open(base, "rb") as w:
            params = w.getparams()
            frames = w.readframes(w.getnframes())
        samples = array.array("h")
        samples.frombytes(frames)
        v = max(0.0, min(1.0, volume / 100.0))
        for i in range(len(samples)):
            s = int(samples[i] * v)
            samples[i] = -32768 if s < -32768 else (32767 if s > 32767 else s)
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        with wave.open(tmp_path, "wb") as out:
            out.setparams(params)
            out.writeframes(samples.tobytes())
        _soundscape_tmp = tmp_path
        winsound.PlaySound(tmp_path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        _SOUNDSCAPE_ACTIVE = True
        return True
    except Exception:
        _SOUNDSCAPE_ACTIVE = False
        return False


def stop_soundscape():
    """Stop any looping soundscape and clean up its temp file."""
    global _SOUNDSCAPE_ACTIVE, _soundscape_tmp
    if _SOUNDSCAPE_ACTIVE:
        try:
            import winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
    _SOUNDSCAPE_ACTIVE = False
    if _soundscape_tmp:
        try:
            os.remove(_soundscape_tmp)
        except Exception:
            pass
        _soundscape_tmp = None


def _play(kind):
    """Plays the bundled .wav for ``kind`` asynchronously, with a system fallback."""
    if not _SOUND_ENABLED:
        return
    # Single winsound channel: don't interrupt an active ambient loop with UI cues.
    if _SOUNDSCAPE_ACTIVE:
        return
    try:
        import os
        import winsound
        path = get_resource_path(_SOUND_FILES[kind])
        if os.path.exists(path):
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            winsound.PlaySound(_SYSTEM_FALLBACK[kind], winsound.SND_ALIAS | winsound.SND_ASYNC)
    except Exception:
        pass


def play_click_sound():
    """Plays a subtle asynchronous click tick."""
    _play("click")


def play_success_sound():
    """Plays a gentle ascending success chime."""
    _play("success")


def play_error_sound():
    """Plays a soft descending error tone."""
    _play("error")


def play_notify_sound():
    """Plays the timer/notification arpeggio."""
    _play("notify")


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.

    In dev we anchor to this file's directory (the project root) rather than the
    current working directory, so bundled assets (images, sounds) resolve even
    when the app is launched from a different folder."""
    import sys
    import os
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
