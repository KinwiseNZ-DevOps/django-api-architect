---
name: django-aws-deployment
description: >
  Use when asked to deploy, host or move a Django project on AWS, to write an
  App Runner config, an ECS task definition or an Elastic Beanstalk config, or
  when a deployed Django app returns 400 on health checks or cannot reach its
  database. Governs deploying a Django API to AWS. Do not use for the Dockerfile
  itself (django-docker-images), the local stack (django-docker-compose),
  settings layout (django-project-structure) or non-AWS platforms.
---

# Django AWS deployment

Stance: the app is built once and configured by environment. Frozen: no secrets in code or images, a production server, a managed database outside the app container, migrations run once per release, and a health check that passes. Flexible: which AWS service hosts it, which follows the project's size, team skills and budget.

## Hard rules

- Never hard-code a secret, or put one in an image, an `apprunner.yaml`, a task definition or a repo. Mechanism: those files are readable by anyone with repo or image access. Reference a Secrets Manager or Parameter Store entry and give the runtime role read access to that one entry.
- Never use SQLite in production on these platforms. Mechanism: containers and instances are replaced, so local files disappear and several instances would hold different copies.
- Never leave `DEBUG` on or `ALLOWED_HOSTS = ["*"]` in production. Mechanism: debug pages leak settings, and a wildcard removes the Host header protection.
- Run `migrate` once per release, not on every start with more than one instance. Mechanism: several instances race to change the same tables. Elastic Beanstalk offers a leader-only command for this; on ECS use a one-off task (inference for ECS, supported by the Elastic Beanstalk documentation for its own platform).
- A secret read from the environment is fixed when the task starts. Mechanism: after a secret changes, force a new deployment or start a new task (stated in the ECS documentation for Secrets Manager values).
- Do not copy version pins from tutorials. Mechanism: the source articles pin old Python and Django versions; use the project's own pins and the platform's currently supported runtime.
- Never run AWS commands that create or delete resources without a person's yes. Mechanism: they cost money and can destroy data.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Project already deploys to AWS and the task is a small change | Follow its setup; change only what the task needs |
| Asked to choose where to host | Use the table in [aws-platforms.md](references/aws-platforms.md) and give one recommendation with reasons |
| Task is the Dockerfile or image | Use [django-docker-images](../django-docker-images/SKILL.md) |
| Task is settings layout or env var names | Use [django-project-structure](../django-project-structure/SKILL.md) |
| Asked to create AWS resources, change IAM, spend money or deploy | Prepare the config and commands and stop; a person with AWS access runs them |
| Asked to put a password or key in a config file, task definition or repo | Decline; reference a secret by name instead |

Reason: AWS actions cost money and change live systems, and a secret committed to a repo cannot be recalled.

## Steps

1. **Detect.** Find the settings module, the WSGI entry point, how the project reads environment variables, the database setting, the static files setup and any existing Dockerfile, `apprunner.yaml`, task definition or `.ebextensions`. Note the Python and Django versions in use.
2. **Choose.** If the platform is not decided, compare the three options in [aws-platforms.md](references/aws-platforms.md) and recommend one. Check current service availability and supported Python versions in the AWS documentation first; the source articles are dated.
3. **Prepare Django.** Make the shared changes in the reference: hosts, secrets from the environment, database from a connection setting, static files, proxy headers, a health endpoint and production checks.
4. **Write the platform config.** Use the matching section of the reference, with placeholders for account IDs, ARNs and domain names.
5. **Plan migrations.** Run `migrate` once per release as a separate step, not in every container start, unless there is exactly one instance and the person accepts the risk.
6. **Verify.** Run `python manage.py check --deploy` with the production settings. Confirm the health check path returns 200 with the platform's Host header. Say which AWS steps were not run.

## Checklist

```text
- [ ] No secret in code, image, task definition or committed config
- [ ] ALLOWED_HOSTS covers the public domain and the health check host
- [ ] Production server (Gunicorn), never runserver
- [ ] Database is managed (RDS), not SQLite
- [ ] Static files served (WhiteNoise or S3 with CloudFront)
- [ ] Behind the load balancer: HTTPS and proxy header settings correct
- [ ] Health check path returns 200 without logging in
- [ ] Migrations run once per release
- [ ] Logs reach CloudWatch
- [ ] Placeholders used for account IDs, ARNs and hostnames
```

## Example

Input: "Our Fargate service keeps replacing tasks; the target group says unhealthy."
Output: the load balancer calls the task by its private IP, so Django rejects the Host header with a 400 and the health check fails. Fix by serving the health path without the host check (a small middleware) or allowing the task's host, point the target group at that path, and confirm in the target health reason code (for example `Target.ResponseCodeMismatch`) before and after.

## References

- [aws-platforms.md](references/aws-platforms.md): the choice table, shared Django settings, and the Fargate, App Runner and Elastic Beanstalk sections with placeholder config.

## Next

- Image and start command: [django-docker-images](../django-docker-images/SKILL.md)
- Settings and env vars: [django-project-structure](../django-project-structure/SKILL.md)
- Workers and schedules: [django-celery](../django-celery/SKILL.md)
