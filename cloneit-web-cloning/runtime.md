# Runtime

## Managed Runtime

The workflow is designed to run without requiring the user to manually create or activate a virtual environment.

On the host-Python path, the runner automatically handles:

- runtime bootstrap
- dependency installation from `assets/requirements.txt`
- browser discovery or Playwright browser installation
- import verification for required Python packages
- runtime rebuild when a copied runtime is stale or machine-specific

## Runtime Locations

The runner may use one of two managed runtime layouts:

- `.runtime/venv`
- `.runtime/site-packages`

## Fallback Behavior

If the host Python environment cannot bootstrap `venv`, the runner falls back to `.runtime/site-packages` instead of failing immediately.

This is intended to support fresh machines where `python3-venv` or `ensurepip` is unavailable.

## Browser Handling

The runner prefers an already available Chrome or Chromium installation when possible.

If no usable browser is found, it installs Playwright Chromium into:

- `.runtime/pw-browsers`

## Environment Variables

Required:

- `GOOGLE_GEMINI_API_KEY`

Optional:

- `WEB_REPLICA_BROWSER_EXECUTABLE`

## Notes

- `.runtime/` is machine-local state
- `.runtime/` should be generated on the target machine
- users should not manually activate `.runtime/venv` during normal execution
