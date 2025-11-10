# Utility Functions Tests
from restack_gen.utils import text
from restack_gen.constants import Config, Language, GenerationType
from restack_gen.utils.toml import TOMLLoader


def test_snake_case():
    assert text.snake_case("MyTest") == "my_test"
    assert text.snake_case("myTestString") == "my_test_string"


def test_pascal_case():
    assert text.pascal_case("my_test") == "MyTest"
    assert text.pascal_case("another_example") == "AnotherExample"


def test_kebab_case():
    assert text.kebab_case("MyTest") == "my-test"
    assert text.kebab_case("myTestString") == "my_test_string".replace("_", "-")


# Config and Enums


def test_config_defaults():
    config = Config()
    assert config.lang is None
    assert config.quiet is False
    assert config.force is False


def test_language_enum():
    assert Language.PYTHON.value == "py"
    assert Language.TYPESCRIPT.value == "ts"


def test_generation_type_enum():
    assert GenerationType.AGENT.value == "agent"
    assert GenerationType.FUNCTION.value == "function"
    assert GenerationType.WORKFLOW.value == "workflow"


# TOML Handling


def test_toml_loader_is_available():
    assert isinstance(TOMLLoader.is_available(), bool)


# Add more tests for commands, integration, security, performance, etc.
# ...
