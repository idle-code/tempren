# Suggested Commands

## Setup
```bash
poetry install --all-extras       # Install all dependencies (including optional pymediainfo)
```

## Testing
```bash
poetry run pytest                  # Run all tests (coverage enabled by default)
poetry run pytest tests/path/to/test.py::TestClass::test_method  # Run single test
poetry run pytest -m "not e2e"     # Skip end-to-end tests
poetry run pytest -m "not slow"    # Skip slow tests
```

## Code Quality
```bash
poetry run mypy                    # Type checking (config in mypy.ini)
poetry run black tempren tests     # Format code (line length 88)
poetry run isort tempren tests     # Sort imports (compatible with black)
poetry run pylint tempren          # Linting
```

## Running
```bash
poetry run tempren                 # Run the CLI tool
```

## ANTLR Grammar
```bash
# Generate parser from grammar (in tempren/template/grammar/)
bash tempren/template/grammar/generate.sh
```

## System Utils
```bash
git, ls, cd, grep, find           # Standard Linux utils
```
