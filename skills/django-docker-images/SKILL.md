---
name: django-docker-images
description: >
  Use when writing or changing a Dockerfile, an image build, ARG or ENV values,
  a container CMD, or a HEALTHCHECK, including when asked to use runserver or to
  pass secrets as build arguments. Governs Dockerfiles and container images for
  Django API projects. Do not use for the local multi-service stack (django-
  docker-compose), settings layout (django-project-structure) or Celery task
  code (django-celery).
---

# Django Docker Images

Stance: the image is a reproducible build artefact. Frozen: a non-root runtime user, no secrets in layers, exec-form commands, and a production server (never `runserver`) in the runtime stage. Flexible: base image choice, requirements layout and tooling (pip, uv, poetry), which follow the project.

## Hard rules

- Never run `runserver` in the runtime stage. Mechanism: Django states it has had no security audit or performance testing and is unsuitable for production; the runtime stage uses a production WSGI or ASGI server such as Gunicorn.
- Run as a non-root user with an explicit UID and GID. Mechanism: automatically assigned IDs can change across rebuilds, and a process running as root turns any container escape or file-write bug into a bigger one.
- Never put a secret in `ENV`, `ARG` or a copied file. Mechanism: those values persist in image layers and anyone with the image can read them. Pass runtime secrets as environment variables or mounted files at run time, and build-time secrets with a build secret mount.
- Use exec-form `CMD` and `ENTRYPOINT` (a JSON array), and `exec` in any wrapper script. Mechanism: shell form runs under `/bin/sh -c`, so the server is not PID 1 and does not receive `SIGTERM` from `docker stop`, which means slow, forced kills and dropped requests.
- Keep `apt-get update` and `apt-get install` in one `RUN`, with `--no-install-recommends` and cleanup of `/var/lib/apt/lists` in the same layer. Mechanism: a cached `update` layer can go stale and make installs fail, and cleanup in a later layer does not shrink the image.
- Copy dependency files and install before copying source. Mechanism: a source edit then reuses the cached dependency layer instead of reinstalling everything.
- Pin the base image to at least a minor version tag, and rebuild regularly. Mechanism: tags are mutable and an image is a snapshot of its base at build time, so unpinned builds drift and old builds miss security fixes. Digest pinning gives full reproducibility but needs automated updates.
- Set `PYTHONUNBUFFERED=1` and `PYTHONDONTWRITEBYTECODE=1` in the image. Mechanism: unbuffered output reaches `docker logs` immediately, and skipping `.pyc` files keeps the writable layer clean.
- Do not run `migrate` in the runtime `CMD`. Mechanism: with more than one replica, several containers race to migrate on start; run migrations as a separate one-off step (inference).
- If `collectstatic` runs at build time, pass its required settings inline for that one `RUN`, not as persistent `ENV`. Mechanism: required secrets have no default, so the command needs values, and persistent `ENV` would bake them into the image.
- Allow the health check's host in `ALLOWED_HOSTS`. Mechanism: with `DEBUG` off Django rejects unknown Host headers, so a check calling `127.0.0.1` fails as unhealthy unless that host is allowed.
- Set Gunicorn `--workers` deliberately. Mechanism: the Gunicorn docs suggest starting at (2 x CPU cores) + 1 and adjusting under load; sync workers need a buffering proxy such as nginx in front.
- Act only on what the user asked. Before answering or changing anything, open the relevant files and check what is already done; report only what you checked, never guess, and do not redo finished work. Reason: guesses and repeated work waste the user's credit.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| The project already has a Dockerfile that builds and runs | Follow its conventions; change only what the task needs |
| No Dockerfile exists | Continue; write a multi-stage one from the example |
| The task is the local stack of web, database, broker and workers | Use [django-docker-compose](../django-docker-compose/SKILL.md) |
| The task changes settings, env vars or app layout | Use [django-project-structure](../django-project-structure/SKILL.md) |
| Asked to put a secret in an `ENV`, `ARG` or `COPY` | Decline; use a runtime variable, a mounted secret or a build secret |

Reason: an image that works on one machine but bakes in local state or secrets is the usual source of "works on my machine" and of leaked credentials.

## Steps

1. **Detect.** Find the existing `Dockerfile`, `.dockerignore`, requirements or lock files, the settings module, the WSGI or ASGI entry point, and any health endpoint. Read the project's conventions before changing anything.
2. **Write.** Use stages: a shared `base`, a dependency stage that builds the virtual environment, a `dev` target, and a final `runtime` target. The last stage is the default build target, so make it the production-shaped one. The full example with comments is in [dockerfile-example.md](references/dockerfile-example.md). Order instructions from least to most frequently changing: system packages, dependency files, installed dependencies, then source code.
3. **Ignore.** Write a `.dockerignore` that excludes `.git`, `.env` and other env files, virtual environments, `__pycache__`, media, test caches and local databases. See the example in the reference.
4. **Verify.** Build both targets. Run the runtime image as its non-root user. Run `python manage.py check --deploy` against the production settings inside the image. Confirm `docker history` shows no secret values. Start the container and confirm the health check reaches healthy.

## References

- [dockerfile-example.md](references/dockerfile-example.md): multi-stage Dockerfile, `.dockerignore`, health check and verification commands, with the official sources they follow.

## Next

- Local stack with database, broker and workers: [django-docker-compose](../django-docker-compose/SKILL.md)
- Settings and environment variables: [django-project-structure](../django-project-structure/SKILL.md)
- Worker and beat commands: [django-celery](../django-celery/SKILL.md)
