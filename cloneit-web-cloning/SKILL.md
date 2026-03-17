---
name: skill
description: Runs a self-contained website-cloning workflow that turns a source URL into a single-file HTML replica using Gemini, with optional instruction expansion, automatic runtime bootstrap, fallback when host Python lacks venv support, and a Docker path for clean first-run execution. Use whenever the user wants to clone, mirror, recreate, copy, or restyle an existing website from a URL.
license: Apache-2.0
---

# Skill

This skill runs a portable URL-to-replica pipeline without depending on external repository engine files.

At a high level, the workflow goes like this:

- confirm the source URL and optional user instructions
- bootstrap an isolated runtime or use the Docker path
- capture the source page with a browser
- prepare the final prompt, expanding short instructions only when needed
- generate a single-file HTML replica with Gemini
- write canonical artifacts and compatibility aliases
- report success, output paths, or exact failure details

## Communicating With the User

This skill may be used by people with very different levels of technical familiarity. Prefer concrete, practical language.

- Explain whether the user should use the host-Python path or the Docker path.
- Treat short style hints as valid input instead of demanding a long design brief.
- If execution fails, identify the failing stage, the likely cause, and the next action.
- Do not ask the user to manually activate `.runtime/venv` as part of the normal flow.

If the user is unsure what to provide, help them supply:

1. the source URL
2. optional design instructions
3. the desired output directory, if any
4. confirmation that `GOOGLE_GEMINI_API_KEY` is available

## Input Contract

The workflow expects:

- **URL**: required, the webpage to clone
- **Instructions**: optional, for design direction or content emphasis
- **Output directory**: optional, defaults to the standard output path if omitted
- **API key**: required through `GOOGLE_GEMINI_API_KEY`

Short instructions are acceptable. For example:

- `make it darker and cleaner`
- `emphasize mobile readability`
- `turn this into an anime-style landing page`

If the instructions are already detailed, use them directly. If they are short or vague, expand them into a structured brief first.

## Stage System

This skill intentionally uses the following stage names:

- `capture-matrix`: browser capture, scrolling snapshot, stylesheet harvest, optional scroll video
- `replica-forge`: Gemini generation of a single-file HTML replica
- `artifact-sync`: canonical artifact writing plus compatibility aliases

When reporting status or failures, always refer to these stage names rather than older pass naming.

## Runtime Strategy

The runner is designed to be plug-and-play on a fresh machine.

### Host Python Path

The host-Python path automatically handles:

- local virtual environment creation in `.runtime/venv` when `venv` can be bootstrapped
- fallback package installation in `.runtime/site-packages` when `python3-venv` or `ensurepip` is missing
- dependency installation from `assets/requirements.txt`
- reuse of an existing Chrome, Chromium, or Playwright browser when available
- Playwright Chromium installation in `.runtime/pw-browsers` when no usable browser is present
- import checks for `google.genai` and `playwright`
- browser launch verification
- automatic runtime rebuild when a copied runtime is stale or machine-specific

### Docker Path

The Docker path is the clean-room option for users who want a fully isolated first run.

- it avoids host-Python `venv` differences
- it uses the repository `Dockerfile`
- it still writes clone outputs to a mounted directory on the host

## Prerequisites

Choose one runtime path:

- Host path: Python 3.11+ with `pip`
- Docker path: Docker with permission to build and run containers

Additional requirements:

- `venv` support is preferred but not required on the host path
- outbound network access to PyPI, Playwright browser download endpoints, and the Gemini API
- an OS environment capable of launching Chromium
- write permission in the skill directory and the chosen output directory

Required input:

- `GOOGLE_GEMINI_API_KEY` through the environment or a local `.env` file

Optional browser override:

- `WEB_REPLICA_BROWSER_EXECUTABLE` to point to a specific Chrome or Chromium binary

## Quick Start

Examples below use `python3`. If the machine exposes the launcher as `python`, substitute that command instead.

From the repository root:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"
```

If this skill is unpacked elsewhere, run from the skill root:

```bash
python3 scripts/clone_with_gemini.py "https://example.com"
```

Normal users should not manually run:

```bash
source .runtime/venv/bin/activate
```

The runner is responsible for creating, verifying, and repairing `.runtime` automatically.

## Docker Quick Start

From the repository root:

```bash
docker build -t skill cloneit-web-cloning
docker run --rm -it --ipc=host \
  -e GOOGLE_GEMINI_API_KEY="$GOOGLE_GEMINI_API_KEY" \
  -v "$(pwd)/outputs:/outputs" \
  skill \
  "https://example.com" \
  --out-dir /outputs/replica_demo
