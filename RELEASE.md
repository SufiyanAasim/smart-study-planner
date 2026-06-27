# Release Process

This document describes how to cut a new release of Smart Study Planner.

---

## 1. Decide version and codename

Use [Semantic Versioning](https://semver.org/):

| Change type | Bump |
|-------------|------|
| Breaking change | MAJOR |
| New feature | MINOR |
| Bug fix only | PATCH |

Choose a codename from a single theme (Space series: Nova, Comet, Nebula, Polaris, …).

Format:
```
v1.3.0
Codename: Nova
```

---

## 2. Update version references

Update the version string in:
- `src/gui.py` — Credits screen version label
- `README.md` — version badge / header line
- `CHANGELOG.md` — new section header

---

## 3. Write the changelog entry

Add a new section to `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [4.0.0] — "Nova" — YYYY-MM-DD

### Added
### Changed
### Improved
### Fixed
### Removed
### Security
```

---

## 4. Write the release doc

Create `docs/releases/v1.3.0.md` using the template in any existing release file as a reference. Include: codename, highlights, full categorized change list, and compatibility table.

---

## 5. Run the test suite

```bash
python -m unittest discover -s tests
```

All tests must pass before tagging.

---

## 6. Commit and tag

```bash
git add -A
git commit -m "release: v1.3.0 - Nova"
git tag v1.3.0
git push origin main --tags
```

Include co-authors in the commit message if applicable:
```
release: v4.0.0 - Nova

Co-authored-by: Contributor Name <their-github-registered-email@example.com>
```

---

## 7. GitHub release

Create a GitHub release from tag `v4.0.0`. Paste the contents of `docs/releases/v4.0.0.md` into the release body. Attach `SmartStudyPlanner.exe` as a release asset, named:

```
SmartStudyPlanner-v1.3.0-windows-x64.exe
```

---

## 8. Update ROADMAP.md

Move the shipped items out of the roadmap and into the changelog reference.
