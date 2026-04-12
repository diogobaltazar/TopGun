from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from topgun.cli.observe import app

runner = CliRunner()


def test_watch_non_tty_prints_snapshot():
    """watch command must print a one-shot snapshot and exit cleanly when stdin is not a TTY.

    Without a TTY check, termios.tcgetattr raises termios.error: (25, 'Not a tty')
    when the command is run inside a Docker container or any non-interactive context.
    This test verifies that the command short-circuits before touching termios,
    calls scan_sessions and render_tabbed_view exactly once, and exits with code 0.
    Edge cases not covered: the full interactive TUI path (requires a real terminal),
    and the --web flag path (separate branch unrelated to TTY handling).
    """
    fake_sessions = [{"id": "test-session"}]
    fake_render   = MagicMock(return_value="snapshot output")

    with (
        patch("sys.stdin") as mock_stdin,
        patch("topgun.cli.observe.scan_sessions", return_value=fake_sessions) as mock_scan,
        patch("topgun.cli.observe.render_tabbed_view", return_value=fake_render()) as mock_render,
    ):
        mock_stdin.isatty.return_value = False
        result = runner.invoke(app, [])

    assert result.exit_code == 0
    mock_scan.assert_called_once()
    mock_render.assert_called_once_with(fake_sessions, 0)
