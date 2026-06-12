# Soft-deleted rows are filtered automatically, not per-query

Tables that inherit soft-delete (admins, users, roles, modules, permissions, settings) carry a `deleted_at` column via a `SoftDeleteMixin`. Rather than requiring every read to add `WHERE deleted_at IS NULL`, we register a session-level `do_orm_execute` event that applies `with_loader_criteria` so soft-deleted rows are excluded from every ORM query by default. To include them deliberately, a query opts in via an execution option.

We chose this because the dominant soft-delete failure mode is a developer forgetting the filter and leaking deleted rows; making exclusion the default eliminates that class of bug. The cost is non-obvious behavior — a reader who writes a straightforward query and sees rows "missing" must know the global filter exists, which is why this is recorded here. The escape hatch (an execution option to include deleted rows) keeps administrative/restore flows possible.
