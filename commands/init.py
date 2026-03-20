import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

TEMPLATE_DIR = Path("/rose/template")
AGENTS_SRC = TEMPLATE_DIR / ".claude" / "agents"
CLAUDE_MD_SRC = TEMPLATE_DIR / "CLAUDE.md"


def init(
    target: Path = typer.Argument(
        Path("/project"),
        help="Target project directory",
        show_default=False,
    ),
):
    """Copy rose template into a project directory."""

    console.print()
    console.print(Panel("[bold magenta]rose init[/bold magenta]", expand=False))
    console.print(f"  Target: [cyan]{target}[/cyan]\n")

    results = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    results.add_column("status", style="bold", width=4)
    results.add_column("item")
    results.add_column("note", style="dim")

    # .claude/agents/
    agents_target = target / ".claude" / "agents"
    if agents_target.exists():
        results.add_row("~", ".claude/agents/", "already exists, skipped")
    else:
        agents_target.mkdir(parents=True)
        shutil.copytree(AGENTS_SRC, agents_target, dirs_exist_ok=True)
        results.add_row("[green]✓[/green]", ".claude/agents/", "auth, list-ui, rag")

    # CLAUDE.md
    claude_md = target / "CLAUDE.md"
    if claude_md.exists():
        results.add_row("~", "CLAUDE.md", "already exists, skipped")
    else:
        shutil.copy(CLAUDE_MD_SRC, claude_md)
        results.add_row("[green]✓[/green]", "CLAUDE.md", "")

    console.print(results)

    console.print(Panel(
        "[bold]Next steps[/bold]\n\n"
        "1. Edit [cyan]CLAUDE.md[/cyan] — fill in your stack and validation commands\n"
        "2. Edit [cyan].claude/agents/*.md[/cyan] — tailor each agent to this project\n"
        "3. Delete agents you don't need, add new ones for your components",
        border_style="dim",
        expand=False,
    ))
    console.print()
