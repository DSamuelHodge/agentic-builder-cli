import pytest
from restack_gen.core.validation import Validator, ValidationError
from pathlib import Path


def test_validate_name_valid():
    assert Validator.validate_name("valid_name") == (True, "")
    assert Validator.validate_name("valid-name") == (True, "")
    assert Validator.validate_name("ValidName") == (True, "")


def test_validate_name_empty():
    assert Validator.validate_name("") == (False, "Name cannot be empty")


def test_validate_name_invalid_chars():
    assert Validator.validate_name("invalid@name") == (False, "'invalid@name' contains invalid characters")


def test_validate_name_starts_with_digit():
    assert Validator.validate_name("123bad") == (False, "Name cannot start with a digit")


def test_validate_name_starts_with_underscore():
    assert Validator.validate_name("_private") == (False, "Name should not start with underscore (convention)")


def test_validate_name_python_keyword():
    assert Validator.validate_name("class") == (False, "'class' is a Python keyword")
    assert Validator.validate_name("def") == (False, "'def' is a Python keyword")


def test_validate_name_kebab_allowed():
    # Kebab case should be allowed even if it contains keyword
    assert Validator.validate_name("class-name") == (True, "")


def test_validate_path_valid(tmp_path):
    assert Validator.validate_path(tmp_path) == (True, "")


def test_validate_path_must_exist(tmp_path):
    nonexistent = tmp_path / "missing"
    assert Validator.validate_path(nonexistent, must_exist=True) == (False, f"Path does not exist: {nonexistent}")


def test_validate_path_suspicious():
    suspicious = Path("../../../etc/passwd")
    assert Validator.validate_path(suspicious) == (False, "Path contains suspicious '..' components")
