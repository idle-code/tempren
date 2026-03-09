# Tempren - Project Overview

## Purpose
Tempren is a template-based file renaming CLI tool written in Python. It uses a custom template language (compiled via ANTLR4) with a plugin-based tag system to generate new filenames from file metadata.

## Tech Stack
- **Language**: Python >=3.9 (mypy targets 3.10)
- **Build/Dependency**: Poetry
- **Template Engine**: ANTLR4 (lexer/parser grammars in `tempren/template/grammar/`)
- **Testing**: pytest with pytest-cov
- **Formatting**: black (line length 88), isort (compatible with black)
- **Type Checking**: mypy
- **Linting**: pylint
- **Pre-commit**: hooks for black, isort, trailing whitespace, AST check, etc.
- **License**: GPL-3.0-or-later

## Key Dependencies
- antlr4-python3-runtime, mutagen (audio), Pillow/piexif (images), python-magic (MIME)
- pymediainfo (optional, for video - requires system lib `libmediainfo0v5`)
- geopy, fastkml, gpxpy (geo/GPS), pint (units), isodate, pathvalidate, Unidecode

## Entry Point
`tempren.cli:throwing_main` (installed as `tempren` command)

## Project Structure
```
tempren/
  cli.py              # CLI entry point and argument parsing
  pipeline.py         # Core pipeline: gather -> filter -> sort -> generate -> resolve -> rename
  primitives.py       # Core abstractions: File, Tag, TagFactory, Pattern, TagName, etc.
  factories.py        # TagFactoryFromClass wrapping Tag classes
  discovery.py        # Auto-discovers Tag subclasses in tempren/tags/
  evaluation.py       # Expression evaluation
  path_generator.py   # Generates new paths from templates
  file_filters.py     # File filtering logic
  file_sorters.py     # File sorting logic
  filesystem.py       # Filesystem operations
  exceptions.py       # Exception classes
  alias.py            # Tag aliasing
  adhoc.py            # Ad-hoc tag creation
  tags/               # Tag plugins (core, image, audio, video, text, hash, filesystem, geo, gpx)
  template/           # Template engine (AST, compiler, parser, registry, generators)
    grammar/          # ANTLR4 grammar files (DO NOT edit generated .py files)
tests/                # Mirror of source structure
  tags/               # Tag tests
  template/           # Template engine tests
  e2e/                # End-to-end tests (subprocess)
  test_data/          # Real media files for testing
```

## Tag Discovery Convention
Classes in `tempren/tags/` are auto-discovered if they:
1. Subclass `Tag`
2. Are not abstract
3. Class name ends with `Tag`
Module name = category, class name minus `Tag` suffix = tag name.
Example: `tempren/tags/image.py::WidthTag` -> `image.width`
