# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.2.x   | Yes       |
| 1.1.x   | No        |
| 1.0.x   | No        |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately by emailing:

**sufiyanaasim@outlook.com**

Include in your report:
- A clear description of the vulnerability.
- Steps to reproduce or a proof-of-concept.
- The potential impact.
- Your suggested fix, if any.

You will receive a response within 7 days. If the vulnerability is confirmed, a patch will be released as a priority and you will be credited in the release notes unless you prefer to remain anonymous.

## Security model

- Passwords and security answers are hashed with PBKDF2-HMAC-SHA-256 (100,000 iterations, random salts per user). Plaintext secrets are never stored.
- All database queries are fully parameterized — no string interpolation.
- Per-user data isolation is enforced at the query layer: every read/write includes a `WHERE user_id = ?` constraint.
- The application stores all data locally. No data is transmitted over a network in the current release.
