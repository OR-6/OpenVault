# openvault/ui.py
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.align import Align
from rich.text import Text
from rich import box
from rich.prompt import Prompt, Confirm
from typing import List, Union, Optional
from .utils import ClipboardManager
from . import config
import shutil
import os

console = Console()

# Clipboard manager will be set from main
_clipboard_manager: Optional[ClipboardManager] = None

BANNER = r"""
                                                                               

 ██████╗ ██████╗ ███████╗███╗   ██╗    ██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
██╔═══██╗██╔══██╗██╔════╝████╗  ██║    ██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
██║   ██║██████╔╝█████╗  ██╔██╗ ██║    ██║   ██║███████║██║   ██║██║     ██║   
██║   ██║██╔═══╝ ██╔══╝  ██║╚██╗██║    ╚██╗ ██╔╝██╔══██║██║   ██║██║     ██║   
╚██████╔╝██║     ███████╗██║ ╚████║     ╚████╔╝ ██║  ██║╚██████╔╝███████╗██║   
 ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═══╝      ╚═══╝  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝   
                                                                               
"""

def set_clipboard_manager(cm: ClipboardManager):
    global _clipboard_manager
    _clipboard_manager = cm

def schedule_clipboard_clear():
    if _clipboard_manager:
        _clipboard_manager.schedule_clear()

def terminal_width():
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80

def show_header(title: str, subtitle: str = None):
    """Show a nice header with banner, title, and version footer."""
    console.rule("[bold blue]OpenVault[/bold blue]")

    banner_lines = BANNER.strip("\n").splitlines()
    banner_text = "\n".join(banner_lines)

    # Footer with version
    footer_text = f"[dim]Version {config.APP_VERSION}[/dim]"

    header_panel = Panel(
        Align.center(Text(banner_text, style="bold magenta")),
        title=f"[bold cyan]{title}[/] {f'- {subtitle}' if subtitle else ''}",
        subtitle=footer_text,
        subtitle_align="center",
        border_style="bright_blue",
        box=box.ROUNDED
    )
    console.print(header_panel)

def ask_password(prompt: str = "Password") -> str:
    return Prompt.ask(f"[bold]{prompt}[/]", password=True)

def ask(prompt: str, default: str = "") -> str:
    if default:
        return Prompt.ask(f"[cyan]{prompt}[/]", default=default)
    return Prompt.ask(f"[cyan]{prompt}[/]")

def confirm(prompt: str) -> bool:
    return Confirm.ask(f"[yellow]{prompt}[/]")

def show_menu(options: List[str], title: str = None, return_index: bool = False) -> Union[str,int]:
    """
    Enhanced menu:
     - shows a pretty numbered list
     - accepts number input
     - returns option text or index
    """
    if title:
        console.print(Panel(f"[bold]{title}[/]", box=box.SIMPLE, style="bright_black"))
    # Print options with numbers and alternating styles
    for i, opt in enumerate(options, 1):
        console.print(f"[bold green]{i}[/]. [white]{opt}[/]")
    while True:
        choice = Prompt.ask("[bold]Enter your choice[/]", default="1")
        if choice.strip() == "":
            # empty input -> treat as cancel/back if present
            if "Back" in options:
                idx = options.index("Back")
                return idx if return_index else options[idx]
            continue
        if not choice.isdigit():
            console.print("[red]Please enter a number[/]")
            continue
        idx = int(choice)
        if 1 <= idx <= len(options):
            return (idx - 1) if return_index else options[idx - 1]
        console.print("[red]Choice out of range[/]")

def show_table(title: str, columns: List[str], rows: List[List[str]]):
    """Pretty table with auto width handling."""
    table = Table(title=title, box=box.ROUNDED, show_lines=False)
    for col in columns:
        table.add_column(col, overflow="fold")
    for row in rows:
        table.add_row(*[str(x) for x in row])
    console.print(table)

def about_panel(app_name: str, version: str, author: str = "Unknown", repo: str = None):
    """Return an About panel text block."""
    lines = [
        f"[bold cyan]{app_name} v{version}[/]",
        "",
        "[dim]A secure open-source password manager, 2FA generator, and secure file locker.[/]",
        "",
        "[bold]Features:[/]",
        "• Password management with categories",
        "• TOTP / 2FA management with QR import & webcam scanning",
        "• Secure file encryption (Fernet/AES)",
        "• Encrypted notes & categories",
        "",
        f"[bold]Author:[/] {author}",
    ]
    if repo:
        lines.append(f"[bold blue]Repo:[/] {repo}")
    return Panel("\n".join(lines), title="About OpenVault", box=box.ROUNDED, border_style="magenta")
