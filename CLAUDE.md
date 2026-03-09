# CLAUDE.md

## Project Overview

Tempren is a template-based file renaming CLI tool written in Python. It uses a custom template language (compiled via ANTLR4) with a plugin-based tag system to generate new filenames from file metadata.

## Development Commands

```bash
poetry install --all-extras       # Install all dependencies (including optional pymediainfo)
poetry run pytest                  # Run all tests (coverage enabled by default)
poetry run pytest tests/path/to/test.py::TestClass::test_method  # Run single test
poetry run pytest -m "not e2e"     # Skip end-to-end tests
poetry run mypy                    # Type checking (config in mypy.ini)
poetry run black tempren tests     # Format code (line length 88)
poetry run isort tempren tests     # Sort imports (compatible with black)
```

Pre-commit hooks are installed (black, isort, trailing whitespace, ast check, etc.).

## Architecture

### Pipeline stages (tempren/pipeline.py)

gather files -> filter -> sort -> generate new names -> resolve conflicts -> rename

Key classes: `Pipeline`, `RuntimeConfiguration`, `OperationMode` (name/path/directory), `ConflictResolutionStrategy`.

### Tag system

- **Tag**: Abstract base in `tempren/primitives.py`. Method: `process(file, context) -> Any`.
- **TagFactory**: Creates Tag instances. `TagFactoryFromClass` in `tempren/factories.py` wraps classes.
- **TagRegistry** (`tempren/template/registry.py`): Maps qualified names (e.g., `image.width`) to factories.

### Tag discovery (tempren/discovery.py)

Classes in `tempren/tags/` are auto-discovered if they:
1. Subclass `Tag`
2. Are not abstract
3. Class name ends with `Tag`

Module name = category, class name minus `Tag` suffix = tag name. Example: `tempren/tags/image.py::WidthTag` -> `image.width`.

### Template grammar (tempren/template/grammar/)

ANTLR4 lexer/parser grammars: `TagTemplateLexer.g4`, `TagTemplateParser.g4`. **Do not edit generated `.py` files** in this directory. Template syntax uses `%TagName{context}(args)` with pipe `|` support.

### Other core abstractions

- **Pattern / PatternElement** (`tempren/template/ast.py`): Template AST nodes (RawText, TagInstance, TagPlaceholder).
- **PathGenerator** (`tempren/path_generator.py`): Generates new paths from templates.
- **File** (`tempren/primitives.py`): Dataclass with `input_directory` and `relative_path`.

## Testing

Tests mirror source structure under `tests/`. Tag tests in `tests/tags/`, template tests in `tests/template/`.

- **Markers**: `@pytest.mark.e2e` (subprocess tests), `@pytest.mark.slow` (timeout-dependent)
- **Test data**: `tests/test_data/` contains real media files; fixtures copy them to tmp dirs
- **E2E tests**: Run tempren as a subprocess

## Notes

- Optional dep `pymediainfo` requires system library `libmediainfo0v5`
- Entry point: `tempren.cli:throwing_main`
- Python >=3.10, mypy targets 3.10
