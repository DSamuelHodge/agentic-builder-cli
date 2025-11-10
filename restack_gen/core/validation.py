# restack-gen 0.1.0
# Date: 2025-11-10
# Timestamp: 2025-11-10T10:38:06.925606
from pathlib import Path
import keyword


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


class Validator:
    """Validates user input."""

    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """Validate identifier name. Returns (is_valid, error_message)."""
        if not name:
            return False, "Name cannot be empty"
        name_check = name.replace("-", "_")
        if not name_check.replace("_", "").isalnum():
            return False, f"'{name}' contains invalid characters"
        if name[0].isdigit():
            return False, "Name cannot start with a digit"
        if name.startswith("_"):
            return False, "Name should not start with underscore (convention)"
        if "-" not in name and keyword.iskeyword(name):
            return False, f"'{name}' is a Python keyword"
        return True, ""

    @staticmethod
    def validate_path(path: Path, must_exist: bool = False) -> tuple[bool, str]:
        """Validate path. Returns (is_valid, error_message)."""
        try:
            resolved = path.resolve()
            if must_exist and not resolved.exists():
                return False, f"Path does not exist: {path}"
            if ".." in str(path):
                return False, "Path contains suspicious '..' components"
            return True, ""
        except Exception as e:
            return False, f"Invalid path: {e}"
