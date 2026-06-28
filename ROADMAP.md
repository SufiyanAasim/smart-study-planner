# Roadmap

## v1.2.5 — Apex ✅ Shipped

- **LAN Study Rooms.** UDP broadcast discovery (port 50505). Host a named study room; peers on the same network see it within seconds. No server or account needed on the network layer.
- **Academic Profile.** Department, Class/Batch, Section, and Batch Year fields on Registration and Settings. Shown in sidebar and LAN room beacons.
- **LAN manager module.** `src/lan.py` — `LANManager` with daemon-thread I/O and stale-room eviction.

## v1.3.0 — Intelligence (planned)

- AI-assisted study scheduling based on deadline proximity and historical completion patterns.
- Smart task prioritization suggestions.
- Personalized study-load warnings.
- Class Hub panel: shared timetable and class-wide tasks, filtered by department/batch/section.
- Real-time LAN sync: shared task updates and basic in-room chat over the local network.

## Ongoing

- Additional language translations.
- Performance improvements to the GUI canvas rendering.
- Expanded test coverage.

---

Roadmap items are subject to change. Check [CHANGELOG.md](CHANGELOG.md) for what has shipped.
