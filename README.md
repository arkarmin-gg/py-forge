# py-forge

A FastAPI + SQLAlchemy + Postgres backend starter — a Python port of the NestJS
`nest-forge` project. It ships an identity / RBAC / auth / logging foundation: every
table from the data model, all the infrastructure, and a working **admin console** API.

The API is split by audience under the version prefix: `/admin` (back-office, governed
by the Admin model + RBAC) and `/app` (mobile/frontend — a reserved namespace, still
empty). On the admin side, **auth**, **admins**, **rbac**, and **settings** are fully
implemented with CRUD routes; **logs** exposes audit-log listing (the Activity Log for
end Users is modeled but has no endpoint yet). The **users** domain is modeled only —
its `/app` routes and services are the main thing left for you to grow.

See [CONTEXT.md](CONTEXT.md) for the domain glossary and [docs/adr/](docs/adr/) for the
decisions that aren't obvious from the code.

## Stack

Python 3.13 · [uv](https://docs.astral.sh/uv/) · FastAPI · SQLAlchemy 2.0 (async) +
asyncpg · Alembic · Pydantic v2 / pydantic-settings · PyJWT · argon2-cffi · ruff · pytest

## Layout

```
src/
├── config.py        database.py      models.py (Base + mixins, soft-delete)
├── exceptions.py    dependencies.py  constants.py     main.py     registry.py
├── schemas.py       request/response base models (ErrorResponse, RequestSchema, ResponseSchema)
├── pagination.py    Page / PaginationParams / paginate() / get_all()
├── query_filters.py where_if_not_none / where_gte_if_not_none / where_lte_if_not_none
├── api/routers.py   top-level router assembly: /admin and /app under the version prefix
├── storage/         S3 client + presigned URLs (own BaseSettings)
└── modules/
    ├── auth/      login/logout/refresh, JWT, password hashing, refresh_tokens + otp_records, /me
    ├── admins/    admin entity + full CRUD (the example protected routes)
    ├── users/     user entity (phone/SMS/social) — modeled only, not wired to routes
    ├── rbac/      roles, modules, permissions, role_permissions + require_permission()
    ├── logs/      activity_logs (modeled) + audit_logs (listing endpoint)
    └── settings/  settings key/value store — full CRUD by key
migrations/    Alembic (async)
scripts/seed.py
tests/         (empty — see Testing below)
```

`src/registry.py` imports every model module for its side effects so `Base.metadata` is
complete; import it wherever the full schema is needed (app, Alembic, seed).

## Prerequisites

- Python 3.13 and `uv`
- **Your own Postgres 13+** (this starter intentionally ships no Docker Compose). Create
  a database and put its URL in `.env`.

## Quick start

```bash
uv sync                       # install everything
cp .env.example .env          # then edit DATABASE_URL + AUTH_JWT_SECRET

createdb py_forge             # or point DATABASE_URL at any Postgres you have
make migrate                  # apply the schema
make seed                     # superadmin role + permissions + initial admin
make run                      # http://127.0.0.1:8000 — docs at /docs
```

Try the slice from `/docs`: **POST `/api/v1/admin/auth/login`** with the seeded
`ADMIN_EMAIL` / `ADMIN_PASSWORD` (email goes in the `username` field), click
**Authorize** with the returned access token, then call **GET `/api/v1/admin/admins`** — it's
guarded by `require_permission("admins", READ)`.

## Make targets

| Command | What it does |
| --- | --- |
| `make run` | API with autoreload |
| `make migrate` | `alembic upgrade head` |
| `make makemigration m="msg"` | autogenerate a migration |
| `make downgrade` | revert the last migration |
| `make seed` | seed superadmin role + initial admin |
| `make test` | run unit tests |
| `make lint` / `make format` | ruff check + format |

## Testing

There are **no tests yet** — `tests/` holds only an empty `__init__.py`, and `make test`
runs pytest against an empty suite. Pytest is wired up (`pytest` + `pytest-asyncio`,
`asyncio_mode = "auto"` in `pyproject.toml`), so you can start adding tests immediately.

The intended starting point is **unit tests that never touch a database** (Argon2
round-trip, JWT encode/decode, the permission-check branch against a fake session) —
fast, dependency-free CI. When you're ready for integration tests, add a Postgres (a CI
`services:` container or testcontainers) and override `get_db` via FastAPI's
`dependency_overrides`; **don't** mock persistence to make tests pass.

## Conventions baked in

- **snake_case** everywhere; fresh, independent database.
- **VARCHAR-backed enums** (`StrEnum`) — adding a value needs no migration ([ADR 0001](docs/adr/0001-varchar-backed-enums.md)).
- **Automatic soft-delete filtering** — soft-deleted rows are hidden from every query by
  default; opt in with `stmt.execution_options(include_deleted=True)` ([ADR 0002](docs/adr/0002-automatic-soft-delete-filter.md)).
- Server-side `gen_random_uuid()` UUID PKs; Argon2id password hashing; refresh tokens
  rotated on use and stored only as a hash.
- One `BaseSettings` per domain — global `src/config.py`, plus `src/modules/auth/config.py`
  (`AUTH_` prefix) and `src/storage/config.py` (`S3_` prefix).
- **Offset/limit pagination** — list endpoints return `Page[T]` via `src/pagination.py`
  (`paginate()` + the `pagination_params` dependency) ([ADR 0005](docs/adr/0005-offset-limit-pagination.md)).
- **Composable query filters** — `src/query_filters.py` `where_*_if_not_none` helpers build
  optional `WHERE` clauses while preserving the statement's exact type.
- **Audience-split API** — `/admin` (Admin + RBAC) vs `/app` (mobile/frontend), assembled in
  `src/api/routers.py` ([ADR 0003](docs/adr/0003-api-audience-namespace-split.md)).
- **Central model registry** — `src/registry.py` populates `Base.metadata` for app, Alembic,
  and seed ([ADR 0004](docs/adr/0004-model-registry-metadata.md)).
- `/docs` and `/redoc` are disabled outside `local` / `staging`.
