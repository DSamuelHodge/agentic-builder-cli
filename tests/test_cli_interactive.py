from unittest.mock import patch, MagicMock
from restack_gen.cli_interactive import InteractiveCLI


@patch.object(InteractiveCLI, "_prompt", autospec=True)
def test_action_selection(mock_prompt):
    mock_prompt.return_value = "new"

    cli = InteractiveCLI([])
    # Use private method introspection
    action = cli._prompt("What would you like to do? (new/help/exit)", "new")

    assert action == "new"


@patch("restack_gen.interactive.InteractiveSession")
def test_new_project_flow(mock_session_class, tmp_path):
    # Setup mocks
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.project_name = "test-app"
    mock_result.language = "py"
    mock_result.package_manager = "uv"
    mock_result.init_git = True
    mock_result.include_docker = False
    mock_result.working_directory = None

    mock_session.start.return_value = mock_result
    mock_session_class.return_value = mock_session

    cli = InteractiveCLI(["--yes"])  # Auto-confirm
    # Use a temporary directory to avoid clashes
    cli.config.cwd = tmp_path

    with patch.object(cli, "_prompt", return_value="y"):
        with patch.object(cli, "_choose_language", return_value=None):
            exit_code = cli._handle_new()

    assert exit_code == 0
    mock_session.start.assert_called_once()
