import os
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from codex_client import CodexSDKClient, CodexExecClient
from prompt_templates import PARALLELIZATION_PROMPT_TEMPLATE, FIX_PROMPT_TEMPLATE
from verifier import results_match
from executor import load_function, run_timed, run_with_cores
from reporter import BenchmarkPoint, render_speedup_chart, render_table, summarize_with_gpt56

load_dotenv()
app = typer.Typer()
console = Console()
MAX_RETRIES = 3


def get_codex_client(repo_dir: Path, model: str):
    console.print("[yellow]Using Codex CLI (subprocess) mode.[/yellow]")
    return CodexExecClient(repo_dir, model=model)


@app.command()
def main(
    script: str = typer.Argument(..., help="Serial script to parallelize"),
    function: str = typer.Option("compute", "--function", "-f"),
    cores: str = typer.Option("1,2,4,8", "--cores", "-c"),
    tolerance: float = typer.Option(1e-6, "--tolerance", "-t"),
    model: str = typer.Option("gpt-5.6-sol", "--model"),
    parallel_file: str = typer.Option(None, "--parallel-file", help="Use a pre-generated parallel file (skip Codex)"),
):
    """ParallelPilot: parallelize and validate serial Python code using Codex."""
    console.print(Panel.fit("[bold cyan]⚡ ParallelPilot[/bold cyan]", border_style="cyan"))
    script_path = Path(script).resolve()
    if not script_path.is_file():
        console.print(f"[red]Error:[/red] the file '{script}' does not exist.")
        raise typer.Exit(1)

    repo_dir = script_path.parent
    output_file = repo_dir / f"{script_path.stem}_parallel.py"
    parallel_fn_name = f"{function}_parallel"

    console.print("\n[bold]1/5[/bold] Running serial version...")
    serial_fn = load_function(script_path, function)
    serial_run = run_timed(serial_fn)
    if not serial_run.ok:
        console.print(f"[red]Failed:[/red]\n{serial_run.traceback}"); raise typer.Exit(1)
    console.print(f"   [green]✓[/green] {serial_run.elapsed_seconds:.4f}s")

    parallel_ok = False
    thread_note = "(not generated)"

    if parallel_file:
        parallel_path = Path(parallel_file).resolve()
        if not parallel_path.is_file():
            console.print(f"[red]Error:[/red] parallel file '{parallel_file}' does not exist.")
            raise typer.Exit(1)
        console.print(f"\n[bold]2/5[/bold] Using pre-generated parallel file: {parallel_path.name}")

        # Si el archivo proporcionado ya es el esperado, no copiamos
        if parallel_path.resolve() != output_file.resolve():
            import shutil
            shutil.copy2(parallel_path, output_file)
            console.print(f"   [dim]Copied to {output_file.name}[/dim]")
        else:
            console.print(f"   [dim]File already at expected location[/dim]")

        try:
            parallel_fn = load_function(output_file, parallel_fn_name)
            run = run_timed(parallel_fn, kwargs={"n_jobs": 1})
            if not run.ok:
                console.print(f"[red]Error in parallel file:[/red]\n{run.traceback}")
                raise typer.Exit(1)
            match, detail = results_match(serial_run.result, run.result, tolerance)
            if match:
                parallel_ok = True
                console.print(f"   [green]✓ Verification successful[/green] ({detail})")
            else:
                console.print(f"[red]✗ Verification failed:[/red] {detail}")
                raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Error loading parallel function:[/red] {e}")
            raise typer.Exit(1)
        thread_note = "pre-generated (Codex web)"
    else:
        console.print(f"\n[bold]2/5[/bold] Generating parallel version with Codex ({model})...")
        prompt = PARALLELIZATION_PROMPT_TEMPLATE.format(
            target_file=script_path.name, function_name=function, output_file=output_file.name)

        with get_codex_client(repo_dir, model) as codex:
            result = codex.start(prompt)
            console.print(f"   [dim]{result.final_response[:200]}[/dim]")

            parallel_ok, last_error, attempt = False, "", 1
            while attempt <= MAX_RETRIES:
                if not output_file.exists():
                    last_error = f"Codex did not create {output_file.name}"
                else:
                    try:
                        parallel_fn = load_function(output_file, parallel_fn_name)
                        run = run_timed(parallel_fn, kwargs={"n_jobs": 1})
                        if not run.ok:
                            last_error = f"Exception:\n{run.traceback}"
                        else:
                            match, detail = results_match(serial_run.result, run.result, tolerance)
                            if match:
                                parallel_ok = True
                                console.print(f"   [green]✓ Attempt {attempt}: correct[/green] ({detail})")
                                break
                            last_error = f"Does not match: {detail}"
                    except Exception as e:
                        last_error = f"Error loading: {e!r}"

                console.print(f"   [yellow]Attempt {attempt} failed:[/yellow] {last_error}")
                if attempt < MAX_RETRIES:
                    fix = FIX_PROMPT_TEMPLATE.format(output_file=output_file.name, function_name=function, error_detail=last_error)
                    result = codex.continue_with(fix)
                    console.print(f"   [dim]{result.final_response[:200]}[/dim]")
                attempt += 1
            thread_note = result.thread_id or "(no capturado)"

    if not parallel_ok:
        console.print(f"\n[red]No se pudo obtener una versión correcta.[/red]")
        raise typer.Exit(1)

    console.print("\n[bold]3/5[/bold] Measuring speedup...")
    core_list = [int(c.strip()) for c in cores.split(",")]
    parallel_fn = load_function(output_file, parallel_fn_name)
    points = []
    for n in core_list:
        run = run_with_cores(parallel_fn, n, args=())
        if run.ok:
            points.append(BenchmarkPoint(n, run.elapsed_seconds))
            console.print(f"   {n} cores: {run.elapsed_seconds:.4f}s")
        else:
            console.print(f"   [red]{n} cores failed:[/red] {run.error}")

    console.print("\n[bold]4/5[/bold] Report...")
    console.print(render_table(serial_run.elapsed_seconds, points))
    chart_path = repo_dir / "parallelpilot_speedup.png"
    render_speedup_chart(serial_run.elapsed_seconds, points, str(chart_path))
    console.print(f"   Chart: {chart_path}")

    console.print("\n[bold]5/5[/bold] Summary (GPT-5.6)...")
    summary = summarize_with_gpt56(serial_run.elapsed_seconds, points, parallel_ok)
    console.print(Panel(summary, title="Summary", border_style="cyan"))
    console.print(f"\n[dim]Technical thread ID: {thread_note}. For the Devpost ID, run /feedback in your interactive session.[/dim]")


if __name__ == "__main__":
    app()