---
name: django-docker-compose
description: >
  Governs the local Docker Compose stack for Django API projects: web, Postgres,
  Redis, Celery worker and beat services, health-gated startup, one-off
  migration, env files and secrets, volumes, ports, hot reload and running tests
  and management commands in containers. Use when writing or changing a
  docker-compose file, fixing a container that starts before Postgres is ready,
  putting passwords in compose files, or running docker compose down -v,
  including when asked for the quick option. Do not use for the Dockerfile
  itself (django-docker-images) or for production orchestration.
---

# Django Docker Compose

Stance: the Compose file defines a repeatable local environment, not production. Frozen: health-gated startup, secrets kept out of the file and out of Git, data in named volumes, and the database host being a service name. Flexible: which optional services run and how code reaches the container (bind mount or watch).

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| The project already has a Compose file that works | Follow it; change only what the task needs |
| No Compose file exists | Continue; write one from the example |
| The task is the Dockerfile or image | Use [django-docker-images](../django-docker-images/SKILL.md) |
| The task is Celery task code, retries or schedules | Use [django-celery](../django-celery/SKILL.md) |
| Asked to commit `.env` or put real passwords in the Compose file | Decline; ship `.env.example` and keep `.env` ignored |
| Asked to treat this Compose file as the production deployment | Decline; it targets local work, so say production needs its own setup |

Reason: a local file stretched into production carries dev servers, open ports and default passwords with it.

## Steps

1. **Detect.** Read any existing `compose.yaml` or `docker-compose.yml`, `.env.example`, the Dockerfile targets, the settings partials that read env vars, and how Celery is started. Match the project's service names and settings module.
2. **Write.** Define services from the example in [compose-example.md](references/compose-example.md): `db`, `redis`, a one-off `migrate`, `web`, `worker` and `beat`. Give every dependency a health check, and use `depends_on` with `condition: service_healthy` (or `service_completed_successfully` for migrate).
3. **Configure.** Put non-secret defaults in the Compose file or `.env.example`, secrets in an ignored `.env`, and read them with `env_file` and interpolation. Use `${VAR:?message}` to fail early on a missing required value.
4. **Verify.** Run `docker compose config` to validate and render the file. Start the stack, check `docker compose ps` shows healthy services, hit the API, then run the tests inside the container. See the command list in the reference.

## Hard rules

- Use `condition: service_healthy` with a real health check, not bare `depends_on`. Mechanism: by default Compose waits only for a container to be running, not for the database to accept connections, so the app starts and its first connections fail.
- Reach other services by service name (`db`, `redis`), never `localhost`. Mechanism: inside a container `localhost` is that container, so the app would look for a database in itself.
- Keep database data in a named volume. Mechanism: container filesystems are ephemeral; without a volume `docker compose down` deletes the data. Mount the volume at the path the Postgres major version expects: `/var/lib/postgresql/data` up to 17, `/var/lib/postgresql` from 18, and mounting the wrong one does not persist data.
- Bind published database and broker ports to loopback (`"127.0.0.1:5432:5432"`) or omit them. Mechanism: a port published without a host IP binds to all interfaces and can be reachable from the network, bypassing host firewall rules.
- Quote port mappings. Mechanism: unquoted `22:22` style values can be parsed by YAML as a base-60 number.
- Never commit `.env` or put real secrets in the Compose file. Mechanism: Git history cannot be recalled. Commit `.env.example` with safe placeholders, and prefer Compose secrets or `_FILE` variables for passwords where the image supports them, because environment variables are visible to every process and leak into logs.
- Run `migrate` as one one-off service that the others wait on. Mechanism: several containers migrating at once race; one task that must complete first gives a single writer.
- Run the dev server only in the local `dev` target, bound to `0.0.0.0`. Mechanism: `runserver` binds to loopback by default, which is unreachable from outside the container; it is never a production server, so production keeps Gunicorn from the runtime image.
- Add `127.0.0.1` and `localhost` to `ALLOWED_HOSTS` for local settings, driven by an env var. Mechanism: with `DEBUG` off Django rejects unknown Host headers.
- Run Celery worker and beat as separate services. Mechanism: one process per concern lets each restart, scale and log on its own.
- Warn before `docker compose down -v` or deleting volumes, and confirm first. Mechanism: it permanently deletes the local database. Postgres init scripts also run only when the data directory is empty, so changing them needs a fresh volume.
- Do not hard-code the Compose project's secrets into the `command`. Mechanism: commands are visible in `docker inspect` and process lists.

## References

- [compose-example.md](references/compose-example.md): full example file, `.env.example`, command cheat sheet, hot reload options and the official sources.

## Next

- Image and Dockerfile: [django-docker-images](../django-docker-images/SKILL.md)
- Worker and beat behaviour: [django-celery](../django-celery/SKILL.md)
- Tests that run in the container: [django-testing](../django-testing/SKILL.md)
- Settings and env vars: [django-project-structure](../django-project-structure/SKILL.md)
