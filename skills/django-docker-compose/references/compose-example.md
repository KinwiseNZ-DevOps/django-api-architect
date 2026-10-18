# Compose example for a Django API

Contents: compose.yaml, hot reload options, .env.example, command cheat sheet

Adapt service names, the settings module, the Celery app path (`config`) and ports to the project. This file is for local development.

## compose.yaml

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-app}
      POSTGRES_USER: ${POSTGRES_USER:-app}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h 127.0.0.1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 20s

  redis:
    image: redis:7
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  migrate:
    build:
      context: .
      target: dev
    command: ["python", "manage.py", "migrate"]
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    restart: "no"

  web:
    build:
      context: .
      target: dev
    command: ["python", "manage.py", "runserver", "0.0.0.0:8000"]
    env_file: .env
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully

  worker:
    build:
      context: .
      target: dev
    command: ["celery", "-A", "config", "worker", "--loglevel=info"]
    env_file: .env
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully

  beat:
    build:
      context: .
      target: dev
    command: ["celery", "-A", "config", "beat", "--loglevel=info", "--scheduler", "django_celery_beat.schedulers:DatabaseScheduler"]
    env_file: .env
    volumes:
      - .:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully

volumes:
  pgdata:
```

Notes:

- The Postgres readiness check uses TCP (`-h 127.0.0.1`). The official image runs a temporary server during first-time initialisation, and a check over the default socket may report ready too early (inference from the image's init behaviour; verify against the image version in use).
- `${POSTGRES_PASSWORD:?message}` stops `docker compose` with that message when the value is missing or empty.
- With a bind mount (`.:/app`) the `runserver` autoreloader picks up edits. Django notes that adding files may not trigger a restart, so restart the service then.
- The Celery `beat` command assumes the `django_celery_beat` package, which matches the `DatabaseScheduler` convention in the django-celery skill. Remove the scheduler flag if the project uses another.
- Restart the worker after code changes; Celery workers do not autoreload by default.
- `web`, `worker` and `beat` share one image. Giving them the same `build` block keeps a single build.

## Hot reload options

- **Bind mount** (shown above): simplest. File I/O can be slow on macOS and Windows, and platform-specific compiled files can leak between host and container.
- **Compose watch** (`develop.watch`): finer control. Use `sync` to copy changed files, `rebuild` when dependency files change, and `sync+restart` for config changes. It works only for services built from local source, does not support glob patterns, and needs `stat`, `mkdir` and `rmdir` in the image. Start it with `docker compose up --watch` or `docker compose watch`.

```yaml
    develop:
      watch:
        - action: sync
          path: .
          target: /app
          ignore:
            - .venv/
            - __pycache__/
        - action: rebuild
          path: requirements/
```

## .env.example

```
# Copy to .env and fill in. .env is never committed.
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=change-me
DJANGO_SETTINGS_MODULE=config.settings.local
SECRET_KEY=change-me
DATABASE_URL=postgres://app:change-me@db:5432/app
CELERY_BROKER_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

Use the variable names the project's settings partials read. The hosts in the URLs are service names (`db`, `redis`), not `localhost`.

## Command cheat sheet

```bash
docker compose config                      # validate and render the file
docker compose up -d --build               # start the stack in the background
docker compose ps                          # check health
docker compose logs -f web worker          # follow logs
docker compose exec web python manage.py shell
docker compose run --rm web pytest         # run the test suite in a fresh container
docker compose run --rm web python manage.py makemigrations
docker compose down                        # stop, keep volumes
docker compose down -v                     # stop AND delete volumes (local database is lost)
```

Confirm with the user before `down -v`.

## Sources

Official, fetched 2026-10-18:

- Compose startup order: https://docs.docker.com/compose/how-tos/startup-order/ (`depends_on` conditions, readiness warning).
- Compose services reference: https://docs.docker.com/reference/compose-file/services/ (healthcheck, `env_file`, ports, volumes, `command`, `init`, restart, profiles, `stop_grace_period`).
- Compose variable interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/ (`:-`, `:?` forms).
- Compose environment best practices: https://docs.docker.com/compose/how-tos/environment-variables/best-practices/
- Compose secrets: https://docs.docker.com/compose/how-tos/use-secrets/ (files at `/run/secrets`, `_FILE` convention).
- Compose watch: https://docs.docker.com/compose/how-tos/file-watch/
- Postgres image: https://hub.docker.com/_/postgres (required password, volume path by major version, init scripts only on empty data directory, `_FILE` variants, avoid trust authentication).
- Django `runserver`: https://docs.djangoproject.com/en/stable/ref/django-admin/ (not for production, autoreload limits, binding to 0.0.0.0).

Inference, not confirmed from a fetched page: pinning the Redis and Postgres tags to a major version is advice, and the Redis health check form is conventional. Check both against the image versions you use.
