"""
LAN connectivity module for Smart Study Planner.
Author: Mohammad Sufiyan Aasim (SufiyanAasim)

UDP broadcast on port 50505 for peer/room discovery.
Rooms are self-announcing; discovery is purely passive (no TCP needed for v1.2.5).
"""

import socket
import threading
import json
import time

DISCOVERY_PORT = 50505
BROADCAST_INTERVAL = 3   # seconds between beacon pulses
STALE_TIMEOUT = 10        # seconds before a room is removed from the discovered list


def get_local_ip():
    """Return the machine's outbound LAN IP (not 127.x)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


class LANManager:
    """
    Manages LAN study-room advertisement and discovery.

    Usage:
        mgr = LANManager()
        mgr.start_discovery(callback)          # start passive listening
        mgr.host_room("OS Study", user, dept, cls, section)  # advertise a room
        mgr.stop_hosting()                     # stop advertising
        mgr.stop()                             # full shutdown
    """

    def __init__(self):
        self._local_ip = get_local_ip()
        self._stop_event = threading.Event()

        self._discovery_thread = None
        self._beacon_thread = None

        self.is_hosting = False
        self._room_info: dict = {}

        # {ip_str: {"room": ..., "host": ..., "department": ..., ...}}
        self.discovered_rooms: dict = {}
        self._on_rooms_updated = None   # callable(dict)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_discovery(self, callback):
        """Begin listening for room broadcasts and call *callback* on any change."""
        self._on_rooms_updated = callback
        self._stop_event.clear()
        self._discovery_thread = threading.Thread(
            target=self._discovery_loop, daemon=True, name="lan-discovery"
        )
        self._discovery_thread.start()

    def host_room(self, room_name, user_name, department, class_name, section):
        """Broadcast a study room so peers can discover it."""
        self._room_info = {
            "room": room_name,
            "host": user_name,
            "department": department,
            "class": class_name,
            "section": section,
        }
        self.is_hosting = True
        if self._beacon_thread is None or not self._beacon_thread.is_alive():
            self._beacon_thread = threading.Thread(
                target=self._beacon_loop, daemon=True, name="lan-beacon"
            )
            self._beacon_thread.start()

    def stop_hosting(self):
        """Stop advertising the current room (discovery keeps running)."""
        self.is_hosting = False
        self._room_info = {}

    def stop(self):
        """Shut down all background threads."""
        self.is_hosting = False
        self._room_info = {}
        self._stop_event.set()

    # ------------------------------------------------------------------
    # Internal loops (run in daemon threads)
    # ------------------------------------------------------------------

    def _beacon_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(1.0)
        while self.is_hosting and not self._stop_event.is_set():
            try:
                payload = json.dumps(self._room_info).encode("utf-8")
                sock.sendto(payload, ("<broadcast>", DISCOVERY_PORT))
            except Exception:
                pass
            # Sleep in small increments so the loop stays responsive to stop signals.
            for _ in range(BROADCAST_INTERVAL * 5):
                if not self.is_hosting or self._stop_event.is_set():
                    break
                time.sleep(0.2)
        sock.close()

    def _discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", DISCOVERY_PORT))
        except OSError:
            # Port already in use (another instance) — can't listen.
            return
        sock.settimeout(1.0)

        last_seen: dict = {}   # ip → float timestamp

        while not self._stop_event.is_set():
            try:
                data, addr = sock.recvfrom(2048)
                ip = addr[0]

                # Ignore our own broadcasts.
                if ip == self._local_ip:
                    continue

                try:
                    info = json.loads(data.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

                info["_ip"] = ip
                changed = self.discovered_rooms.get(ip) != info
                self.discovered_rooms[ip] = info
                last_seen[ip] = time.time()

                if changed and self._on_rooms_updated:
                    try:
                        self._on_rooms_updated(dict(self.discovered_rooms))
                    except Exception:
                        pass

            except socket.timeout:
                pass
            except Exception:
                pass

            # Evict stale rooms.
            now = time.time()
            stale = [ip for ip, t in last_seen.items() if now - t >
                     STALE_TIMEOUT]
            if stale:
                for ip in stale:
                    self.discovered_rooms.pop(ip, None)
                    last_seen.pop(ip, None)
                if self._on_rooms_updated:
                    try:
                        self._on_rooms_updated(dict(self.discovered_rooms))
                    except Exception:
                        pass

        sock.close()
