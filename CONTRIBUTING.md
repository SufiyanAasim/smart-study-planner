# Contributing

Thank you for your interest in Smart Study Planner. Contributions are welcome — please read this guide before opening a pull request.

---

## Getting started

1. Fork the repository and clone your fork.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the test suite to confirm everything works: `python -m unittest discover -s tests`
4. Create a branch: `git checkout -b feature/your-feature-name`

## Commit convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use for |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation only |
| `refactor:` | Code restructuring without behavior change |
| `perf:` | Performance improvements |
| `test:` | Test additions or fixes |
| `chore:` | Build scripts, dependency updates |
| `ci:` | CI/CD configuration |

**Examples:**
```
feat(gui): add department profile fields
fix(auth): handle empty username on login
docs(readme): update installation section
```

## Pull request guidelines

- Keep PRs focused — one feature or fix per PR.
- All new features must include tests.
- Run `python -m unittest discover -s tests` and confirm all tests pass before submitting.
- Fill in the pull request template fully.
- Reference any related issues with `Closes #n`.

## Code style

- Follow PEP 8.
- No commented-out code in submitted PRs.
- Keep comments to the minimum needed to explain *why*, not *what*.

## Reporting bugs

Use the Bug Report issue template. Include:
- Python version and OS.
- Steps to reproduce.
- Expected vs. actual behavior.
- Any relevant error output.

## Security vulnerabilities

Do **not** open a public issue for security vulnerabilities. See [SECURITY.md](SECURITY.md).
