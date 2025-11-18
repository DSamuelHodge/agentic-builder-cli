# Interactive Mode — Checklist

This checklist tracks completed work and outstanding items for the interactive CLI feature.

## Completed ✅ (implemented & merged to feature branch `feature-interactive-mode`)
- [x] Entry point dispatcher: `restack_gen.__main__:main` that detects TTY & `-i/--interactive` and dispatches accordingly.
- [x] Minimal interactive CLI: `restack_gen/cli_interactive.py` provides a small wizard and uses `NewCommand` for project creation.
- [x] Interactive package scaffolding: `restack_gen/interactive/` with:
  - `prompts.py` — fallback to `input()` if `prompt_toolkit` unavailable
  - `session.py` — `InteractiveSession` and `PromptResult`
- [x] Tests added:
  - `tests/test_cli_interactive.py` — mock-based interactive tests
  - Dispatcher tests (as outlined in `instructions.md`) — `should_use_interactive_mode` behavior
- [x] Updated script entrypoint in `pyproject.toml` to `restack_gen.__main__:main` so the dispatcher runs from CLI script.
- [x] Basic cleanup in `NewCommand` flow remains unchanged; interactive mode re-uses `NewCommand` to avoid duplication.
- [x] Created docs & changelog:
  - `CHANGELOG.md`
  - `docs/interactive-mode.md` — detailed description, tests and future items.
- [x] Created and pushed branch `feature-interactive-mode` and committed the changes.

## Outstanding / Future work ❗ (not yet implemented)
- [ ] Full `prompt_toolkit` UX features
  - [ ] `restack_gen/interactive/theme.py` — color and styles
  - [ ] `restack_gen/interactive/completers.py` — auto-completion for language, template choices, package managers
  - [ ] `restack_gen/interactive/validators.py` — input validation (project names, paths)
  - [ ] Integrate `prompt_toolkit`-based UI elements into `prompts.py` for improved UX
- [ ] Templates & project presets
  - [ ] `restack_gen/interactive/templates.py` — template selection & defaults
  - [ ] Template-driven `InteractiveSession.start_with_template()` and CLI path `--template` support
- [ ] Context-aware defaults & persistence
  - [ ] `restack_gen/interactive/context.py` to store user defaults (`~/.config/restack-gen/preferences.json`)
  - [ ] Use context to prefill choices in the wizard
- [ ] Wizard & multi-step UI enhancements
  - [ ] Add `restack_gen/interactive/wizard.py` implementing multi-step flows and feature selection
  - [ ] Add `prompt_toolkit.shortcuts` interactions (checkbox lists, menus)
- [ ] Error handling & fallbacks
  - [ ] `restack_gen/interactive/fallback.py` to check terminal capabilities and advise fallback to standard CLI
  - [ ] `restack_gen/interactive/sanitize.py` to sanitize inputs
  - [ ] `restack_gen/interactive/signals.py` to handle SIGINT/SIGTERM gracefully
- [ ] Additional tests
  - [ ] E2E tests for full interactive session (`tests/e2e/test_interactive_flow.py`) mocking `prompt_toolkit.prompt`
  - [ ] Integration tests verifying created project structure for both `py` and `ts`
  - [ ] Performance tests for startup & import time
- [ ] Documentation & Release
  - [ ] README updated with interactive examples and `--interactive` usage
  - [ ] Add `help`/CLI docs changes to `src/restack_gen/commands/info.py` to include interactive section
  - [ ] Changelog bump and release notes
- [ ] CI / Automation
  - [ ] Add GitHub Actions to run unit tests and e2e tests on PRs
  - [ ] Add linting and style checks (ruff, black) enforced on PRs
- [ ] Telemetry & Metrics (optional, opt-in)
  - [ ] `utils/telemetry.py`, record summary metrics like usage count, mode used, and durations
  - [ ] Add configuration to opt-in/out of telemetry

## Next actionable recommendations
1. Implement `interactive/templates.py` and wire templates into `InteractiveSession` (medium priority).
2. Improve `prompts.py` with `prompt_toolkit` controls (auto-complete & validators) and add UX tests (high priority for interactive user experience).
3. Add `fallback.py`, `signals.py`, and `sanitize.py` to improve robustness and safety (high priority before broad public release).
4. Add CI workflows to run the test suite and e2e tests on PRs (high priority).

## Notes
- This checklist is a living record; move items to the "Completed ✅" section as they are implemented and pushed to `feature-interactive-mode`.
- The current implementation favors minimal dependency usage so the CLI remains usable in automation and CI.

---

`docs/checklist.md` — generated on 2025-11-18
