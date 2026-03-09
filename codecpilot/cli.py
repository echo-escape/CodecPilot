import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from typing import Optional
from codecpilot.analyzer import analyze_video, FFprobeError

app = typer.Typer(help="CodecPilot: Smart CLI wrapper and encoding analysis tool for FFmpeg")
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """
    CodecPilot - 终端原生的智能 FFmpeg 包装器与编码分析工具
    """
    if ctx.invoked_subcommand is None:
        console.print("[bold blue]Welcome to CodecPilot![/bold blue]")
        console.print("Run [bold cyan]codecpilot --help[/bold cyan] for more info.")

@app.command()
def analyze(file: str = typer.Argument(..., help="Path to the video file to analyze")):
    """Analyze a video file and extract its metadata."""
    try:
        with console.status(f"Analyzing [bold cyan]{file}[/bold cyan]...", spinner="dots"):
            info = analyze_video(file)
            
        console.print(f"\n[bold green]Analysis Complete for:[/bold green] {info.format.filename}")
        
        # Format Table
        fmt_table = Table(title="[bold]Container & General Info[/bold]", show_header=True, header_style="bold magenta")
        fmt_table.add_column("Property", style="dim", width=20)
        fmt_table.add_column("Value")
        
        fmt_table.add_row("Format", info.format.format_long_name)
        fmt_table.add_row("Duration", f"{info.format.duration:.2f} seconds")
        fmt_table.add_row("Size", f"{info.format.size / (1024*1024):.2f} MB")
        if info.format.bit_rate:
            fmt_table.add_row("Overall Bitrate", f"{info.format.bit_rate / 1000:.0f} kbps")
            
        console.print(fmt_table)
        
        # Video Streams Table
        if info.video_streams:
            vi_table = Table(title="[bold]Video Streams[/bold]", show_header=True, header_style="bold cyan")
            vi_table.add_column("Index", style="dim", width=6)
            vi_table.add_column("Codec", width=12)
            vi_table.add_column("Resolution", width=12)
            vi_table.add_column("Pixel Format", width=15)
            vi_table.add_column("Color Space", width=15)
            vi_table.add_column("Bitrate", width=12)
            vi_table.add_column("FPS", width=10)
            
            for stream in info.video_streams:
                res = f"{stream.width}x{stream.height}"
                fps = stream.avg_frame_rate if stream.avg_frame_rate else "Unknown"
                if fps and '/' in fps:
                    num, den = map(int, fps.split('/'))
                    if den != 0:
                        fps = f"{num/den:.2f}"
                        
                bitrate = f"{int(stream.bit_rate)/1000:.0f} kbps" if stream.bit_rate else "N/A"
                
                vi_table.add_row(
                    str(stream.index),
                    str(stream.codec_name),
                    res,
                    str(stream.pix_fmt or "N/A"),
                    str(stream.color_space or "N/A"),
                    bitrate,
                    fps
                )
            console.print(vi_table)
            
        # Audio Streams Table
        if info.audio_streams:
            au_table = Table(title="[bold]Audio Streams[/bold]", show_header=True, header_style="bold yellow")
            au_table.add_column("Index", style="dim", width=6)
            au_table.add_column("Codec", width=12)
            au_table.add_column("Channels", width=10)
            au_table.add_column("Sample Rate", width=12)
            au_table.add_column("Bitrate", width=12)
            au_table.add_column("Language", width=10)
            
            for stream in info.audio_streams:
                bitrate = f"{int(stream.bit_rate)/1000:.0f} kbps" if stream.bit_rate else "N/A"
                lang = stream.language or "N/A"
                au_table.add_row(
                    str(stream.index),
                    str(stream.codec_name),
                    str(stream.channels or "N/A"),
                    f"{int(stream.sample_rate)} Hz" if stream.sample_rate else "N/A",
                    bitrate,
                    lang
                )
            console.print(au_table)
            
    except FFprobeError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")

