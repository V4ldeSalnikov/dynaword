# makefile of a dataset repo that depends on the package instead of carrying src/

install:
	@echo "--- 🚀 Installing project dependencies ---"
	uv sync

test:
	@echo "--- 🧪 Running tests ---"
	uv run pytest --pyargs dynaword.tests --rootdir=. | tee test_results.log

lint:
	@echo "--- 🧹 Running linters ---"
	uv run ruff format .
	uv run ruff check . --fix

bump-version:
	@echo "--- 🚀 Bumping patch version ---"
	uv run python -m dynaword.bump_version

update-descriptive-statistics:
	@echo "--- 🚀 Recomputing Descriptive statistics ---"
	uv run python -m dynaword.update_descriptive_statistics # compute missing descriptive statistics for all datasets
	uv run python -m dynaword.update_descriptive_statistics --dataset default --force # always ensure default dataset is up to date
