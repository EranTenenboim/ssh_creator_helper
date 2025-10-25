.PHONY: help install test test-unit test-integration test-security lint format clean coverage docs

help: ## Show this help message
	@echo "SSH Creator Helper - Development Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements-test.txt

test: test-unit test-integration test-security ## Run all tests

test-unit: ## Run unit tests
	python -m pytest tests/ -v -m "not integration and not security"

test-integration: ## Run integration tests
	python -m pytest tests/ -v -m integration

test-security: ## Run security tests
	python -m pytest tests/ -v -m security

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	shellcheck ssh_auth_manager.sh

format: ## Format code
	black . --line-length 127
	isort .

coverage: ## Run tests with coverage
	python -m pytest tests/ --cov=ssh_auth_manager --cov-report=html --cov-report=term-missing

clean: ## Clean up generated files
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf tests/__pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs: ## Generate documentation
	@echo "Documentation is in README.md"

security-scan: ## Run security scan
	bandit -r . -f json -o bandit-report.json
	trivy fs .

shell-test: ## Test shell script
	bash -n ssh_auth_manager.sh
	shellcheck ssh_auth_manager.sh

ci-test: ## Run CI tests locally
	make lint
	make test
	make security-scan
	make shell-test

pre-commit: ## Run pre-commit checks
	make lint
	make test-unit
	make shell-test
