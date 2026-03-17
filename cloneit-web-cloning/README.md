# Skill

This folder packages the main website-cloning skill as a self-contained unit that is easy to push, share, and run.

## What This Folder Contains

- `SKILL.md`: the main skill definition
- `scripts/clone_with_gemini.py`: the runtime entrypoint
- `assets/`: prompts, configuration, and Python requirements
- `references/`: supporting documentation
- `Dockerfile`: isolated container path for first-run execution

## What The Skill Does

The skill clones a source website URL into a single-file HTML replica using Gemini. It supports:

- automatic runtime bootstrap
- fallback when host Python does not support `venv`
- optional prompt expansion for short user instructions
- browser capture and stylesheet extraction
- canonical artifact output plus compatibility aliases

## Quick Start

From the repository root:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"
```

If this folder is used on its own, run from inside the folder:

```bash
python3 scripts/clone_with_gemini.py "https://example.com"
```

## Required Setup

- Python 3.11+ with `pip`, or Docker
- `GOOGLE_GEMINI_API_KEY` set in the environment or available in a local `.env`
- network access to PyPI, Playwright downloads, and the Gemini API

## Docker Path

```bash
docker build -t skill .
docker run --rm -it --ipc=host \
  -e GOOGLE_GEMINI_API_KEY="$GOOGLE_GEMINI_API_KEY" \
  -v "$(pwd)/../outputs:/outputs" \
  skill \
  "https://example.com" \
  --out-dir /outputs/replica_demo
```

## Recommended Push Scope

If you want to push only the main skill package, this folder is the unit to push:

- `cloneit-web-cloning/`

That includes the skill file, README, scripts, prompts, references, and Docker setup needed by the workflow.
