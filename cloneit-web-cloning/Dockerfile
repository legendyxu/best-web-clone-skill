FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3.12-venv \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

ENTRYPOINT ["python3", "/app/scripts/clone_with_gemini.py"]
CMD ["--help"]
