import pytest
from restack_gen.interactive.validators import ProjectNameValidator


def test_project_name_validator_valid(monkeypatch):
    class Doc:
        def __init__(self, text):
            self.text = text

    v = ProjectNameValidator()
    v.validate(Doc("my-project"))
    v.validate(Doc("MyProject"))


def test_project_name_validator_invalid(monkeypatch):
    class Doc:
        def __init__(self, text):
            self.text = text

    v = ProjectNameValidator()
    with pytest.raises(Exception):
        v.validate(Doc("123-abc"))
    with pytest.raises(Exception):
        v.validate(Doc("has space"))
