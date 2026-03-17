# Troubleshooting

## Always Report The Failing Stage

If the workflow fails, report one of:

- `bootstrap`
- `capture-matrix`
- `replica-forge`
- `artifact-sync`

## Common Failure Categories

### Missing API Key

Symptoms:

- Gemini requests cannot start
- the workflow reports a missing key

Fix:

- set `GOOGLE_GEMINI_API_KEY`
- or provide it through a local `.env`

### Dependency Bootstrap Failure

Symptoms:

- Python packages fail to install
- import verification fails

Fix:

- verify Python 3.11+ and `pip`
- retry with `--force-rebuild-runtime`
- use the Docker path if the host setup is unreliable

### Browser Install Or Launch Failure

Symptoms:

- Chromium cannot be found or launched
- Playwright browser setup fails

Fix:

- let the workflow install Playwright Chromium
- or set `WEB_REPLICA_BROWSER_EXECUTABLE`
- verify the machine can run Chromium

### Network Problems

Symptoms:

- dependency downloads fail
- model calls fail
- the source page cannot be captured reliably

Fix:

- verify access to PyPI
- verify access to Playwright download endpoints
- verify access to the Gemini API
- verify the source site is reachable from the current environment

### Source Site Capture Problems

Symptoms:

- the source page partially loads
- capture output is incomplete
- scrolling or styling extraction is inconsistent

Fix:

- retry the run
- verify the site is not blocking automation
- switch to Docker for a cleaner environment if needed
