.PHONY: lint fmt test

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff format .
	uv run ruff check --fix .
	
test:
	uv run pytest -q
