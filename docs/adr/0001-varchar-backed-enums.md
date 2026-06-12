# Store enums as VARCHAR, not native Postgres enum types

The source ERD declares eight native Postgres enum types (`log_action`, `otp_status`, etc.). We model these as Python `StrEnum`s but store them as `VARCHAR` columns (`native_enum=False`), enforcing the allowed set at the application boundary via Pydantic and the `StrEnum`, rather than creating native Postgres `ENUM` types.

We chose this because native Postgres enums are costly to evolve: `ALTER TYPE ... ADD VALUE` cannot run inside a transaction, values cannot be removed, and Alembic autogenerate does not detect enum changes. Several of these enums — `log_action` especially — are expected to grow as features are added, and we want those changes to be a one-line code edit with no migration. The trade-off is that we give up DB-level type enforcement; an out-of-band `INSERT` could write an unlisted string.
