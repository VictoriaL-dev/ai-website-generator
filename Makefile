run-dev: ## Start the FastAPI development server
	uv run fastapi dev src/main.py

lint: ## Check the code in the repository using linters
	uv run ruff check ./src

format: ## Run the auto-fixer and auto-formatter to clean up code
	uv run ruff check --fix ./src
	uv run ruff format ./src

list: ## Display a list of available commands and their descriptions
	@echo "List of available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
