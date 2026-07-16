"""ParallelPilot CLI - Day 1: functional skeleton."""
import os
import typer
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
from codex_client import test_codex_connection

load_dotenv()
app = typer.Typer()
console = Console()

@app.command()
def main(
    script: str = typer.Argument(..., help="Serial Python script to parallelize"),
    cores: int = typer.Option(None, "--cores", "-c", help="Cores to use (all by default)"),
    tolerance: float = typer.Option(1e-6, "--tolerance", "-t", help="Numeric tolerance"),
    test_codex: bool = typer.Option(False, "--test-codex", help="Test the Codex connection and show the session ID"),
):
    """ParallelPilot: automatically parallelize serial Python code with Codex."""
    console.print(Panel.fit("[bold cyan]⚡ ParallelPilot[/bold cyan]", border_style="cyan"))

    if not os.path.isfile(script):
        console.print(f"[red]Error:[/red] the file '{script}' does not exist.")
        raise typer.Exit(1)

    if test_codex:
        console.print("\n[bold yellow]Testing Codex connection...[/bold yellow]")
        session_id = test_codex_connection()
        if session_id:
            console.print(f"[green]✓ Connection successful. Session ID:[/green] {session_id}")
        else:
            console.print("[red]✗ Connection failed.[/red]")
        raise typer.Exit()

    console.print(f"[dim]Script: {script} | cores: {cores} | tol: {tolerance}[/dim]")
    

if __name__ == "__main__":
    app()