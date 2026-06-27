# Troubleshooting

## Application won't start

**Error:** `ModuleNotFoundError: No module named 'PIL'`
```bash
pip install Pillow
```

**Error:** `ModuleNotFoundError: No module named 'tkinter'`
On Linux, Tkinter is a separate package:
```bash
sudo apt install python3-tk       # Debian/Ubuntu
sudo dnf install python3-tkinter  # Fedora
```

---

## Blank Focus Timer screen

The timer panel requires a minimum window size to render correctly. Resize the window to at least 920×600 pixels or check that no monitor scaling is set above 200%.

---

## Sound effects not playing

1. Verify sound is enabled: **Settings → Sound & Feedback → Enable Sounds**.
2. Check that `assets/sounds/` exists and contains `.wav` files. If they are missing, re-clone the repository.
3. On Linux, ensure a compatible audio backend is available (`pulseaudio` or `pipewire`).

---

## Charmap encoding errors in the terminal (Windows)

Run the application with UTF-8 output:
```cmd
set PYTHONIOENCODING=utf-8
python main.py
```
Or use the `--cli` flag from PowerShell, which handles encoding automatically.

---

## Database locked / `OperationalError: database is locked`

Only one instance of the application should access the database at a time. Close any other running instances and try again. If the error persists, the `data/planner.db` file may be corrupted — rename it and restart (a fresh database will be created).

---

## Tests failing with `ModuleNotFoundError`

Run tests from the project root, not from inside `tests/`:
```bash
python -m unittest discover -s tests
```

---

## Password recovery not working

The security answer comparison is case-insensitive and trims leading/trailing whitespace. If recovery still fails, ensure you are answering the same question that was selected during registration. There is no server-side reset — the answer hash must match.

---

## `.exe` opens a black terminal window

Ensure the executable was built with the `--noconsole` flag. Rebuild using the provided spec file:
```bash
python -m PyInstaller SmartStudyPlanner.spec
```
