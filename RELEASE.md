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

Codenames follow a single consistent theme across all releases.

Format:
```
v1.3.0
Codename: Intelligence
```

---

## 2. Update version references

Update the version string in:
- `src/gui.py` — Credits screen version label
- `README.md` — version badge
- `CHANGELOG.md` — new section header and footer reference link

---

## 3. Write the changelog entry

Add a new section to `CHANGELOG.md` following the [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [1.3.0] — "Intelligence" — YYYY-MM-DD

### Added
### Changed
### Improved
### Fixed
### Removed
### Security
```

---

## 4. Write the release doc

Create `docs/releases/v1.3.0.md` using any existing release file as a template. Include: codename, release type, overview, full categorized change list, and compatibility table.

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
git commit -m "release: v1.3.0 - Intelligence"
git tag v1.3.0
git push origin main --tags
```

Include co-authors in the commit message if applicable:
```
release: v1.3.0 - Intelligence

Co-authored-by: Contributor Name <their-github-registered-email@example.com>
```

---

## 7. GitHub release

Create a GitHub release from tag `v1.3.0`. Paste the contents of `docs/releases/v1.3.0.md` into the release body. Attach `SmartStudyPlanner.exe` as a release asset, named:

```
SmartStudyPlanner-v1.3.0-windows-x64.exe
```

---

## 8. Update ROADMAP.md

Mark the shipped version as ✅ Shipped and promote the next planned version.
