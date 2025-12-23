.PHONY: test test-unit test-integration run-example install

# Install dependencies
install:
	@echo "Installing dependencies..."
	python -m venv .venv
	@echo "To activate virtual environment:"
	@echo "  source .venv/bin/activate  # Linux/Mac"
	@echo "  .venv\\Scripts\\activate    # Windows"
	@echo ""
	@echo "Then run:"
	@echo "  pip install -r requirements.txt"

# Run all tests
test:
	@echo "Running all tests..."
	pytest -q

# Run only unit tests for Manus
test-unit:
	@echo "Running unit tests for Manus..."
	pytest tests/test_manus.py -q

# Run integration tests
test-integration:
	@echo "Running integration tests..."
	pytest tests/test_full_integration.py tests/test_simple.py -q

# Run example script
run-example:
	@echo "Running Manus example..."
	@python examples/manus_example.py

# Run tests with verbose output
test-verbose:
	@echo "Running tests with verbose output..."
	pytest -v

# Run specific test file
test-file:
	@echo "Usage: make test-file FILE=tests/test_manus.py"
	@echo "Running specific test file..."
	pytest $(FILE) -v

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf .venv
	rm -rf __pycache__
	rm -rf src/__pycache__
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -f .coverage
	rm -f *.pyc

# Show project structure
structure:
	@echo "Project structure:"
	@find . -type f -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.sh" | grep -v ".venv" | grep -v "__pycache__" | grep -v ".pytest_cache" | sort

# Show test coverage
coverage:
	@echo "Running tests with coverage..."
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Update requirements
requirements:
	@echo "Updating requirements..."
	pip freeze > requirements.txt

# Help
help:
	@echo "Available commands:"
	@echo "  make install        - Create virtual environment"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make run-example    - Run example script"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make coverage       - Run tests with coverage report"
	@echo "  make clean          - Clean up generated files"
	@echo "  make structure      - Show project structure"
	@echo "  make help           - Show this help"
