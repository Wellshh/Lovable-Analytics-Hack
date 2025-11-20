"""
Enhanced logging module using rich library for colored output and progress bars.
"""

import threading
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table

console = Console()

_log_lock = threading.Lock()

_thread_colors = [
    "cyan",
    "magenta",
    "blue",
    "yellow",
    "green",
    "red",
    "bright_cyan",
    "bright_magenta",
    "bright_blue",
    "bright_yellow",
    "bright_green",
    "bright_red",
]
_thread_registry: dict[int, dict[str, any]] = {}
_thread_counter = 0
_thread_counter_lock = threading.Lock()


def register_thread(thread_id: int) -> dict[str, any]:
    """Register a thread and assign it a color and number"""
    global _thread_counter
    with _thread_counter_lock:
        if thread_id not in _thread_registry:
            thread_num = _thread_counter
            _thread_counter += 1
            color = _thread_colors[thread_num % len(_thread_colors)]
            _thread_registry[thread_id] = {
                "number": thread_num + 1,
                "color": color,
                "thread_id": thread_id,
            }
        return _thread_registry[thread_id]


def get_thread_info(thread_id: int) -> dict[str, any]:
    """Get thread info, register if not exists"""
    return register_thread(thread_id)


def format_thread_prefix(thread_id: int) -> str:
    """Format thread prefix with color and number"""
    info = get_thread_info(thread_id)
    return f"[bold {info['color']}][T{info['number']}][/bold {info['color']}]"


class BotLogger:
    """Enhanced logger with rich formatting and thread-safe output"""

    def __init__(self, verbose: bool = False, thread_id: Optional[int] = None):
        self.verbose = verbose
        self.console = console
        self.thread_id = thread_id
        if thread_id is not None:
            register_thread(thread_id)

    def _print(self, message: str):
        """Thread-safe print with optional thread prefix"""
        with _log_lock:
            if self.thread_id is not None:
                prefix = format_thread_prefix(self.thread_id)
                self.console.print(f"{prefix} {message}")
            else:
                self.console.print(message)

    def info(self, message: str, style: str = "bold green", thread_id: Optional[int] = None):
        """Log info message"""
        thread_id = thread_id or self.thread_id
        if thread_id is not None:
            prefix = format_thread_prefix(thread_id)
            with _log_lock:
                self.console.print(f"{prefix} [{style}]i[/{style}] {message}")
        else:
            with _log_lock:
                self.console.print(f"[{style}]i[/{style}] {message}")

    def success(self, message: str, thread_id: Optional[int] = None):
        """Log success message"""
        thread_id = thread_id or self.thread_id
        if thread_id is not None:
            prefix = format_thread_prefix(thread_id)
            with _log_lock:
                self.console.print(f"{prefix} [bold green]✓[/bold green] {message}")
        else:
            with _log_lock:
                self.console.print(f"[bold green]✓[/bold green] {message}")

    def warning(self, message: str, thread_id: Optional[int] = None):
        """Log warning message"""
        thread_id = thread_id or self.thread_id
        if thread_id is not None:
            prefix = format_thread_prefix(thread_id)
            with _log_lock:
                self.console.print(f"{prefix} [bold yellow]⚠[/bold yellow] {message}")
        else:
            with _log_lock:
                self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def error(self, message: str, thread_id: Optional[int] = None):
        """Log error message"""
        thread_id = thread_id or self.thread_id
        if thread_id is not None:
            prefix = format_thread_prefix(thread_id)
            with _log_lock:
                self.console.print(f"{prefix} [bold red]✗[/bold red] {message}")
        else:
            with _log_lock:
                self.console.print(f"[bold red]✗[/bold red] {message}")

    def debug(self, message: str, thread_id: Optional[int] = None):
        """Log debug message (only if verbose)"""
        if self.verbose:
            thread_id = thread_id or self.thread_id
            if thread_id is not None:
                prefix = format_thread_prefix(thread_id)
                with _log_lock:
                    self.console.print(f"{prefix} [dim cyan]🐛[/dim cyan] {message}")
            else:
                with _log_lock:
                    self.console.print(f"[dim cyan]🐛[/dim cyan] {message}")

    def proxy_config(
        self,
        server: str,
        user: str,
        password_masked: str,
        thread_id: Optional[int] = None,
    ):
        """Log proxy configuration"""
        table = Table(title="Proxy Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Server", server)
        table.add_row("Username", user)
        table.add_row("Password", password_masked)

        with _log_lock:
            if thread_id is not None:
                prefix = format_thread_prefix(thread_id)
                self.console.print(f"{prefix}")
            self.console.print(table)

    def bot_start(self, url: str, threads: int = 1):
        """Log bot start"""
        panel = Panel(
            f"[bold cyan]Target URL:[/bold cyan] {url}\n"
            f"[bold cyan]Threads:[/bold cyan] {threads}",
            title="[bold green]🤖 Traffic Bot Starting[/bold green]",
            border_style="green",
        )
        self.console.print(panel)

    def form_submission(self, name: str, thread_id: int):
        """Log form submission"""
        prefix = format_thread_prefix(thread_id)
        with _log_lock:
            self.console.print(
                f"{prefix} [bold blue]📝[/bold blue] Submitting as [bold]{name}[/bold]"
            )

    def navigation(self, url: str, thread_id: Optional[int] = None):
        """Log navigation"""
        thread_id = thread_id or self.thread_id
        if thread_id is not None:
            prefix = format_thread_prefix(thread_id)
            with _log_lock:
                self.console.print(f"{prefix} [bold cyan]🌐[/bold cyan] Navigating to {url}")
        else:
            with _log_lock:
                self.console.print(f"[bold cyan]🌐[/bold cyan] Navigating to {url}")

    def page_loaded(self, thread_id: Optional[int] = None):
        """Log page loaded"""
        if self.verbose:
            thread_id = thread_id or self.thread_id
            if thread_id is not None:
                prefix = format_thread_prefix(thread_id)
                with _log_lock:
                    self.console.print(
                        f"{prefix} [dim green]✓[/dim green] Page loaded successfully"
                    )
            else:
                with _log_lock:
                    self.console.print("[dim green]✓[/dim green] Page loaded successfully")

    def bounce(self, thread_id: int):
        """Log bounce simulation"""
        prefix = format_thread_prefix(thread_id)
        with _log_lock:
            self.console.print(f"{prefix} [yellow]↩[/yellow] Simulating bounce")

    def screenshot(self, path: str, thread_id: Optional[int] = None):
        """Log screenshot saved"""
        thread_id = thread_id or self.thread_id
        if thread_id is not None:
            prefix = format_thread_prefix(thread_id)
            with _log_lock:
                self.console.print(f"{prefix} [green]📸[/green] Screenshot saved: {path}")
        else:
            with _log_lock:
                self.console.print(f"[green]📸[/green] Screenshot saved: {path}")

    def completion(self):
        """Log completion"""
        self.console.print(
            Panel(
                "[bold green]All bot instances completed successfully! 🎉[/bold green]",
                border_style="green",
            )
        )


