"""ParallelPilot CLI – Día 1: esqueleto funcional."""
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
    script: str = typer.Argument(..., help="Script Python serial a paralelizar"),
    cores: int = typer.Option(None, "--cores", "-c", help="Núcleos a usar (por defecto todos)"),
    tolerance: float = typer.Option(1e-6, "--tolerance", "-t", help="Tolerancia numérica"),
    test_codex: bool = typer.Option(False, "--test-codex", help="Probar conexión con Codex y mostrar ID de sesión"),
):
    """ParallelPilot: paraleliza automáticamente código Python serial con Codex."""
    console.print(Panel.fit("[bold cyan]⚡ ParallelPilot[/bold cyan]", border_style="cyan"))

    if not os.path.isfile(script):
        console.print(f"[red]Error:[/red] el archivo '{script}' no existe.")
        raise typer.Exit(1)

    if test_codex:
        console.print("\n[bold yellow]Probando conexión a Codex...[/bold yellow]")
        session_id = test_codex_connection()
        if session_id:
            console.print(f"[green]✓ Conexión exitosa. ID de sesión:[/green] {session_id}")
        else:
            console.print("[red]✗ Falló la conexión.[/red]")
        raise typer.Exit()

    # El resto de la lógica se implementará en los días siguientes
    console.print(f"[dim]Script: {script} | cores: {cores} | tol: {tolerance}[/dim]")