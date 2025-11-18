"""Validators for interactive prompts.

When prompt_toolkit is present we export classes that implement
`prompt_toolkit.validation.Validator`. In non-ptk environments these
are lightweight callables used in the test harness.
"""

from __future__ import annotations

import re

try:
    from prompt_toolkit.validation import Validator, ValidationError
    from prompt_toolkit.document import Document
except Exception:  # pragma: no cover
    Validator = object
    ValidationError = Exception


PROJECT_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*$")


class ProjectNameValidator(Validator):
    """Validate project names.

    Accepts letters, numbers, hyphens and underscores and must start with
    a letter or underscore.
    """

    def validate(self, document: "Document") -> None:  # type: ignore
        text = document.text
        if not text:
            raise ValidationError(message="Project name cannot be empty")
        if not PROJECT_NAME_RE.match(text):
            raise ValidationError(
                message="Invalid project name. Use letters, numbers, '-', or '_', and start with a letter."
            )


class PathValidator(Validator):
    def validate(self, document: "Document") -> None:  # type: ignore
        text = document.text
        # discourage NUL bytes
        if "\x00" in text:
            raise ValidationError(message="Invalid path")
