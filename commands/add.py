import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

REGISTRY_DIR = Path("/rose/registry")


def add(
    name: str = typer.Argument(..., help="Registry config name (e.g. fastapi, rag-milvus)"),
    target: Path = typer.Argument(
        Path("/project"),
        help="Target project directory",
        show_default=False,
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite if agent already exists"),
):
    """Add a registry config to the current project."""

    console.print()
    console.print(Panel(f"[bold magenta]rose add[/bold magenta] {name}", expand=False))

    src = REGISTRY_DIR / name / "agent.md"

    if not src.exists():
        available = sorted(p.parent.name for p in REGISTRY_DIR.glob("*/agent.md"))
        console.print(f"\n  [red]Error:[/red] '{name}' not found in registry.\n")
        if available:
            table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
            table.add_column("name", style="cyan")
            for a in available:
                table.add_row(a)
            console.print("  Available configs:\n")
            console.print(table)
        else:
            console.print("  Registry is empty.\n")
        raise typer.Exit(1)

    dst_dir = target / ".claude" / "agents"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / f"{name}.md"

    if dst.exists() and not force:
        console.print(f"\n  [yellow]~[/yellow] {dst.relative_to(target)} already exists — skipped (use --force to overwrite)\n")
        raise typer.Exit()

    shutil.copy(src, dst)

    results = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    results.add_column("status", style="bold", width=4)
    results.add_column("item")
    results.add_row("[green]✓[/green]", f".claude/agents/{name}.md")
    console.print()
    console.print(results)
    console.print(f"\n  [dim]Tailor [cyan].claude/agents/{name}.md[/cyan] to this project before using.[/dim]\n")
