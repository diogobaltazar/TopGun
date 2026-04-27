import importlib
import os
from pathlib import Path
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


def test_paths_derive_from_claude_dir(tmp_path, monkeypatch):
    """When CLAUDE_DIR is set all six path constants must be rooted there.

    The topgun Docker service sets CLAUDE_DIR=/claude but does not set the
    individual PROJECTS_DIR / SESSIONS_DIR / … vars. Before this fix, observe.py
    fell back to Path.home() / ".claude" / … which resolves to /root/.claude/…
    inside the container — a path that does not exist — so live sessions were
    never detected. This test verifies that a single CLAUDE_DIR env var is
    sufficient to make all paths resolve correctly.
    Edge cases not covered: interaction between CLAUDE_DIR and an explicitly-set
    SESSIONS_DIR (that combination still works via the inner os.environ.get).
    """
    import topgun.cli.observe as obs_module

    monkeypatch.setenv("CLAUDE_DIR", str(tmp_path))
    for var in ("PROJECTS_DIR", "SESSIONS_DIR", "TEAMS_DIR",
                "SUBAGENT_LOG", "MESSAGE_LOG", "OBSERVE_CONFIG"):
        monkeypatch.delenv(var, raising=False)

    importlib.reload(obs_module)

    assert obs_module.PROJECTS_DIR   == tmp_path / "projects"
    assert obs_module.SESSIONS_DIR   == tmp_path / "sessions"
    assert obs_module.TEAMS_DIR      == tmp_path / "teams"
    assert obs_module.SUBAGENT_LOG   == tmp_path / "logs" / "subagent-events.jsonl"
    assert obs_module.MESSAGE_LOG    == tmp_path / "logs" / "message-events.jsonl"
    assert obs_module.OBSERVE_CONFIG == tmp_path / "observe-config.json"


def test_paths_fall_back_to_home_dot_claude(monkeypatch):
    """When CLAUDE_DIR is not set paths fall back to ~/.claude/… with no regression.

    This guards against the fix accidentally breaking host (non-Docker) usage
    where neither CLAUDE_DIR nor the individual path vars are set.
    """
    import topgun.cli.observe as obs_module

    for var in ("CLAUDE_DIR", "PROJECTS_DIR", "SESSIONS_DIR", "TEAMS_DIR",
                "SUBAGENT_LOG", "MESSAGE_LOG", "OBSERVE_CONFIG"):
        monkeypatch.delenv(var, raising=False)

    importlib.reload(obs_module)

    base = Path.home() / ".claude"
    assert obs_module.PROJECTS_DIR   == base / "projects"
    assert obs_module.SESSIONS_DIR   == base / "sessions"
    assert obs_module.TEAMS_DIR      == base / "teams"
    assert obs_module.SUBAGENT_LOG   == base / "logs" / "subagent-events.jsonl"
    assert obs_module.MESSAGE_LOG    == base / "logs" / "message-events.jsonl"
    assert obs_module.OBSERVE_CONFIG == base / "observe-config.json"
