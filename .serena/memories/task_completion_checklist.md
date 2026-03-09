# Task Completion Checklist

When a coding task is completed, run the following checks:

1. **Format code**:
   ```bash
   poetry run black tempren tests
   poetry run isort tempren tests
   ```

2. **Type check**:
   ```bash
   poetry run mypy
   ```

3. **Run tests**:
   ```bash
   poetry run pytest
   ```
   - For quick feedback, run only relevant tests first:
     ```bash
     poetry run pytest tests/path/to/relevant_test.py
     ```

4. **Verify pre-commit hooks pass** (will run on commit):
   - trailing-whitespace, check-ast, end-of-file-fixer, check-added-large-files
   - check-merge-conflict, check-case-conflict, check-docstring-first
   - check-shebang-scripts-are-executable, check-yaml, check-toml, debug-statements
   - isort, black
