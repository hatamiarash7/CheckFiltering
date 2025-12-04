.PHONY: clean install lock run build test test-cov lint format type-check check pre-commit help
.DEFAULT_GOAL := help

# Colors for pretty output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

clean: ## Clean build files and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf dist build *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	poetry install

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	poetry install --with dev,test

lock: ## Update poetry.lock
	@echo "$(BLUE)Updating lock file...$(RESET)"
	poetry lock

run: ## Run the CLI application
	poetry run check-filter

build: clean ## Build package
	@echo "$(BLUE)Building package...$(RESET)"
	poetry build

test: ## Run tests
	@echo "$(BLUE)Running tests...$(RESET)"
	poetry run pytest

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	poetry run pytest --cov=check_filter --cov-report=html --cov-report=term-missing

test-fast: ## Run tests excluding slow/integration tests
	@echo "$(BLUE)Running fast tests...$(RESET)"
	poetry run pytest -m "not slow and not integration"

lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(RESET)"
	poetry run ruff check check_filter tests
	poetry run pylint check_filter

lint-fix: ## Run linters and fix auto-fixable issues
	@echo "$(BLUE)Running linters with auto-fix...$(RESET)"
	poetry run ruff check --fix check_filter tests

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	poetry run black check_filter tests
	poetry run isort check_filter tests

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code format...$(RESET)"
	poetry run black --check check_filter tests
	poetry run isort --check-only check_filter tests

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	poetry run mypy check_filter

check: format-check lint type-check test ## Run all checks (format, lint, type-check, test)
	@echo "$(GREEN)All checks passed!$(RESET)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	poetry run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	poetry run pre-commit install

docs: ## Generate documentation (placeholder)
	@echo "$(YELLOW)Documentation generation not configured yet$(RESET)"

release-patch: ## Bump patch version
	@echo "$(BLUE)Bumping patch version...$(RESET)"
	poetry version patch

release-minor: ## Bump minor version
	@echo "$(BLUE)Bumping minor version...$(RESET)"
	poetry version minor

release-major: ## Bump major version
	@echo "$(BLUE)Bumping major version...$(RESET)"
	poetry version major

help: ## Show this help
	@echo "$(BLUE)CheckFilter - Development Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'