from restack_gen.interactive.templates import TemplateSelector, TEMPLATES


def test_templates_list():
    selector = TemplateSelector()
    assert len(selector.templates) == len(TEMPLATES)


def test_template_selection_fallback(monkeypatch, tmp_path):
    # Simulate fallback by removing prompt_toolkit
    monkeypatch.setitem(__import__("sys").modules, "prompt_toolkit", None)
    selector = TemplateSelector()

    # Monkeypatch input to select the first template id
    first_id = list(selector.templates.keys())[0]
    monkeypatch.setattr("builtins.input", lambda prompt="": first_id)

    choice = selector.prompt_template()
    assert choice.id == first_id
