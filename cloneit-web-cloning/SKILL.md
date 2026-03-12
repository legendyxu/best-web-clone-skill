---
name: web-replica-forge
description: Self-contained workflow to clone an existing website URL into a single-file HTML replica using Gemini. Supports optional user instructions (short/vague OK) via built-in prompt-expander. Use when users ask to clone/copy/recreate/mirror a website.
license: Apache-2.0
---

# Web Replica Forge

Run a self-contained URL-to-replica pipeline with no dependency on external repository engine files.

## Input

- **URL** (required): Target webpage to clone
- **Instructions** (optional): User preferences. If the brief is short or vague (e.g., "做成暗色主题", "简洁一点", "突出移动端"), the built-in prompt-expander will auto-expand it into a structured design brief. If the brief is already detailed, the skill will use it directly instead of expanding it again.

## Stage System (Custom Naming)

- `capture-matrix`: browser capture, scrolling snapshot, stylesheet harvest, optional scroll video
- `replica-forge`: Gemini generation of a single-file HTML replica (with optional expanded user instructions)
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

Clone with short/vague user instructions (prompt-expander will auto-expand them):

```bash
python cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "做成暗色主题，简洁一点"
```

Review the expanded prompt before clone generation:

```bash
python cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "做成暗色主题，简洁一点" \
  --confirm-expanded-prompt
```

If you already reviewed `expanded_user_prompt.txt`, continue in non-interactive mode with:

```bash
python cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "做成暗色主题，简洁一点" \
  --confirm-expanded-prompt \
  --approve-expanded-prompt
```

## Bundled Prompts (Secret Sauce)

Prompt files are embedded in this skill:
- `assets/prompts/clone.system_prompt.txt`
- `assets/prompts/clone.pass1.prompt_template.txt`

The runner loads these from `assets/cloneit.skill.toml` by default, so prompt behavior is portable.

## Prompt Expander (Built-in)

When `--instructions` is provided, the skill:
1. Infers website type from the source URL and user brief
2. Automatically decides whether the brief needs expansion
3. If the brief is short/vague, expands it into a structured prompt with:
   - visual style
   - page sections
   - content details
   - interactions
   - audience and tone
4. If the brief is already detailed, keeps the user's original brief and uses it directly
5. Saves the prepared prompt as `expanded_user_prompt.txt`
6. Optionally pauses for explicit user confirmation when `--confirm-expanded-prompt` is used and auto-expansion actually happened
7. Injects the prepared prompt into the final clone prompt used by Gemini

This allows non-expert users to give short hints like "暗色" or "简洁" and still get a professional design direction, while not over-processing already detailed prompts.

## Artifact Contract

Primary artifacts:
- `run_manifest.txt`
- `source_snapshot.png`
- `source_styles.css`
- `source_scroll.webm` (when enabled)
- `web_replica.html`
- `expanded_user_prompt.txt` (when `--instructions` is provided; contains either the auto-expanded brief or the user's direct brief with a direct-use decision)

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
