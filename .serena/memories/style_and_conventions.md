# Code Style and Conventions

## Formatting
- **black** with line length 88 (default)
- **isort** with multi_line_output=3, trailing comma, line length 88

## Naming
- Classes: PascalCase (e.g., `CountTag`, `TagFactory`, `PathGenerator`)
- Functions/methods: snake_case (e.g., `process`, `configure`, `from_path`)
- Tag classes: Must end with `Tag` suffix (e.g., `CountTag`, `WidthTag`)
- Private methods: prefixed with underscore (e.g., `_get_counter_value_for`)
- Variables: snake_case

## Type Hints
- Used throughout the codebase
- mypy configured for Python 3.10 target
- `typing` module used for `Optional`, `Union`, `Any`, etc.
- ANTLR4 generated grammar files are excluded from mypy checks

## Docstrings
- Used on Tag.configure() methods to document parameters
- Uses `:param name: description` format (parsed by docstring-parser)
- Not required on every method

## Testing Conventions
- Tests mirror source structure under `tests/`
- Test classes named `TestXxx` (e.g., `TestCountTag`)
- Test methods named `test_descriptive_name` with snake_case
- Follows arrange-act-assert pattern with blank lines between sections
- Fixtures used for test data (e.g., `nonexistent_file: File`)
- Markers: `@pytest.mark.e2e`, `@pytest.mark.slow`
- Test data in `tests/test_data/`

## Design Patterns
- Abstract base classes (ABC) for interfaces (Tag, TagFactory, Pattern, PathGenerator)
- Dataclasses for data containers (File, QualifiedTagName, Location)
- Plugin discovery pattern for tags
- Template pattern: `%TagName{context}(args)` with pipe `|` support

## Important Notes
- DO NOT edit generated `.py` files in `tempren/template/grammar/`
- coverage excludes: grammar files, `raise NotImplementedError`, `assert`, `__repr__`, `pass`