def create_progress_bar(_description: str = "Processing") -> Progress:
    """
    Create a rich progress bar.

    Args:
        description: Description text for the progress bar

    Returns:
        Progress: Rich progress bar instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    )


def print_field_table(fields: list[dict]):
    """
    Print a formatted table of form fields.

    Args:
        fields: List of field dictionaries with keys like 'tag', 'type', 'name', 'id'
    """
    table = Table(
        title="[bold cyan]Discovered Form Fields[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Tag", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Name", style="green")
    table.add_column("ID", style="blue")
    table.add_column("Placeholder", style="magenta")

    for idx, field in enumerate(fields, 1):
        table.add_row(
            str(idx),
            field.get("tag", "N/A"),
            field.get("type", "N/A"),
            (
                field.get("name", "N/A")[:18] + ".."
                if len(field.get("name", "N/A")) > 20
                else field.get("name", "N/A")
            ),
            (
                field.get("id", "N/A")[:18] + ".."
                if len(field.get("id", "N/A")) > 20
                else field.get("id", "N/A")
            ),
            (
                field.get("placeholder", "N/A")[:28] + ".."
                if len(field.get("placeholder", "N/A")) > 30
                else field.get("placeholder", "N/A")
            ),
        )

    console.print(table)


def print_config_generated(_config: dict, path: str):
    """Print generated configuration"""
    console.print(
        Panel(
            f"[bold green]✓ Configuration file generated successfully![/bold green]\n\n"
            f"[bold cyan]Location:[/bold cyan] {Path(path).resolve()}",
            title="[bold]Configuration Generated[/bold]",
            border_style="green",
        )
    )


_logger: Optional[BotLogger] = None


def get_logger(verbose: bool = False, thread_id: Optional[int] = None) -> BotLogger:
    """Get or create a logger instance for a thread"""
    return BotLogger(verbose=verbose, thread_id=thread_id)
