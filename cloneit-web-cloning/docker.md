# Docker

## When To Use Docker

Use the Docker path when:

- the host Python setup is unreliable
- the user wants a clean-room test
- the machine is missing `venv` support
- you want a reproducible first-run environment

## Build

From the repository root:

```bash
docker build -t skill cloneit-web-cloning
```

From inside `cloneit-web-cloning/`:

```bash
docker build -t skill .
```

## Run

From the repository root:

```bash
docker run --rm -it --ipc=host \
  -e GOOGLE_GEMINI_API_KEY="$GOOGLE_GEMINI_API_KEY" \
  -v "$(pwd)/outputs:/outputs" \
  skill \
  "https://example.com" \
  --out-dir /outputs/replica_demo
```

## Output Mounting

The container writes clone outputs to the mounted host directory:

- host path: `$(pwd)/outputs`
- container path: `/outputs`

## Why This Path Exists

The Docker image avoids host-specific Python packaging differences and provides a more predictable first-run experience for users who just want the workflow to work.
