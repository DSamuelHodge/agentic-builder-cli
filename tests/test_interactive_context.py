from restack_gen.interactive.context import UserContext


def test_context_defaults(tmp_path, monkeypatch):
    p = tmp_path / "prefs.json"
    monkeypatch.setattr("restack_gen.interactive.context.UserContext.CONFIG_FILE", p)

    ctx = UserContext()
    assert ctx.get_default_language() is None

    ctx.update_from_result(type("R", (), {"language": "py", "package_manager": "uv"}))
    assert ctx.get_default_language() == "py"

    # Reload
    ctx2 = UserContext()
    assert ctx2.get_default_language() == "py"
