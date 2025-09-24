# ========= Base (dependencies) =========
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app

# System deps (tiny + security)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

# ========= Dev image (hot reload) =========
FROM base AS dev
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
EXPOSE 8000
# hot-reload for local development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ========= Prod image (lean) =========
FROM base AS prod
# create non-root user
RUN addgroup --system app && adduser --system --ingroup app app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
USER app
EXPOSE 8000
# uvicorn workers; tune workers based on CPU (2*CPU+1 is typical)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
