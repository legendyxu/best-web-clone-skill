# Skill - Website Cloning

This folder contains a self-contained website-cloning skill that turns a source URL into a single-file HTML replica using Gemini.

## Package Contents

- `README.md`: human-facing overview and quick-start guide
- `SKILL.md`: agent-facing skill definition
- `runtime.md`: managed runtime behavior and fallback rules
- `docker.md`: Docker-based execution path
- `prompt-expansion.md`: instruction expansion behavior
- `artifacts.md`: stage names and output contract
- `troubleshooting.md`: common failures and remediation
- `scripts/clone_with_gemini.py`: workflow entrypoint
- `assets/`: prompts, config, and Python requirements
- `references/`: additional supporting documentation
- `Dockerfile`: container image definition

## Quick Start

From the repository root:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"
```

From inside this folder:

```bash
python3 scripts/clone_with_gemini.py "https://example.com"
```

## Required Setup

- Python 3.11+ with `pip`, or Docker
- `GOOGLE_GEMINI_API_KEY` set in the environment or provided through a local `.env`
- network access to PyPI, Playwright downloads, and the Gemini API

## Documentation

- [Runtime](runtime.md)
- [Docker](docker.md)
- [Prompt Expansion](prompt-expansion.md)
- [Artifacts](artifacts.md)
- [Troubleshooting](troubleshooting.md)

## Folder Scope

If you want to push the main cloning skill as a standalone package, push:

- `cloneit-web-cloning/`

This directory contains the skill definition, runtime entrypoint, prompts, docs, and Docker path needed by the workflow.