@app.command()
def encode(
    file: str = typer.Argument(..., help="Path to the video file to encode"),
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Natural language description of your encoding goals"),
    profile: Optional[str] = typer.Option(None, "--profile", "-prof", help="Use a saved profile instead of generating a command"),
):
    """Generate and run an optimal FFmpeg encoding command based on a natural language prompt or profile."""
    from codecpilot.llm import LLMService
    from codecpilot.runner import run_ffmpeg_command, EncodingError
    from codecpilot.profiles import get_profile, save_profile
    import platform
    
    if not prompt and not profile:
        console.print("[bold red]Error:[/bold red] You must provide either --prompt or --profile.")
        raise typer.Exit(code=1)
        
    try:
        with console.status("Analyzing source video...", spinner="dots"):
            info = analyze_video(file)
            
        if profile:
            command_str = get_profile(profile)
            if not command_str:
                console.print(f"[bold red]Error:[/bold red] Profile '{profile}' not found.")
                raise typer.Exit(code=1)
        else:
            with console.status("Generating optimal FFmpeg command via AI...", spinner="arc"):
                llm = LLMService()
                command_str = llm.generate_encode_command(info, prompt)
            
        console.print(Panel(command_str, title="[bold green]Proposed FFmpeg Command[/bold green]", expand=False))
        
        command_str = Prompt.ask("\nEdit the command before execution", default=command_str)
        
        confirm = Confirm.ask("Do you want to execute this command now?")
        if not confirm:
            console.print("Operation canceled.")
            raise typer.Abort()
            
        with console.status("Encoding video...", spinner="bouncingBar"):
            run_ffmpeg_command(command_str)
            
        console.print("[bold green]Encoding Complete![/bold green]")
        
        if not profile:
            save_ans = Confirm.ask("Do you want to save this command as a profile?")
            if save_ans:
                prof_name = Prompt.ask("Enter a profile name")
                if save_profile(prof_name, command_str):
                    console.print(f"[green]Profile '{prof_name}' saved![/green]")
                else:
                    console.print("[red]Failed to save profile.[/red]")
            
    except FFprobeError as e:
        console.print(f"[bold red]Analysis Error:[/bold red] {e}")
    except ValueError as e:
         console.print(f"[bold red]Configuration Error:[/bold red] {e}")
    except EncodingError as e:
        console.print(f"\n[bold red]Encoding Failed![/bold red] {e.message}")
        console.print(f"Log saved to: [italic]{e.log_file}[/italic]")
        console.print("Run [cyan]codecpilot debug ffmpeg_error.log[/cyan] to analyze the error.")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")

@app.command()
def explain(
    param: str = typer.Argument(..., help="FFmpeg parameter to explain (e.g., b_pyramid)"),
):
    """Explain a complex FFmpeg parameter using AI."""
    from codecpilot.llm import LLMService
    
    try:
        console.print(f"[bold blue]Explanation of {param}[/bold blue]", justify="center")
        llm = LLMService()
        generator = llm.explain_parameter(param)
        
        content = ""
        with Live(Markdown(content), console=console, refresh_per_second=15) as live:
            for chunk in generator:
                content += chunk
                live.update(Markdown(content))
        
    except ValueError as e:
         console.print(f"[bold red]Configuration Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")

@app.command()
def debug(
    log_file: str = typer.Argument(..., help="Path to the FFmpeg error log file"),
):
    """Analyze an FFmpeg error log and provide troubleshooting suggestions."""
    from codecpilot.llm import LLMService
    import os
    
    if not os.path.exists(log_file):
         console.print(f"[bold red]Log file not found:[/bold red] {log_file}")
         raise typer.Exit(code=1)
         
    try:
        with open(log_file, "r") as f:
            log_content = f.read()
            
        console.print("[bold red]Error Analysis & Fixes[/bold red]", justify="center")
        llm = LLMService()
        generator = llm.debug_log(log_content)
        
        content = ""
        with Live(Markdown(content), console=console, refresh_per_second=15) as live:
            for chunk in generator:
                content += chunk
                live.update(Markdown(content))
        
    except ValueError as e:
         console.print(f"[bold red]Configuration Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
