# PlantCare backend — FastAPI + Python 3.12
FROM docker.io/library/python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (python-pptx image handling can use libmagic-free pure python;
# kept minimal on purpose)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# Generated PPT files directory (bind-mountable volume), owned by the app user
RUN useradd --create-home --uid 10001 plantcare \
    && mkdir -p /app/generated_files \
    && chown -R plantcare:plantcare /app

USER plantcare
WORKDIR /app

COPY --chown=plantcare:plantcare app ./app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
