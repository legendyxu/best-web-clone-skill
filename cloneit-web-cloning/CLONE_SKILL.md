---
name: clone-skill
description: Runs a self-contained website-cloning workflow that turns a source URL into a single-file HTML replica using Gemini, with optional instruction expansion and automatic runtime management. Use whenever the user wants to clone, mirror, recreate, copy, or restyle an existing website from a URL. Make sure to use this skill whenever the user mentions cloning, replicating, copying, mirroring, or rebuilding a website, even if they don't explicitly say "clone" — for example "I want to remake this page", "turn this URL into a standalone file", or "make a simpler version of this site."
license: Apache-2.0
---

# Clone Skill — Website Cloning

This skill runs a portable URL-to-replica pipeline without depending on external repository engine files.

At a high level, the workflow goes like this:

- confirm the source URL and any optional user instructions
- choose the runtime path: host Python or Docker
- bootstrap the managed runtime
- capture the source page with a browser
- expand short instructions only when needed
- generate a single-file HTML replica with Gemini
- write canonical artifacts and compatibility aliases
- report output paths or the exact failure stage and remediation

## Communicating With the User

This skill may be used by people with very different levels of technical familiarity. Prefer concrete, practical language.

- Treat short style hints like "make it darker" as valid input — the built-in prompt expander handles them.
- Explain whether the host-Python path or Docker path is more appropriate for their environment.
- **Never** ask the user to manually activate `.runtime/venv`. The runner handles that automatically.
- If execution fails, identify the exact stage that failed and the next corrective action, not just a generic error message.

If the user is unsure what to provide, help them supply:

1. the source URL
2. optional design instructions (or confirm they want a faithful copy)
3. the desired output directory, if any
4. confirmation that `GOOGLE_GEMINI_API_KEY` is available

## Prerequisites

The user needs one of:

- **Host path**: Python 3.11+ with `pip`. `venv` support is preferred but not required — the runner falls back to `.runtime/site-packages` if `python3-venv` is missing.
- **Docker path**: Docker with permission to build and run containers.

In either case they also need:

- `GOOGLE_GEMINI_API_KEY` through the environment or a local `.env` file
- outbound network access to PyPI, Playwright browser download endpoints, and the Gemini API
- an OS environment capable of launching Chromium

Optional browser override: `WEB_REPLICA_BROWSER_EXECUTABLE` to point to a specific Chrome or Chromium binary.

## Quick Start

```bash
# From the repository root
python3 cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"

# From inside the skill folder
python3 scripts/clone_with_gemini.py "https://example.com"
```

## Core Workflow

### Step 1: Confirm The Request

Capture:

1. source URL
2. optional design instructions
3. optional output directory
4. whether the user wants host Python or Docker

### Step 2: Verify The API Key

Ensure `GOOGLE_GEMINI_API_KEY` is available before proceeding. The runner reads it from the environment or `.env`.

### Step 3: Bootstrap The Runtime

On the host path, let the runner decide whether to use `.runtime/venv` or `.runtime/site-packages`. **Do not fail early** just because `venv` support is missing — the fallback exists for this case.

### Step 4: Capture The Source Page

The `capture-matrix` stage should:

- launch a usable browser
- navigate to the target URL
- perform the required scrolling
- save a source snapshot and collect stylesheet information
- optionally capture a scroll video

### Step 5: Prepare User Instructions

When `--instructions` is present:

1. infer the likely website type from the URL and user brief
2. decide whether the instructions need expansion
3. expand short or vague instructions into a structured design brief
4. keep already detailed instructions as-is
5. save the prepared prompt to `expanded_user_prompt.txt`
6. pause for review only when `--confirm-expanded-prompt` is used and auto-expansion actually occurred

### Step 6: Generate The Replica

The `replica-forge` stage should:

- combine the captured source context with the prepared user prompt
- call Gemini to generate a single-file HTML replica
- preserve the intended layout and styling direction as closely as practical

### Step 7: Write Artifacts

The `artifact-sync` stage should:

- write canonical outputs (manifest, snapshot, styles, replica HTML)
- write compatibility aliases
- report final file paths clearly

### Step 8: Report Results

On success, report the main output files. On failure, report:

1. the failing stage (`bootstrap`, `capture-matrix`, `replica-forge`, or `artifact-sync`)
2. the exact command output or error text
3. the most likely remediation path

## Common Commands

```bash
# Bootstrap/verify only
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only

# Verify runtime only
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --verify-runtime

# Force a clean runtime rebuild
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only --force-rebuild-runtime

# Clone to an explicit output directory
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --out-dir outputs/replica_demo

# Clone with short/vague instructions (auto-expanded)
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it dark and cleaner"

# Review the expanded prompt before generation
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it dark and cleaner" \
  --confirm-expanded-prompt
```

## Output Contract

Primary outputs:

- `run_manifest.txt`
- `source_snapshot.png`
- `source_styles.css`
- `source_scroll.webm` (when enabled)
- `web_replica.html`
- `expanded_user_prompt.txt` (when `--instructions` is provided)

Compatibility aliases:

- `output_manifest.txt`
- `page_stitched.png`
- `page_html_styles.css`
- `cloned_site.html`

## Failure Handling

If execution fails, always return:

1. the failing stage: one of `bootstrap`, `capture-matrix`, `replica-forge`, or `artifact-sync`
2. the exact command output or error text
3. the likely remediation path

Common failure patterns and their fixes:

- **Missing API key**: Set `GOOGLE_GEMINI_API_KEY` or provide it through `.env`.
- **Dependency bootstrap failure**: Verify Python 3.11+ and `pip`, then retry with `--force-rebuild-runtime`. Use the Docker path as a fallback.
- **Browser install or launch failure**: Let the workflow install Playwright Chromium automatically, or set `WEB_REPLICA_BROWSER_EXECUTABLE` to an existing binary.
- **Network problems**: Verify access to PyPI, Playwright download endpoints, the Gemini API, and the source URL.

## Examples

**Example 1: Faithful clone**

Input: "Clone `https://example.com` and keep it visually close to the source."

Expected behavior:

- run the standard workflow with minimal user instructions
- return canonical artifact paths and confirmation

**Example 2: Clone with style direction**

Input: "Clone `https://example.com`, make it darker, simplify the layout, and let me review the expanded prompt first."

Expected behavior:

- prepare and save `expanded_user_prompt.txt`
- pause for review because confirmation was requested
- continue generation only after approval

**Example 3: Docker-based run**

User: "I don't have Python set up, but I have Docker. Can I still clone a site?"

Expected behavior:

- point the user to the Docker path
- run `docker build -t clone-skill cloneit-web-cloning` and `docker run` as documented
- return the same artifact paths

## Additional Resources

- For runtime behavior and fallback rules, see [runtime.md](runtime.md)
- For Docker usage, see [docker.md](docker.md)
- For instruction expansion behavior, see [prompt-expansion.md](prompt-expansion.md)
- For stage names and artifact details, see [artifacts.md](artifacts.md)
- For failure remediation, see [troubleshooting.md](troubleshooting.md)
- For prompt-level quality guidance, see [references/prompting-playbook.md](references/prompting-playbook.md)
- For prompt-expander reference tables, see [references/prompt-expander-reference.md](references/prompt-expander-reference.md)
