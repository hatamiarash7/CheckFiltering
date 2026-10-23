POETRY ?= poetry

# Colors for pretty output
BLUE ?= \033[36m
GREEN ?= \033[32m
YELLOW ?= \033[33m
RESET ?= \033[0m

export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

.DEFAULT_GOAL := help

##@ General

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} \
		/^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Development

.PHONY: install
install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(POETRY) install

.PHONY: install-dev
install-dev: ## Install development and test dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(POETRY) install --with dev,test

.PHONY: lock
lock: ## Update the Poetry lockfile
	@echo "$(BLUE)Updating lock file...$(RESET)"
	$(POETRY) lock

.PHONY: run
run: ## Run the CLI application
	$(POETRY) run check-filter

.PHONY: build
build: clean ## Clean artifacts and build the package
	@echo "$(BLUE)Building package...$(RESET)"
	$(POETRY) build

##@ Quality

.PHONY: test
test: ## Run all tests, including live DNS tests
	@echo "$(BLUE)Running tests...$(RESET)"
	$(POETRY) run pytest

.PHONY: test-cov
test-cov: ## Run all tests with coverage reports
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(POETRY) run pytest --cov=check_filter --cov-report=html --cov-report=term-missing

.PHONY: test-fast
test-fast: ## Run tests excluding slow and integration tests
	@echo "$(BLUE)Running fast tests...$(RESET)"
	$(POETRY) run pytest -m "not slow and not integration"

.PHONY: lint
lint: ## Run Ruff and Pylint
	@echo "$(BLUE)Running linters...$(RESET)"
	$(POETRY) run ruff check check_filter tests
	$(POETRY) run pylint check_filter

.PHONY: lint-fix
lint-fix: ## Fix auto-fixable Ruff issues
	@echo "$(BLUE)Running linters with auto-fix...$(RESET)"
	$(POETRY) run ruff check --fix check_filter tests

.PHONY: format
format: ## Format code with Black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(POETRY) run black check_filter tests
	$(POETRY) run isort check_filter tests

.PHONY: format-check
format-check: ## Check formatting without making changes
	@echo "$(BLUE)Checking code format...$(RESET)"
	$(POETRY) run black --check check_filter tests
	$(POETRY) run isort --check-only check_filter tests

.PHONY: type-check
type-check: ## Check types with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	$(POETRY) run mypy check_filter

# Run checks in order, including when invoked with make -j.
.PHONY: check
check: ## Check formatting, lint, types, and all tests in order
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	@echo "$(GREEN)All checks passed!$(RESET)"

# These optional helpers require a local .pre-commit-config.yaml.
.PHONY: pre-commit
pre-commit: ## Run all hooks (requires local configuration)
	@echo "$(BLUE)Running pre-commit hooks...$(RESET)"
	$(POETRY) run pre-commit run --all-files

.PHONY: pre-commit-install
pre-commit-install: ## Install hooks (requires local configuration)
	@echo "$(BLUE)Installing pre-commit hooks...$(RESET)"
	$(POETRY) run pre-commit install

##@ Documentation

# Retain the existing placeholder for compatibility; no generator is configured.
.PHONY: docs
docs: ## Report that documentation generation is not configured
	@echo "$(YELLOW)Documentation generation not configured yet$(RESET)"

##@ Release

# These opt-in helpers only change Poetry metadata, not the library version.
.PHONY: release-patch
release-patch: ## Bump the Poetry patch version
	@echo "$(BLUE)Bumping patch version...$(RESET)"
	$(POETRY) version patch

.PHONY: release-minor
release-minor: ## Bump the Poetry minor version
	@echo "$(BLUE)Bumping minor version...$(RESET)"
	$(POETRY) version minor

.PHONY: release-major
release-major: ## Bump the Poetry major version
	@echo "$(BLUE)Bumping major version...$(RESET)"
	$(POETRY) version major

##@ Cleanup

.PHONY: clean
clean: ## Remove build artifacts, reports, and project caches
	@echo "$(YELLOW)Cleaning build artifacts...$(RESET)"
	rm -rf dist build check_filter.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml junit.xml
	find check_filter tests -type d -name __pycache__ -exec rm -rf {} +
	find check_filter tests -type f -name "*.pyc" -delete
