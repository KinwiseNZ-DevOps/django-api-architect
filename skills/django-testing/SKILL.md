---
name: django-testing
description: >
  Governs the test suite for Django API projects: pytest layout, what to test
  at each layer, mocking boundaries, and test-state construction. Use when
  writing, changing or reviewing tests, deciding what to mock, or adding
  coverage for a service, selector, API or task. Do not use for writing the
  production code the tests cover; that is owned by the sibling skills.
---

# Django Testing

Stance: the pytest layout and the mock boundaries are frozen; what counts as enough coverage per layer follows the layer's own skill. Tests mirror the module structure.

## Agent dispatch

Before handling a request, follow the agent selection workflow in [django-api-architect](../django-api-architect/SKILL.md), including when this specialist skill is invoked directly. Give the selected agent this skill's instructions. If the runtime cannot discover or invoke an agent, continue the work yourself using this skill.

## Gate

| Situation | Action |
|---|---|
| Tests accompany a code change (they always should) | Continue |
| Someone proposes skipping tests for a "trivial" service change | Push back; the service layer is the project's contract |
| Pure plumbing with no logic (an import, a constant) | A smoke-level test or none is acceptable; say which |

## Steps

1. **Detect.** Find `<app>/tests/`. Confirm the layout: `test_services.py`, `test_selectors.py`, `test_apis.py`, `test_models.py`, `test_tasks.py`, plus dedicated files for special surfaces (webhooks, admin). Classes are `Test<Thing>` with plain asserts; database tests carry `@pytest.mark.django_db`.
   If the project has no pytest setup, add it first and keep it small: `pytest` and `pytest-django` in the dev requirements (ask before adding a dependency), a `pytest.ini` with `DJANGO_SETTINGS_MODULE = config.settings.test` and `python_files = test_*.py`, and a root `conftest.py` holding an `api_client` fixture (`rest_framework.test.APIClient`) and the shared user fixture. Mechanism: without `DJANGO_SETTINGS_MODULE` pytest-django cannot start, and the first run fails before any test executes.
2. **Fix.** Write tests by layer:
   - Services: exhaustive coverage of the business logic, hitting the database, with task calls and everything outside the project mocked. Patch at the point of use (`apps.billing.services.stripe.Customer.create`), not at the provider's own module.
   - Selectors: coverage of filtering and ownership scoping; verify a caller cannot fetch another user's rows.
   - APIs: status codes, response shapes, the error contract, permission outcomes.
   - Models: only when the model adds validation, properties or methods; validation tests need no database.
   - Tasks: that they call the service, retry on failure, and stop after `max_retries`.
   - `on_commit` triggers: tests that run inside a rolled-back transaction never fire `transaction.on_commit` callbacks. Collect them with Django's `captureOnCommitCallbacks()` to assert the task was scheduled, and check whether your pytest-django version offers an equivalent fixture.
   - Build state through real services (`user_create`) rather than raw `Model.objects.create()`, so validation runs in test state too; use fixtures for shared state.
3. **Verify.** `python -m pytest` passes (single app: `python -m pytest apps/<name>/tests`); every changed behaviour has at least one failure-path test.

## Hard rules

- Mock only at boundaries: task `.delay` calls and anything that leaves the project. Never mock the ORM or the function under test. Mechanism: symptom is tests that pass while production fails; cause is mocked internals hiding real query, transaction or validation behaviour; fix is real database plus boundary mocks.
- Every service change lands with its tests in the same change. Mechanism: deferred tests do not happen, and the service layer is where regressions are cheapest to catch.
- Do not assert on private state or implementation order; assert observable outcomes (returned objects, database rows, response bodies, mock call counts at boundaries). Mechanism: implementation-coupled tests break on refactor and teach the wrong lesson.

## References

Rules source: the public Django Styleguide, https://github.com/HackSoftware/Django-Styleguide (testing section); starter practice follows pytest conventions. `on_commit` in tests: https://docs.djangoproject.com/en/6.1/topics/db/transactions/

## Next

- The layers under test: [django-services-selectors](../django-services-selectors/SKILL.md), [django-apis-serializers](../django-apis-serializers/SKILL.md)
- Task retry semantics: [django-celery](../django-celery/SKILL.md)
