---
name: skill
description: Runs a self-contained website-cloning workflow that turns a source URL into a single-file HTML replica using Gemini, with optional instruction expansion, automatic runtime bootstrap, fallback when host Python lacks venv support, and a Docker path for clean first-run execution. Use whenever the user wants to clone, mirror, recreate, copy, or restyle an existing website from a URL.
license: Apache-2.0
---

# Skill

This skill runs a portable URL-to-replica pipeline without depending on external repository engine files.

## When To Use

Use this skill whenever the user wants to:

- clone a website from a URL
- recreate or mirror an existing webpage
- restyle a source site while keeping its structure
- generate a single-file HTML replica from a live page

## Core Workflow

Follow this sequence:

1. Confirm the source URL and optional user instructions.
2. Verify that `GOOGLE_GEMINI_API_KEY` is available.
3. Choose the runtime path:
   - host Python, or
   - Docker
4. Bootstrap the managed runtime.
5. Run `capture-matrix` to capture the source page.
6. Expand short instructions only when needed.
7. Run `replica-forge` to generate the single-file HTML output.
8. Run `artifact-sync` to write canonical outputs and aliases.
9. Report output paths or the exact failure stage.

## Communicating With The User

Prefer practical language over abstract workflow descriptions.

- Treat short style hints as valid input.
- Explain whether the host-Python path or Docker path is more appropriate.
- Do not ask the user to manually activate `.runtime/venv`.
- If something fails, identify the exact stage and the next corrective action.

If the user is unsure what to provide, collect:

1. the source URL
2. optional design instructions
3. the desired output directory, if any
4. confirmation that the API key is available

## Quick Start

From the repository root:

```bash
python3 cloneit-web-cloning/scripts/clone_with_gemini.py "https://example.com"
```

From inside the skill folder:

```bash
python3 scripts/clone_with_gemini.py "https://example.com"
```

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

## Output Contract

Primary outputs:

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

If execution fails, always report:

1. the failing stage: `bootstrap`, `capture-matrix`, `replica-forge`, or `artifact-sync`
2. the exact command output or error text
3. the likely remediation path

## Additional Resources

- For runtime behavior and fallback rules, see [runtime.md](runtime.md)
- For container usage, see [docker.md](docker.md)
- For instruction expansion behavior, see [prompt-expansion.md](prompt-expansion.md)
- For stage names and artifact details, see [artifacts.md](artifacts.md)
- For failure remediation, see [troubleshooting.md](troubleshooting.md)
- For extra prompt notes, see [references/prompting-playbook.md](references/prompting-playbook.md)
- For prompt-expander details, see [references/prompt-expander-reference.md](references/prompt-expander-reference.md)

## Examples

**Example 1:**

Input: "Clone `https://example.com` and keep it visually close to the source."

Expected behavior:

- run the standard workflow
- keep user instructions minimal
- return canonical artifact paths

**Example 2:**

Input: "Clone `https://example.com`, make it darker, simplify the layout, and let me review the expanded prompt first."

Expected behavior:

- prepare and save `expanded_user_prompt.txt`
- pause for review because confirmation was requested
- continue generation only after approval
