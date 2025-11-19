import types

from restack_gen.commands.info import ListTemplatesCommand, TelemetryCommand


def test_list_templates_not_found(tmp_path, capsys):
    config = types.SimpleNamespace(lang=None)
    cmd = ListTemplatesCommand(config, templates_root=tmp_path / "no-templates")
    rc = cmd.execute([])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Templates directory not found" in captured.out


def test_list_templates_language_not_found(tmp_path, capsys):
    config = types.SimpleNamespace(lang=None)
    # Create templates dir without a 'py' subdir
    templates_root = tmp_path / "templates"
    templates_root.mkdir()
    cmd = ListTemplatesCommand(config, templates_root=templates_root)
    rc = cmd.execute([])
    assert rc == 0


def test_telemetry_show_toggle(monkeypatch, capsys):
    # Fake collector to avoid filesystem changes
    class FakeCollector:
        def __init__(self):
            self._enabled = False

        def is_enabled(self):
            return self._enabled

        def enable(self):
            self._enabled = True

        def disable(self):
            self._enabled = False

    fake = FakeCollector()
    monkeypatch.setattr("restack_gen.utils.telemetry.get_collector", lambda: fake)

    cmd = TelemetryCommand(types.SimpleNamespace())
    rc = cmd.execute([])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Telemetry is currently" in captured.out

    # Enable
    rc = cmd.execute(["enable"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Telemetry enabled" in captured.out
    assert fake.is_enabled()

    # Disable
    rc = cmd.execute(["disable"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Telemetry disabled" in captured.out
    assert not fake.is_enabled()


def test_telemetry_unknown(monkeypatch, capsys):
    fake = types.SimpleNamespace(is_enabled=lambda: False)
    monkeypatch.setattr("restack_gen.utils.telemetry.get_collector", lambda: fake)
    cmd = TelemetryCommand(types.SimpleNamespace())
    rc = cmd.execute(["bogus"])
    assert rc == 1
    captured = capsys.readouterr()
    assert "Unknown telemetry subcommand" in captured.out
