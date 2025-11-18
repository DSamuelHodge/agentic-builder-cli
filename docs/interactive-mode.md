# Interactive Mode (Feature)

This document describes the interactive mode implemented for `restack-gen` and explains the files added, modified, tests created, and design choices.

## Overview

Interactive mode offers a guided wizard for users to create a new project interactively. The dispatcher in `restack_gen.__main__` chooses between standard CLI and interactive mode based on command-line flags and TTY presence.

## Files Added

- `restack_gen/cli_interactive.py` — main interactive entry module that prompts users and dispatches commands.
- `restack_gen/interactive/__init__.py` — public exports for interactive utilities.
- `restack_gen/interactive/prompts.py` — prompt and fallback prompt functions, returns structured results.
- `restack_gen/interactive/session.py` — orchestrates a prompt wizard and returns a `PromptResult` dataclass.

## Files Modified

- `restack_gen/__main__.py` — now contains `should_use_interactive_mode()` and dispatch logic for interactive vs standard CLI.
- `pyproject.toml` — updated entrypoint to use `restack_gen.__main__:main` so the dispatcher is used when the `restack-gen` script is invoked.

## Summary of Behavior

- Mode detection (`restack_gen.__main__`):
  - `--interactive` or `-i` forces interactive mode.
  - No args + TTY = interactive mode (default if no args and running in a terminal).
  - `help`, `--help`, or standard commands (e.g., `new`) use the standard CLI.

- Interactive mode (`restack_gen/cli_interactive.py`):
  - Uses `prompt_toolkit` when installed; otherwise uses `input()` as a fallback.
  - Prompts for action (e.g. `new`) and collects data using `restack_gen.interactive` components.
  - Calls into `NewCommand` to create projects so logic stays shared and DRY.

## Tests Added & Results

- `tests/test_cli_interactive.py`:
  - Verifies interactive CLI selection logic and `NewCommand` flow with mocks to avoid filesystem changes.
  - Uses `tmp_path` fixture making tests safe to run.

All tests pass locally using `python -m pytest -q`.

## Notes & Design Choices

- The interactive feature is purposely minimal to minimize dependency changes and keep the CLI usable in CI and automation scripts.
- `prompt_toolkit` is optional — we only import and use it when present.
- The interactive session returns a `PromptResult` object for easy mapping to `Config` when calling into existing command code.
- Where possible, existing `NewCommand` is reused rather than cloning project generation logic.

## Future Enhancements

- Add `interactive/templates.py` and `interactive/context.py` to support templates & user preferences.
- Add `interactive/theme.py`, `validators.py`, `completers.py` to improve prompts and UX with `prompt_toolkit`.
- Expand test coverage for additional interactive behaviors and edge cases such as cancellations and non-TTY fallbacks.

---

If you want more details for any of these components or want to implement the advanced prompt UX, let me know and I will extend the interactive package next.