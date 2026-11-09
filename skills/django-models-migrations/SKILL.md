---
name: django-models-migrations
description: >
  Use when adding or changing a Django model, field, index, constraint, foreign
  key or primary key, writing or reviewing a migration, backfilling data, or
  setting database connection options such as timeouts, including when asked to
  use CASCADE everywhere, store money as a float, edit an applied migration or
  fake a migration. Governs model design, safe schema changes and production
  database settings for Django API projects. Do not use for queries and
  transactions (django-services-selectors), release and rollback process
  (django-release-governance) or hosting the database (django-aws-deployment).
---

# Django Models and Migrations

Stance: the database is the last line of defence and the hardest thing to change, so models state their rules and every schema change is safe to apply while the previous release is still running. Field choices inside those limits are flexible.

## Hard rules

- Choose `on_delete` on purpose for every foreign key: `PROTECT` by default, `CASCADE` only for rows that cannot exist without the parent and carry no history, `SET_NULL` only on a nullable field. Mechanism: symptom is deleted parents silently taking invoices, audit rows or ledger entries with them; cause is `CASCADE` chosen to make an error go away; fix is `PROTECT` and an explicit service that archives or deletes in the right order.
- Never store money in a `FloatField`. Use `DecimalField` with explicit `max_digits` and `decimal_places`, or an integer count of the smallest unit (cents) with a currency code beside it. Mechanism: binary floats cannot represent most decimal amounts, so totals drift by fractions of a cent.
- Put rules the database can enforce into named constraints (`UniqueConstraint`, `CheckConstraint`) in `Meta.constraints`, not only in code. Mechanism: code paths come and go, but a constraint holds for every writer, including scripts, admin and migrations. `CheckConstraint` takes `condition=`; the old `check=` argument was removed in Django 6.0. A constraint on an abstract base class needs `%(app_label)s` and `%(class)s` in its name, because every subclass inherits the same name. Constraints also run during `full_clean()`.
- A schema change must work with the previous release of the code as well as the new one: add first, switch the code, remove later. New columns are nullable or have a constant default; renames and drops happen in a later release than the code change. Mechanism: during a rolling deploy or a rollback, old and new code run against the same tables.
- Never edit or delete a migration that has been applied anywhere else, and never use `migrate --fake` unless you have confirmed the real schema already matches. Mechanism: the migration table then disagrees with the schema and later migrations fail or silently skip work; fix is a new corrective migration.
- Commit the migration with the model change, and have CI fail on a missing or conflicting migration. Mechanism: a model without its migration is not installable, and two branches with the same migration number break the next deploy.
- Avoid `GenericForeignKey` and multi-table inheritance unless a written reason says otherwise. Mechanism: a generic key has no database constraint or index on its target, and multi-table inheritance adds a hidden join per read; prefer an explicit foreign key, an abstract base class or a one-to-one relation.
- Set database timeouts and the connection policy explicitly in production settings. Mechanism: without a statement timeout one bad query holds a worker and its connection until the database gives up.
- Act only on what the user asked. Before answering or changing anything, open the relevant files and check what is already done; report only what you checked, never guess, and do not redo finished work. Reason: guesses and repeated work waste the user's credit.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| New or changed model, field, index, constraint or migration | Continue |
| Someone asks for `CASCADE` everywhere, a float for money, or to edit an applied migration | Push back; explain the mechanism and offer the safe path |
| Question is how a query or transaction should be written | Use [django-services-selectors](../django-services-selectors/SKILL.md) |
| Question is how to release or roll back | Use [django-release-governance](../django-release-governance/SKILL.md) |

## Steps

