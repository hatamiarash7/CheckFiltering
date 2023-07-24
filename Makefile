.PHONY: install lock run test lint help
.DEFAULT_GOAL := help

install: ## Install dependencies
	poetry install

lock: ## Update poetry.lock
	poetry lock

run: ## Run project
	poetry run katran-master

test: ## Run tests
	poetry run pytest

lint: ## Lint files
	find . -name "*.py" -not -ipath "./.venv/*" | xargs python3 -m pylint --rcfile=.pylintrc

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'