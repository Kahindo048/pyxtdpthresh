# Changelog

All notable changes are recorded here. The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Package skeleton in `src/` layout with the layered architecture and import-linter contracts.
- Layer-0 modules: global options, exception hierarchy with Stata return codes, French/English message catalogue, type aliases.
- Tooling: ruff, mypy (strict on the computational layers), pytest markers, coverage, pre-commit.
- Stata validation harness (`validation/`): PowerShell runner for Stata 17 MP.
