import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

ROSE_REPO = "https://github.com/diogobaltazar/rose.git"


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def register(
    agent_path: Path = typer.Argument(..., help="Path to agent file, e.g. .claude/agents/rag.md"),
    name: str = typer.Option(None, "--name", "-n", help="Registry name (defaults to filename stem)"),
    target: Path = typer.Argument(
        Path("/project"),
        help="Project directory (used to resolve relative agent_path)",
        show_default=False,
    ),
):
    """Register a project agent into the rose registry via a GitHub PR."""

    # Resolve agent file
    resolved = agent_path if agent_path.is_absolute() else target / agent_path
    if not resolved.exists():
        console.print(f"\n  [red]Error:[/red] {resolved} not found.\n")
        raise typer.Exit(1)

    registry_name = name or resolved.stem

    console.print()
    console.print(Panel(
        f"[bold magenta]rose register[/bold magenta]\n\n"
        f"  Agent:    [cyan]{resolved}[/cyan]\n"
        f"  Registry: [cyan]{registry_name}[/cyan]",
        expand=False,
    ))

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        console.print("\n  [red]Error:[/red] GITHUB_TOKEN is not set.\n")
        console.print("  Pass it via the alias or export it before running rose.\n")
        raise typer.Exit(1)

    authed_repo = ROSE_REPO.replace("https://", f"https://diogobaltazar:{token}@")
    branch = f"registry/{registry_name}"

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        console.print("\n  [dim]Cloning rose repo...[/dim]")
        _run(["git", "clone", "--depth=1", authed_repo, "."], cwd=tmp_path)
        _run(["git", "config", "user.name", "diogobaltazar"], cwd=tmp_path)
        _run(["git", "config", "user.email", "d.ogobaltazar+github@gmail.com"], cwd=tmp_path)
        _run(["git", "checkout", "-b", branch], cwd=tmp_path)

        # Copy agent into registry
        dest = tmp_path / ".claude" / "registry" / registry_name / "agent.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(resolved, dest)

        _run(["git", "add", str(dest)], cwd=tmp_path)
        _run(["git", "commit", "-m", f"registry: add {registry_name} agent"], cwd=tmp_path)

        console.print("  [dim]Pushing branch...[/dim]")
        _run(["git", "push", "origin", branch], cwd=tmp_path)

        console.print("  [dim]Opening PR...[/dim]")
        pr = subprocess.run(
            [
                "gh", "pr", "create",
                "--repo", "diogobaltazar/rose",
                "--title", f"registry: add {registry_name}",
                "--body", f"Adds `{registry_name}` agent to the rose registry.\n\nSource: `{agent_path}`",
                "--head", branch,
                "--base", "main",
            ],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            env={**os.environ, "GH_TOKEN": token},
        )

    if pr.returncode == 0:
        url = pr.stdout.strip()
        console.print(Panel(
            f"[green]PR opened[/green]\n\n{url}",
            border_style="green",
            expand=False,
        ))
    else:
        console.print(f"\n  [red]Error opening PR:[/red] {pr.stderr.strip()}\n")
        raise typer.Exit(1)

    console.print()
