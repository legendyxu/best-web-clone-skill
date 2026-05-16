<div align="center">
  <h1>Best Web Clone Skill</h1>
  <p>
    <b>A Cursor skill package that clones any website URL into a single-file HTML replica via Gemini,<br>
    with built-in bug fixing and prompt expansion workflows.</b>
  </p>

  <!-- Badges -->
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache 2.0-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker"></a>
  <br>
  <a href="#quick-start">Quick Start</a> •
  <a href="#skills">Skills</a> •
  <a href="#workflow">Workflow</a> •
  <a href="#license">License</a>
</div>

---

A portable, self-contained set of [Cursor](https://cursor.com) skills that turns a source URL into a single-file HTML replica. Designed to work on a fresh machine — automatically bootstraps its runtime, falls back when `venv` is missing, and also supports Docker for fully isolated execution.

## Table of Contents

- [Features](#features)
- [Skills](#skills)
- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Docker](#docker)
- [Workflow](#workflow)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- **URL to HTML replica** — give it a URL and get back a self-contained HTML file
- **Automated runtime bootstrap** — creates `.runtime/venv` or falls back to `.runtime/site-packages`
- **Browser capture** — full-page scrolling snapshot, stylesheet extraction, optional video
- **Smart prompt expansion** — short style hints become detailed design briefs
- **Bugfix workflow** — diagnose and patch visual fidelity issues after cloning
- **Two runtime paths** — host Python or Docker, same output contract
- **Single-file output** — everything in one HTML file, with compatibility aliases

## Skills

| Skill | File | Purpose |
|-------|------|---------|
| **Clone** | [`cloneit-web-cloning/CLONE_SKILL.md`](cloneit-web-cloning/CLONE_SKILL.md) | Clone a URL into a single-file HTML replica via Gemini |
| **Bugfix** | [`cloneit-web-bugfix/BUGFIX_SKILL.md`](cloneit-web-bugfix/BUGFIX_SKILL.md) | Diagnose and repair visual bugs in cloned websites |
| **Expander** | [`.cursor/skills/prompt-expander/EXPANDER_SKILL.md`](.cursor/skills/prompt-expander/EXPANDER_SKILL.md) | Expand short user prompts into structured design briefs |

## Quick Start

```bash
# Clone a website (from the repository root)
python3 cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"

# Clone with a design hint
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it darker and cleaner"

# Review the expanded prompt before generating
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it darker and cleaner" \
  --confirm-expanded-prompt
```

> The runner auto-creates and manages the runtime — no need to run `pip install` or activate a virtual environment manually.

## Prerequisites

**Host path:**

- Python 3.11+ with `pip`
- `venv` support is preferred but not required — the runner falls back to `.runtime/site-packages` automatically
- `GOOGLE_GEMINI_API_KEY` set in the environment or a `.env` file
- Network access to PyPI, Playwright download endpoints, and the Gemini API

**Docker path:**

- Docker with permission to build and run containers

## Docker

```bash
# Build
docker build -t clone-skill cloneit-web-cloning

# Run
docker run --rm -it --ipc=host \
  -e GOOGLE_GEMINI_API_KEY="$GOOGLE_GEMINI_API_KEY" \
  -v "$(pwd)/outputs:/outputs" \
  clone-skill \
  "https://example.com" \
  --out-dir /outputs/replica_demo
```

The Docker path avoids host-Python `venv` differences entirely. It is the most isolated way to run the workflow.

## Workflow

The clone skill runs through three named stages:

```
capture-matrix  →  replica-forge  →  artifact-sync
```

| Stage | What happens |
|-------|-------------|
| **capture-matrix** | Browser launches, navigates to the source URL, performs scrolling snapshots, collects stylesheets, and optionally records a video |
| **replica-forge** | Captured context plus the user's instructions (auto-expanded if needed) are sent to Gemini, which generates a single-file HTML replica |
| **artifact-sync** | Canonical outputs and compatibility aliases are written to the output directory |

If a cloned page has visual issues, the bugfix skill offers a separate repair loop:

```
reproduce → classify → patch → validate → report
```

The expander skill, when invoked separately or triggered by a short input, follows:

```
classify → pull reference → extract constraints → build prompt → confirm
```

## Project Structure

```
best-web-clone-skill/
├── README.md                          # This file
├── LICENSE                            # Apache 2.0
├── .gitignore
├── cloneit-web-cloning/               # Main cloning skill package
│   ├── CLONE_SKILL.md                 # Agent-facing skill definition
│   ├── README.md                      # Package-level documentation
│   ├── runtime.md                     # Managed runtime behavior
│   ├── docker.md                      # Docker usage guide
│   ├── prompt-expansion.md            # Instruction expansion behavior
│   ├── artifacts.md                   # Stage names and output contracts
│   ├── troubleshooting.md             # Common failure remediation
│   ├── scripts/
│   │   └── clone_with_gemini.py       # Workflow entrypoint
│   ├── assets/
│   │   ├── cloneit.skill.toml
│   │   ├── requirements.txt
│   │   └── prompts/
│   ├── references/
│   ├── Dockerfile
│   └── .dockerignore
├── cloneit-web-bugfix/                # Bugfix skill package
│   ├── BUGFIX_SKILL.md
│   └── references/
│       └── bugfix-playbook.md
└── .cursor/
    └── skills/
        └── prompt-expander/           # Prompt expander skill package
            ├── EXPANDER_SKILL.md
            └── reference-library.md
```

## Community

- [Contributing Guidelines](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## License

Distributed under the [Apache 2.0 License](LICENSE).
