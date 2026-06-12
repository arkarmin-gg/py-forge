.PHONY: help install run migrate makemigration downgrade seed test lint format

help:
	@echo "py-forge — common tasks"
	@echo "  make install         Install dependencies (uv sync)"
	@echo "  make run             Run the API with autoreload"
	@echo "  make migrate         Apply migrations (alembic upgrade head)"
	@echo "  make makemigration m=\"msg\"   Autogenerate a migration"
	@echo "  make downgrade       Revert the last migration"
	@echo "  make seed            Seed superadmin role + initial admin"
	@echo "  make test            Run unit tests"
	@echo "  make lint            Check lint + format (no changes)"
	@echo "  make format          Auto-fix lint + format"

install:
	uv sync

run:
	uv run uvicorn src.main:app --reload

migrate:
	uv run alembic upgrade head

makemigration:
	uv run alembic revision --autogenerate -m "$(m)"

downgrade:
	uv run alembic downgrade -1

seed:
	uv run python -m scripts.seed

test:
	uv run pytest

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

format:
	uv run ruff check --fix src tests
	uv run ruff format src tests
