---
name: web-replica-forge
description: Self-contained workflow to clone an existing website URL into a single-file HTML replica using Gemini, including runtime bootstrap, dependency installation, package verification, browser verification, capture, and artifact generation. Use when users ask to clone/copy/recreate/mirror a website and need plug-and-play execution without external engine code.
license: Apache-2.0
---

# Web Replica Forge

Run a self-contained URL-to-replica pipeline with no dependency on external repository engine files.

## Stage System (Custom Naming)

- `capture-matrix`: browser capture, scrolling snapshot, stylesheet harvest, optional scroll video
- `replica-forge`: Gemini generation of a single-file HTML replica
- `artifact-sync`: canonical artifact writing + compatibility aliases

This skill intentionally does not use old pass naming.

## Plug-and-Play Runtime

The runner auto-handles:
- local virtualenv creation in `.runtime/venv` (inside skill directory)
- Python dependency installation from `assets/requirements.txt`
- Playwright Chromium installation
- import checks for `google.genai` and `playwright`
- browser launch verification

## Quick Start

From any working directory (project copy):

```bash
python skills/skills/cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"
```

If this skill is unpacked elsewhere, run the script from that skill root:

```bash
python scripts/clone_with_gemini.py "https://example.com"
```

## Prerequisites

- Python 3.11+ with `venv` support
- Outbound network access to:
  - PyPI (for dependency bootstrap)
  - Playwright browser download endpoints
  - Gemini API
- OS environment capable of running Chromium (Playwright)
- Write permission in:
  - skill directory (for `.runtime/venv`)
  - chosen output directory

Required input:
- `GOOGLE_GEMINI_API_KEY` (env var or `.env` in current directory)

## Environment Assumptions

- Existing virtualenvs are tolerated; this skill always uses its own isolated runtime by default.
- No repository engine structure is required; prompt/config resolution is relative to this skill directory.
- No pre-created output folders are required.

## Common Commands

Bootstrap/verify only:

```bash
python skills/skills/cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only
```

Runtime verification only:

```bash
python skills/skills/cloneit-web-cloning/scripts/clone_with_gemini.py --verify-runtime
```

Clone with explicit output directory:

```bash
python skills/skills/cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --out-dir outputs/replica_demo
```

Skip video capture:

```bash
python skills/skills/cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --no-include-video
```

## Bundled Prompts (Secret Sauce)

Prompt files are embedded in this skill:
- `assets/prompts/clone.system_prompt.txt`
- `assets/prompts/clone.pass1.prompt_template.txt`

The runner loads these from `assets/cloneit.skill.toml` by default, so prompt behavior is portable.

## Artifact Contract

Primary artifacts:
- `run_manifest.txt`
- `source_snapshot.png`
- `source_styles.css`
- `source_scroll.webm` (when enabled)
- `web_replica.html`

Compatibility aliases are also written:
- `output_manifest.txt`
- `page_stitched.png`
- `page_html_styles.css`
- `cloned_site.html`

## Failure Handling

If execution fails, return:
1. failing stage (`bootstrap`, `capture-matrix`, `replica-forge`, or `artifact-sync`)
2. exact command output
3. remediation steps (missing key, package install failure, browser install failure, network/site blocking)
