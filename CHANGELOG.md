# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-11-18
### Added
- Dual-mode CLI architecture: `restack-gen` now dispatches to either the standard CLI or interactive mode.
- Interactive mode entry: `restack_gen/cli_interactive.py` provides a guided wizard for project creation with minimal `prompt_toolkit` support and a fallback to `input()`.
- Interactive session package: `restack_gen/interactive/*` including `prompts.py` and `session.py` for modular interactive logic.
- Tests for interactive mode and dispatcher: `tests/test_cli_interactive.py` and mode detection tests (added by plan).

### Changed
- CLI entrypoint adjusted to dispatch to `restack_gen.__main__:main` through `pyproject.toml` to support mode selection.
- `restack_gen/__main__.py` updated as entrypoint dispatcher.

### Notes
- The interactive implementation is intentionally minimal to keep dependencies optional; we only use `prompt_toolkit` if available.
- The new interactive mode leverages the existing `NewCommand` to avoid duplicating project creation logic.

---

For detailed documentation and usage examples, see `docs/interactive-mode.md`.