.PHONY: lint fmt test add-pre-commit

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff format .
	uv run ruff check --fix .
	
test:
	uv run pytest -q

add-pre-commit:
	uv run pre-commit install
