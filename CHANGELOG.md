# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-11-18
### Added
- Dual-mode CLI architecture: `restack-gen` now dispatches to either the standard CLI or interactive mode.
- Interactive mode entry: `restack_gen/cli_interactive.py` provides a guided wizard for project creation with minimal `prompt_toolkit` support and a fallback to `input()`.
- Interactive session package: `restack_gen/interactive/*` including `prompts.py` and `session.py` for modular interactive logic.
- Tests for interactive mode and dispatcher: `tests/test_cli_interactive.py` and mode detection tests (added by plan).
- Enhanced interactive UX with full `prompt_toolkit` integration:
  - `theme.py`: Color schemes and styling for prompts.
  - `completers.py`: Auto-completion for language, template, and package manager choices.
  - `validators.py`: Input validation for project names, paths, and other fields.
- Templates and project presets:
  - `templates.py`: Template selection and default configurations.
  - Support for template-driven sessions and CLI `--template` flag.
- Context-aware defaults and persistence:
  - `context.py`: Stores user preferences in `~/.config/restack-gen/preferences.json`.
  - Prefills wizard choices based on user context.
- Wizard and multi-step UI enhancements:
  - `wizard.py`: Implements multi-step flows and feature selection.
  - Integration with `prompt_toolkit.shortcuts` for checkboxes and menus.
- Error handling and fallbacks:
  - `fallback.py`: Checks terminal capabilities and advises fallback to standard CLI.
  - `sanitize.py`: Sanitizes user inputs.
  - `signals.py`: Handles SIGINT/SIGTERM gracefully.
- Cache and telemetry:
  - `cache.py`: Caches interactive session data.
  - `telemetry.py`: Basic telemetry for usage analytics.
- Additional unit tests: `tests/test_interactive_*.py` for validators, templates, context, fallback, and wizard.

### Changed
- CLI entrypoint adjusted to dispatch to `restack_gen.__main__:main` through `pyproject.toml` to support mode selection.
- `restack_gen/__main__.py` updated as entrypoint dispatcher.

### Fixed
- Test issues in `test_interactive_fallback.py` resolved with proper monkeypatch for importlib.util.find_spec.

### Notes
- The interactive implementation is intentionally minimal to keep dependencies optional; we only use `prompt_toolkit` if available.
- The new interactive mode leverages the existing `NewCommand` to avoid duplicating project creation logic.

---

For detailed documentation and usage examples, see `docs/interactive-mode.md`.