# AWS platforms for Django

Contents: choosing a platform, shared Django settings, ECS on Fargate, App Runner, Elastic Beanstalk, sources and limits.

Sources: the AWS Containers blog post on deploying Django to App Runner, the Elastic Beanstalk developer guide page on deploying Django, and the Amazon ECS and Elastic Load Balancing developer guides. A Medium article on Fargate was also requested but could not be read (the site refused the request), so the Fargate section rests on the AWS documentation only. The sources use old Python and Django versions; nothing here pins a version. Check current availability, quotas and supported runtimes in the AWS documentation before building.

## Choosing a platform

| | ECS on Fargate | App Runner | Elastic Beanstalk |
|---|---|---|---|
| What you give it | A container image | A container image or source repo | A zipped project and a config |
| You manage | Task definition, service, load balancer, networking | Very little; a service config | The environment settings and instances' platform choices |
| Control | Most | Least | Middle |
| Good for | An existing Docker setup, workers beside the web app, tighter networking | A small web API that scales on requests | A team that wants a quick start without Docker |
| Watch for | Most moving parts to set up | Check it still suits a new project (see current docs) | Platform branches retire; Django and Python versions must match the platform |

Default recommendation for this repo's style (Docker images, Celery workers, Compose locally): ECS on Fargate, because the same image runs the web app and the workers. Choose App Runner for a single small API with no workers, and Elastic Beanstalk only when the team is not using containers.

## Shared Django settings

Read everything environment-specific from environment variables. The names below are examples; follow the project's own.

```python
import os

DEBUG = False
ALLOWED_HOSTS = os.environ["DJANGO_ALLOWED_HOSTS"].split(",")  # e.g. api.example.com
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # injected from Secrets Manager
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")  # only behind a trusted proxy
CSRF_TRUSTED_ORIGINS = os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"].split(",")  # full https:// origins
```

- Database: one connection setting such as `DATABASE_URL` (the App Runner article used `dj-database-url`), stored as a secret, pointing at RDS for PostgreSQL. The app and the database must be able to reach each other through security groups.
- Static files: either WhiteNoise (the middleware directly after `SecurityMiddleware`, and a compressed manifest storage backend) or S3 with CloudFront through `django-storages` for media and heavier assets. Run `collectstatic` at build time or once per release, not by hand.
- HTTPS: a load balancer or the platform ends TLS and forwards plain HTTP. Set the proxy header setting only when the proxy always sets that header, otherwise clients can fake it.
- Health endpoint: a cheap path such as `/healthz/` that returns 200 without authentication or a database call. Keep it separate from a deeper readiness check.
- `ALLOWED_HOSTS` and health checks: the load balancer calls the task by its private IP, so Django answers 400 for an unknown Host and the target turns unhealthy. Choose one fix: serve the health path from a tiny middleware placed before the host check, or add the task's host (inference from how Django validates Host; confirm in your environment). Do not use `"*"`.
- Run `python manage.py check --deploy` with the production settings, as in [django-docker-images](../../django-docker-images/SKILL.md).

## ECS on Fargate

- Fargate runs containers without servers. A task definition sets `requiresCompatibilities` to `FARGATE`, the CPU and memory, and `awsvpc` networking. Because of `awsvpc`, an Application Load Balancer target group must use target type `ip`, not `instance`.
- Secrets: the container definition's `secrets` field maps an environment variable name to a Secrets Manager (or Parameter Store) ARN. The task execution role needs permission to read that secret. If the secret changes, force a new deployment.

```json
{
  "containerDefinitions": [{
    "name": "web",
    "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/<repo>:<tag>",
    "portMappings": [{ "containerPort": 8000 }],
    "environment": [{ "name": "DJANGO_ALLOWED_HOSTS", "value": "api.example.com" }],
    "secrets": [
      { "name": "DJANGO_SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:<region>:<account-id>:secret:<name>" },
      { "name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:<region>:<account-id>:secret:<name>" }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": { "awslogs-group": "/ecs/<service>", "awslogs-region": "<region>", "awslogs-stream-prefix": "web" }
    }
  }]
}
```

- Application Load Balancer health check settings (AWS defaults): protocol HTTP, path `/`, success code 200, interval 30 seconds, timeout 5 seconds, healthy after 5 successes, unhealthy after 2 failures. Set the path to the health endpoint. A new target must pass a check before it receives traffic.
- Migrations: run as a separate one-off task using the same image, before the service update (inference; not stated in the sources).
- Workers: run Celery as a separate service from the same image with a different command; see [django-celery](../../django-celery/SKILL.md).
- Fargate Spot is cheaper but tasks can be interrupted with a two-minute warning, so use it only for work that can restart.

## App Runner

- Deploys from a source repository (App Runner builds it) or from an image. The blog post covers the source route.
- Config file `apprunner.yaml`, placeholders only:

```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: sh startup.sh
  network:
    port: 8000
  secrets:
    - name: DATABASE_SECRET
      value-from: "arn:aws:secretsmanager:<region>:<account-id>:secret:<name>"
```

- The post's `startup.sh` ran migrations, then `collectstatic`, then Gunicorn. That is simple, but it runs `migrate` on every start. Keep it only for a single instance, and prefer a one-off migrate step once the service scales above one.
- `ALLOWED_HOSTS` in the post was the default App Runner domain suffix; add your custom domain when you attach one.
- Database access: App Runner runs in an AWS-managed network. To reach RDS in your own network, add a VPC connector for outgoing traffic, with subnets and a security group that RDS allows.
- Instance role: give it only `secretsmanager:GetSecretValue` on the one secret.
- Scaling: set minimum size, maximum size and maximum concurrency per instance, and tune CPU, memory and concurrency by load testing. The maximum is limited by the account's Fargate on-demand vCPU quota.
- The post did not cover health check configuration; check the current App Runner documentation.

## Elastic Beanstalk

- The EB CLI flow: `eb init`, `eb create`, `eb status` (to find the environment's domain), add that domain to `ALLOWED_HOSTS`, then `eb deploy`. `eb terminate` removes the environment when you are finished, and the application stays.
- `requirements.txt` lists the packages installed on the instances. Keep it pinned and generated from the project's own tool.
- `.ebextensions/django.config` sets the WSGI entry point (the tutorial's value was `<project>.wsgi:application`; for older Amazon Linux AMI platforms it was a file path, so match the platform).

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: <project>.wsgi:application
```

- Migrations with a leader-only command so only one instance runs them:

```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python3 manage.py migrate"
    leader_only: true
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: <project>.settings
```

- Static files: set `STATIC_ROOT`, run `collectstatic` (the tutorial ran it locally and deployed the output), and make sure the platform serves the static path. Prefer the shared WhiteNoise or S3 approach above so there is one way to do it.
- The tutorial used SQLite for simplicity and said production should use RDS kept separate from the environment. Follow that advice.
- Keep secrets out of `.ebextensions`; set them as environment properties from a secret store, not literals in a committed file.

## Limits of this guide

- No AWS resources were created or tested. The snippets are patterns with placeholders, not verified end to end.
- Service availability, quotas, platform versions and prices change; check the AWS documentation on the day you build.
