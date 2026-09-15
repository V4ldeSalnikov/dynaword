# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).

## [v0.1.0] - 2026-09-15

### Added

- The code that every Dynaword dataset repository carried in `src/dynaword`, as one installable package:
  `create.py` helpers, descriptive statistics, datasheet and README generation, plots, the Propella annotation
  schema and statistics, and the dataset test-suite (`dynaword.tests`).
- `dynaword.toml`: optional per-repository settings (`hub_id`, `reference_corpora`, `license_names`, `removed_sources`).
- `examples/`: the `pyproject.toml`, `makefile` and `dynaword.toml` a dataset repository needs.

### Changed

- The repository the tooling works on is the current working directory (or `DYNAWORD_REPO`) instead of the
  folder the code lives in.
- The corpus name comes from the README front matter; datasheets accept any language codes.
