# Jortype Project Context

Jortype is a Python tool for statistical text analysis and contextual OpenType glyph variation.

## Architecture

- `jortype.py`: Command-line entry point and pipeline.
- `analysis.py`: Text statistics and n-gram analysis.
- `context.py`: Letter-context analysis and distribution.
- `calt.py`: Contextual alternate analysis and rule generation.
- `opentype.py`: OpenType substitution generation.
- `config.py`: Configuration constants and glyph mappings.
- `report_writer.py`: Text, JSON and FEA output.
- `tests/`: Unit tests for the project's modules.

## Important Design Principles

- Keep statistical analysis separate from OpenType generation.
- The analysis model should remain usable independently.
- Context distribution is frequency-based, not sequential.
- Generated OpenType rules are deterministic.
- Triple-letter, double-letter and ordinary contexts are treated as distinct rule classes.

## Development Guidelines

Before modifying code:

1. Examine the relevant modules.
2. Identify dependencies and function call relationships.
3. Check how changes affect the complete pipeline.
4. Preserve existing functionality unless explicitly instructed otherwise.
5. Add or update tests when changing or introducing functionality.
6. Run the complete test suite after making changes.

Do not assume that a function is unused without searching the project.

Do not modify unrelated files.