1. **Detect.** Read the app's `models.py` (or `models/` package), the base model, the latest migrations, the `DATABASES` setting and `DEFAULT_AUTO_FIELD`. Run `python manage.py showmigrations` against a development database to see what is applied. Say what you could not run.
2. **Fix.** Least invasive first:
   - Base model: one abstract model in the shared `common` app with `created_at` (`auto_now_add`) and `updated_at` (`auto_now`); other models inherit it. Use `django.utils.timezone.now()` and keep `USE_TZ` on. `auto_now` fields are not set by `QuerySet.update()` or `bulk_update()`, so pass the timestamp explicitly there.
   - Fields: avoid `null=True` on text fields (an empty string already means "no value"); `null` is a database rule and `blank` is a validation rule. Use `BigAutoField` for ids (it is the default from Django 6.0; on older versions set `DEFAULT_AUTO_FIELD`). Keep the default integer key; if clients must not guess ids, add a separate unique `uuid` field and expose that. Break a circular import between apps with a string reference (`"billing.Invoice"`). `__str__` returns a short label with no personal data.
   - Indexes: index columns that queries filter or order by often (a foreign key already has one); each index slows writes, so confirm with `queryset.explain()` on realistic data first (`analyze=True` runs the query). On a large PostgreSQL table create the index with `AddIndexConcurrently` from `django.contrib.postgres.operations` in a migration with `atomic = False`.
   - Adding a column: nullable or with a constant default (Django 5.0 and later offers a database-level `db_default`), then backfill, then tighten with a later migration. Making a column required, adding a unique constraint, or changing a type can lock or rewrite a big table, so check the generated SQL with `python manage.py sqlmigrate <app> <number>` first. On PostgreSQL, add a check constraint to a big table with `AddConstraintNotValid` in one migration and `ValidateConstraint` in a separate later one (Django documents that doing both together defeats the purpose).
   - Data changes: keep them out of the schema migration, in their own migration or a management command or task that works in batches. A `RunPython` step uses `apps.get_model`, is safe to run twice, has a reverse (`migrations.RunPython.noop` when nothing needs undoing), and reads no local files. Mechanism: the same migration runs on every developer machine and in staging.
   - Production connection settings: under WSGI, `CONN_MAX_AGE` above zero with `CONN_HEALTH_CHECKS` on reuses connections, but the database must have room for workers times connections. Under ASGI Django says to leave persistent connections off and use the database backend's pooling instead (on PostgreSQL with psycopg 3, `"OPTIONS": {"pool": True}` and the pool package installed). Set a statement timeout (and a lock timeout for migrations) with PostgreSQL's own settings, passed through the connection `OPTIONS` rather than a signal receiver, for example `{"options": "-c statement_timeout=30000"}`; this is PostgreSQL behaviour that Django passes through, so confirm it on staging. Follow the database driver's own guidance on which build to install for production.
3. **Verify.** `python manage.py makemigrations --check --dry-run` reports no changes; the migration applies on an empty database and on a copy of realistic data; `sqlmigrate` shows no unexpected table rewrite; the previous release's tests still pass against the new schema where that can be tried. Say which of these you could not run.

## Example

```python
import uuid
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Invoice(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey("billing.Customer", on_delete=models.PROTECT)
    total_cents = models.BigIntegerField()
    currency = models.CharField(max_length=3)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(total_cents__gte=0), name="invoice_total_not_negative"
            ),
        ]
```

Adding `public_id` to a table that already has rows needs three steps (add nullable, backfill, then make unique and required), because a single `default=uuid.uuid4` gives every existing row the same value.

## References

Django models, fields and constraints: https://docs.djangoproject.com/en/stable/topics/db/models/ . Migrations and the operations list: https://docs.djangoproject.com/en/stable/topics/migrations/ . PostgreSQL-specific operations: https://docs.djangoproject.com/en/stable/ref/contrib/postgres/operations/ . Persistent connections: https://docs.djangoproject.com/en/stable/ref/databases/#persistent-connections

## Next

- Queries, transactions and where validation lives: [django-services-selectors](../django-services-selectors/SKILL.md)
- Rolling back and releasing safely: [django-release-governance](../django-release-governance/SKILL.md)
- Running migrations once per release: [django-aws-deployment](../django-aws-deployment/SKILL.md)
- Tests that build model state: [django-testing](../django-testing/SKILL.md)
