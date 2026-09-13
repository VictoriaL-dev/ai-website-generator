lint: ## Check the code in the repository using linters
	ruff check ./src

format: ## Run the auto-formatter
	ruff check --fix ./src

list: ## Display a list of available commands and their descriptions
	@echo "List of available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
