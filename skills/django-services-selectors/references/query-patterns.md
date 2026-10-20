# Query patterns for selectors and services

Contents: evaluating a queryset once, select_related/prefetch_related, defer/only, bulk methods skip signals, foreign key shortcuts, raw SQL safety, search

Distilled from Django's database topic guides (https://docs.djangoproject.com/en/stable/topics/db/optimization/, .../sql/, .../search/); check them directly for anything this file does not cover.

## Evaluate a queryset once, then reuse it

`QuerySet.exists()`, `.count()` and `len()` each run their own query. Calling more than one of them, or calling one after the queryset has already been evaluated some other way, is an extra round trip for no reason:

```python
# wrong: up to three separate queries for one answer
def order_summary_for_user(*, user):
    items = Order.objects.filter(user=user)
    if items.exists():
        return {"count": items.count(), "first": items.first()}

# right: one query, reused
def order_summary_for_user(*, user):
    items = list(Order.objects.filter(user=user))
    if items:
        return {"count": len(items), "first": items[0]}
```

Use `exists()`, `count()` or `contains()` only when nothing else about the result is needed; otherwise evaluate the queryset once (iterate it, or force it with `list()`) and work from that.

## N+1: select_related and prefetch_related

A selector that returns a queryset the caller will iterate and access relations on must declare those relations up front, not leave the caller to trigger one query per row:

```python
# wrong: one query per order to reach its user, inside a loop at the caller
def orders_for_billing_run():
    return Order.objects.filter(status="pending")

# right: the relation the caller needs is already loaded
def orders_for_billing_run():
    return Order.objects.filter(status="pending").select_related("user")
```

`select_related()` is for a forward foreign key or one-to-one (one extra join, one query). `prefetch_related()` is for a reverse foreign key or a many-to-many (a second query, joined in Python); use a `Prefetch` object when the prefetched side itself needs filtering or ordering. Related-object access goes through the relation's base manager, not any custom default manager on that model, so a custom manager's filtering is not automatically applied there.

## defer() and only() can make things worse

Excluding columns only helps when the excluded columns are large (long text, JSON blobs) and are not about to be accessed anyway; the database still has to read most of a row's other columns regardless. Reaching for a deferred field later costs an extra query per instance. Profile before using either, and prefer `values()` or `values_list()` instead when the caller only needs plain data, not model instances or behaviour.

## Bulk methods skip save() and signals

`QuerySet.update()`, `QuerySet.delete()`, `bulk_create()` and `bulk_update()` operate directly in the database and do not call each instance's `save()` or `delete()`, and do not send `pre_save`, `post_save`, `pre_delete` or `post_delete`. Any side effect a service relies on through a signal, or through logic in an overridden `save()`, silently does not run for rows touched this way:

```python
# if anything (a signal, an overridden save()) depends on post_save firing
# per instance, this silently skips it for every row
Order.objects.filter(status="pending").update(status="cancelled")
```

If a bulk write needs the same side effects as the single-row path, call the service that produces those side effects once per affected row (accepting the extra queries), or make the side effect explicit in the same service that issues the bulk write, rather than relying on a signal to catch it.

## Prefer the field id to the related object when only the id is needed

`order.user_id` reads the foreign key column directly, with no query. `order.user.id` fetches the entire related object first. Use the `_id` form whenever only the id itself is needed.

## Raw SQL: parameterize, never format

Reach for `Manager.raw()` or `connection.cursor()` only once the ORM genuinely cannot express the query (a database-specific function, a query shape the ORM has no API for). Either way, the same rule applies, and it is the same rule the ORM itself follows for every normal query:

```python
# right: an unquoted placeholder, the value passed separately
Person.objects.raw("SELECT * FROM myapp_person WHERE last_name = %s", [last_name])

cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])

# wrong, both of these are SQL injection: never string-format a value into
# the query, and never quote a placeholder
Person.objects.raw("SELECT * FROM myapp_person WHERE last_name = '%s'" % last_name)
cursor.execute("UPDATE bar SET foo = 1 WHERE baz = '%s'" % self.baz)
```

Leaving the `%s` placeholder unquoted and passing the value through `params` is what makes it safe; quoting the placeholder or building the string with formatting defeats that regardless of whether the value happens to come from a trusted source this time. `Manager.raw()` does not validate that the SQL it is given actually returns rows shaped like the model; a malformed query surfaces as a confusing error rather than a clear one. See security-code-review for the same rule from the attacker's side.

## Search: plain lookups, then full-text, then trigram

`icontains` is a reasonable starting point but is a substring match, not a language-aware search, and depends on the user guessing an exact fragment. PostgreSQL-only tools improve on it in two different ways, and the choice depends on the data: full-text search (`django.contrib.postgres.search`, `SearchVector`, or the simpler `field__search` lookup) matches on words, with stemming and stop-word handling, and suits body text where whole-word relevance matters; trigram similarity (`trigram_similar`) matches on letter sequences and suits short, misspelling-prone fields such as names. Both are PostgreSQL-specific; Django has no built-in equivalent for other backends. This file covers only the basic shape; `SearchQuery`, `SearchRank` and the indexing a production search needs (a `GinIndex`, typically) are in Django's `contrib.postgres` search reference, not summarised here.
