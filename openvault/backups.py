# openvault/backups.py
import os
import shutil
from openvault import ui, config
from typing import Optional
from datetime import datetime

def save_backup_for_vault(vault):
    """Open file dialog for saving a copy of the encrypted vault file."""
    if not vault.path or not os.path.exists(vault.path):
        ui.console.print("[red]Vault file missing[/]")
        return
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw(); root.update()
        
        default_name = f"{vault.vault_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.enc"
        dest = filedialog.asksaveasfilename(title="Save backup as", initialfile=default_name, defaultextension=".enc")
        root.destroy()
    except Exception:
        dest = ui.ask("Enter full path to save backup file (or blank to cancel)", default="")
        if not dest:
            ui.console.print("[yellow]Cancelled[/]")
            return
    try:
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(vault.path, dest)
        ui.console.print(f"[green]Backup saved to {dest}[/]")
    except Exception as e:
        ui.console.print(f"[red]Failed to save backup: {e}[/]")

def load_backup_for_vault(vault):
    """Let user pick a backup file to restore into the selected vault."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw(); root.update()
        src = filedialog.askopenfilename(title="Select backup file", filetypes=[("Encrypted vault","*.enc"),("All files","*.*")])
        root.destroy()
    except Exception:
        src = ui.ask("Enter path to backup file (or blank to cancel)", default="")
        if not src:
            ui.console.print("[yellow]Cancelled[/]")
            return
    if not os.path.exists(src):
        ui.console.print("[red]Backup file not found[/]")
        return
    try:
        shutil.copy2(src, vault.path)
        ui.console.print("[green]Backup restored (please unlock to verify)[/]")
    except Exception as e:
        ui.console.print(f"[red]Failed to restore backup: {e}[/]")
