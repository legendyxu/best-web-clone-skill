# Artifacts

## Stage Names

The workflow uses these stage names:

- `capture-matrix`
- `replica-forge`
- `artifact-sync`

Use these names in status updates, logs, and failure reports.

## Primary Outputs

Canonical output files:

- `run_manifest.txt`
- `source_snapshot.png`
- `source_styles.css`
- `source_scroll.webm` when enabled
- `web_replica.html`
- `expanded_user_prompt.txt` when instructions are provided

## Compatibility Aliases

Alias files are also written for compatibility with older expectations:

- `output_manifest.txt`
- `page_stitched.png`
- `page_html_styles.css`
- `cloned_site.html`

## Reporting Guidance

On success, report the main output path and any other relevant generated files. On failure, report the exact stage that failed before listing remediation steps.
