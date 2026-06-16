# py-forge

A FastAPI + SQLAlchemy + Postgres backend starter — a Python port of the NestJS
`nest-forge` project. It ships an identity / RBAC / auth / logging foundation: every
table from the data model, all the infrastructure, and **one fully working vertical
slice** (admin login → JWT + refresh token → permission-guarded route) that locks in
the patterns. The other domains are modeled but their routes/services are stubs for you
to grow.

See [CONTEXT.md](CONTEXT.md) for the domain glossary and [docs/adr/](docs/adr/) for the
decisions that aren't obvious from the code.

## Stack

Python 3.13 · [uv](https://docs.astral.sh/uv/) · FastAPI · SQLAlchemy 2.0 (async) +
asyncpg · Alembic · Pydantic v2 / pydantic-settings · PyJWT · argon2-cffi · ruff · pytest

## Layout

```
src/
├── config.py        database.py      models.py (Base + mixins, soft-delete)
├── exceptions.py    dependencies.py  constants.py    main.py     registry.py
├── auth/      login/logout/refresh, JWT, password hashing, refresh_tokens + otp_records
├── admins/    admin entity + the example protected route
├── users/     user entity (phone/SMS/social) — modeled, stubbed
├── rbac/      roles, modules, permissions, role_permissions + require_permission()
├── logs/      activity_logs + audit_logs — modeled, stubbed
└── settings/  settings key/value store — modeled, stubbed
migrations/    Alembic (async)
scripts/seed.py
tests/         unit tests (no database)
```

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

Tests are **unit-only and never touch a database** (Argon2 round-trip, JWT
encode/decode, the permission-check branch against a fake session). This is a deliberate
starting point that trades the doc's "use a real DB, never mock it" rule for fast,
dependency-free CI — see `tests/`. When you're ready for integration tests, add a
Postgres (a CI `services:` container or testcontainers) and override `get_db` via
FastAPI's `dependency_overrides`; **don't** "fix" the unit tests by mocking persistence.

## Conventions baked in

- **snake_case** everywhere; fresh, independent database.
- **VARCHAR-backed enums** (`StrEnum`) — adding a value needs no migration ([ADR 0001](docs/adr/0001-varchar-backed-enums.md)).
- **Automatic soft-delete filtering** — soft-deleted rows are hidden from every query by
  default; opt in with `stmt.execution_options(include_deleted=True)` ([ADR 0002](docs/adr/0002-automatic-soft-delete-filter.md)).
- Server-side `gen_random_uuid()` UUID PKs; Argon2id password hashing; refresh tokens
  rotated on use and stored only as a hash.
- One `BaseSettings` per domain (`src/config.py` + `src/auth/config.py`).
- `/docs` and `/redoc` are disabled outside `local` / `staging`.
