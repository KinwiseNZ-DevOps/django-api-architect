# Dockerfile example for a Django API

Adapt names and paths to the project. The layout assumes `requirements/base.txt` and `requirements/dev.txt`, a settings package at `config/`, and a WSGI entry point at `config.wsgi:application`. Projects that use another dependency tool (uv, poetry, pip-tools) keep the same stage structure and change only the install lines.

## Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

# Production dependencies in a virtual environment, built with compilers
# that never reach the final image.
FROM base AS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements/base.txt requirements/base.txt
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install -r requirements/base.txt

# Development dependencies on top of the production ones.
FROM deps AS deps-dev
COPY requirements/dev.txt requirements/dev.txt
RUN /opt/venv/bin/pip install -r requirements/dev.txt

# Development target: source is bind-mounted or synced by Compose.
FROM base AS dev
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=deps-dev /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
USER app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Runtime target: last stage, so it is the default build target.
FROM base AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=deps /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY --chown=app:app . .
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/', timeout=3)"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

Notes on the choices:

- The final stage is `runtime`. Build the development image with `docker build --target dev .`. BuildKit builds only the stages the chosen target depends on.
- `useradd` runs in `base`, so every stage that uses `USER app` shares the same fixed UID and GID.
- The health check uses Python from the image, so it needs no `curl`. It needs a lightweight `/health/` route and `127.0.0.1` in `ALLOWED_HOSTS`. If the project has no health route, adding one is an API-layer change: a thin view that returns 200 and holds no business logic.
- `libpq5` is the PostgreSQL client library the runtime needs. `libpq-dev` and `build-essential` are only needed to compile packages in the `deps` stage.
- Static files: if `collectstatic` runs at build time, add it as a `RUN` that sets its required environment variables inline on that one line, never with `ENV`. Alternatively run it as a deploy step.

## .dockerignore

```
.git
.gitignore
.env
.env.*
!.env.example
.venv
venv
__pycache__
*.pyc
.pytest_cache
.mypy_cache
.ruff_cache
media
staticfiles
*.sqlite3
docker-compose*.yml
Dockerfile
```

Reason: a smaller build context is faster to send and cannot leak local env files or history into the image.

## Verification commands

```bash
docker build --target dev -t myapp:dev .
docker build -t myapp:latest .
docker run --rm myapp:latest id
docker run --rm --env-file .env.production myapp:latest python manage.py check --deploy
docker history --no-trunc myapp:latest
```

The `id` command should show UID 10001, not root. `check --deploy` should run against the production settings; point it at them with `DJANGO_SETTINGS_MODULE` or `--settings`. In `docker history`, search for any secret value.

## Sources

Official, fetched 2026-10-18:

- Docker build best practices: https://docs.docker.com/build/building/best-practices/ (multi-stage, pinning, layer order, apt, USER, exec form, ENV).
- Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/ (named stages, `--target`).
- Docker build secrets: https://docs.docker.com/build/building/secrets/ (why `ARG` and `ENV` leak).
- Dockerfile reference: https://docs.docker.com/reference/dockerfile/ (HEALTHCHECK defaults: interval 30s, timeout 30s, start period 0s, retries 3; exit 0 healthy, 1 unhealthy).
- Django `runserver` and `check --deploy`: https://docs.djangoproject.com/en/stable/ref/django-admin/
- Django deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Python environment variables: https://docs.python.org/3/using/cmdline.html
- Gunicorn design: https://gunicorn.org/design/ (worker types, worker count, buffering proxy).

Inference, not stated by a fetched page: the Gunicorn `/dev/shm` worker temp directory advice for containers is widely repeated but was not confirmed from the Gunicorn docs in this pass; consider `--worker-tmp-dir /dev/shm` only if workers stall in a container, and verify.
