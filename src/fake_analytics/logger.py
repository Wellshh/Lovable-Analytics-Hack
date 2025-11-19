"""
Enhanced logging module using rich library for colored output and progress bars.
"""

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

# Global console instance
console = Console()


class BotLogger:
    """Enhanced logger with rich formatting"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = console

    def info(self, message: str, style: str = "bold green"):
        """Log info message"""
        self.console.print(f"[{style}]i[/{style}] {message}")

    def success(self, message: str):
        """Log success message"""
        self.console.print(f"[bold green]✓[/bold green] {message}")

    def warning(self, message: str):
        """Log warning message"""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")

    def error(self, message: str):
        """Log error message"""
        self.console.print(f"[bold red]✗[/bold red] {message}")

    def debug(self, message: str):
        """Log debug message (only if verbose)"""
        if self.verbose:
            self.console.print(f"[dim cyan]🐛[/dim cyan] {message}")

    def proxy_config(self, server: str, user: str, password_masked: str):
        """Log proxy configuration"""
        table = Table(title="Proxy Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Server", server)
        table.add_row("Username", user)
        table.add_row("Password", password_masked)

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

    def form_submission(self, name: str, pid: int):
        """Log form submission"""
        self.console.print(
            f"[bold blue]📝[/bold blue] Thread {pid}: Submitting as [bold]{name}[/bold]"
        )

    def navigation(self, url: str):
        """Log navigation"""
        self.console.print(f"[bold cyan]🌐[/bold cyan] Navigating to {url}")

    def page_loaded(self):
        """Log page loaded"""
        if self.verbose:
            self.console.print("[dim green]✓[/dim green] Page loaded successfully")

    def bounce(self, pid: int):
        """Log bounce simulation"""
        self.console.print(f"[yellow]↩[/yellow] Thread {pid}: Simulating bounce")

    def screenshot(self, path: str):
        """Log screenshot saved"""
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


# Global logger instance
_logger: Optional[BotLogger] = None


def get_logger(verbose: bool = False) -> BotLogger:
    """Get or create the global logger instance"""
    global _logger
    if _logger is None or _logger.verbose != verbose:
        _logger = BotLogger(verbose)
    return _logger