```

Use this path when the host Python setup is unreliable or when the user wants the most isolated new-user test.

## Workflow

Run the cloning process in this order.

### Step 1: Confirm The Request

Capture:

1. source URL
2. optional instructions
3. optional output directory
4. whether the user wants host Python or Docker

### Step 2: Bootstrap The Runtime

On the host path, let the runner decide whether to use:

- `.runtime/venv`, or
- `.runtime/site-packages`

Do not fail early just because `venv` support is missing. The fallback path exists specifically for this case.

### Step 3: Capture The Source Page

The `capture-matrix` stage should:

- launch a usable browser
- navigate to the target URL
- perform the required scrolling
- save a source snapshot
- collect stylesheet information
- optionally capture a scroll video

### Step 4: Prepare User Instructions

When `--instructions` is present:

1. infer the likely website type from the URL and user brief
2. decide whether the instructions need expansion
3. expand short or vague instructions into a more structured design brief
4. keep already detailed instructions as-is
5. save the prepared prompt to `expanded_user_prompt.txt`
6. pause for review only when `--confirm-expanded-prompt` is requested and auto-expansion actually occurred

### Step 5: Generate The Replica

The `replica-forge` stage should:

- combine the captured source context with the prepared user prompt
- call Gemini to generate a single-file HTML replica
- preserve the intended layout and styling direction as closely as practical

### Step 6: Write Artifacts

The `artifact-sync` stage should:

- write canonical outputs
- write compatibility aliases
- report final file paths clearly

### Step 7: Report Results

On success, report the main output files. On failure, report:

1. the failing stage
2. the exact command output or error text
3. the most likely remediation path

## Common Commands

Bootstrap only:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only
```

Verify runtime only:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --verify-runtime
```

Force a clean runtime rebuild:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py --bootstrap-only --force-rebuild-runtime
```

Clone to an explicit output directory:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --out-dir outputs/replica_demo
```

Skip video capture:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --no-include-video
```

Clone with short instructions:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it dark and cleaner"
```

Review the expanded prompt before generation:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it dark and cleaner" \
  --confirm-expanded-prompt
```

Approve the already reviewed expanded prompt in non-interactive mode:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py \
  "https://example.com" \
  --instructions "make it dark and cleaner" \
  --confirm-expanded-prompt \
  --approve-expanded-prompt
```

## Prompt Expansion

The prompt-expander is built into this skill.

When expansion is needed, the prepared prompt should cover:

- visual style
- page sections
- content details
- interaction ideas
- audience and tone

This lets non-expert users provide short hints while still producing a stronger design brief for the final generation step.

## Bundled Resources

Prompt configuration and templates are bundled with this skill:

- `assets/cloneit.skill.toml`
- `assets/prompts/clone.system_prompt.txt`
- `assets/prompts/clone.pass1.prompt_template.txt`

The runner resolves these relative to the skill directory so the workflow remains portable.

## Environment Assumptions

- existing virtual environments are tolerated, but this skill prefers its own managed runtime
- copied or stale managed runtimes may be rebuilt automatically
- `.runtime/` is machine-local state and should be generated on the target machine rather than committed
- no external repository engine layout is required
- no pre-created output directory is required

## Artifact Contract

Primary artifacts:

- `run_manifest.txt`
- `source_snapshot.png`
- `source_styles.css`
- `source_scroll.webm` when enabled
- `web_replica.html`
- `expanded_user_prompt.txt` when `--instructions` is provided

Compatibility aliases:

- `output_manifest.txt`
- `page_stitched.png`
- `page_html_styles.css`
- `cloned_site.html`

## Failure Handling

If execution fails, always return:

1. the failing stage: `bootstrap`, `capture-matrix`, `replica-forge`, or `artifact-sync`
2. the exact command output or error text
3. the most likely remediation steps

Typical remediation categories include:

- missing API key
- dependency bootstrap failure
- browser install or launch failure
- blocked network access
- source site behavior that prevents reliable capture

## Examples

**Example 1:**

Input: "Clone `https://example.com` and keep it visually close to the source."

Expected behavior:

- run the standard workflow
- keep user instructions minimal because fidelity is the primary goal
- return canonical artifact paths

**Example 2:**

Input: "Clone `https://example.com`, make it darker, simplify the layout, and let me review the expanded prompt first."

Expected behavior:

- prepare and save `expanded_user_prompt.txt`
- pause for explicit review because confirmation was requested
- continue generation only after approval

## Summary Checklist

Before considering the run complete, verify:

- [ ] the source URL is correct
- [ ] `GOOGLE_GEMINI_API_KEY` is available
- [ ] the runtime path is clear: host Python or Docker
- [ ] output files were written successfully
- [ ] prompt expansion behavior matched the user's request
- [ ] failures, if any, were reported with exact stage and remediation
