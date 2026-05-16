# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | :white_check_mark: |
| < latest| :x:                |

Only the latest release receives security updates.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, report privately using one of these channels:

- **GitHub Security Advisory** (preferred) — navigate to the repository's Security tab and click "Report a vulnerability".
- **Email** — if a maintainer email is listed in the commit history, send your report there.

You can expect:

1. **Acknowledgement** within 48 hours
2. **Status updates** every 7 days until resolution
3. **Coordinated disclosure** — we aim to patch within 90 days for critical issues

## Scope

This project handles API keys (`GOOGLE_GEMINI_API_KEY`) and makes outbound requests to third-party services. The following are in scope:

- Exposure of credentials through code, logs, or git history
- Remote code execution or injection vulnerabilities
- Dependency supply chain risks during runtime bootstrap
- Insecure handling of user-provided URLs or file paths

When reporting, include:

- A clear description of the vulnerability and its impact
- Steps to reproduce the issue
- Affected versions or commit hashes
- Any suggested fix or mitigation, if known

## Preferred Language

English preferred; Chinese also accepted.

## Disclosure Policy

We follow coordinated disclosure. After a fix is published, reporters will be credited in the release notes unless anonymity is requested.
