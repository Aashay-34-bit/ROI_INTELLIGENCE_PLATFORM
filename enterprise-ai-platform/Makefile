.PHONY: install dev test lint seed eval up down
install:
	uv sync --extra dev
dev:
	uv run uvicorn app.main:app --reload
test:
	uv run pytest
lint:
	uv run ruff check app tests
seed:
	uv run python scripts/seed_demo_requests.py
eval:
	uv run python scripts/run_eval.py
up:
	docker compose up --build
down:
	docker compose down
