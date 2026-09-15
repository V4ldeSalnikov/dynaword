install:
	@echo "--- 🚀 Installing the package ---"
	uv sync

lint:
	@echo "--- 🧹 Running linters ---"
	uv run ruff format .
	uv run ruff check . --fix
