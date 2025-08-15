# openvault/settings.py
from openvault import utils, ui
from openvault import config
from typing import Dict
import os

def open_settings_menu(cfg: Dict):
    ui.console.print("[bold]Settings[/]")
    while True:
        opts = [
            f"Auto-update on startup: {'Enabled' if cfg.get('auto_update', True) else 'Disabled'}",
            f"Auto-lock timeout (seconds): {cfg.get('auto_lock_timeout', config.DEFAULT_TIMEOUT)}",
            f"Clipboard clear time (seconds): {cfg.get('clipboard_clear_time', config.DEFAULT_CLIP_CLEAR)}",
            f"Default backup path: {cfg.get('default_backup_path','(not set)')}",
            "Manage Vaults",
            "Back"
        ]
        choice = ui.show_menu(opts, title="Settings")
        if choice.startswith("Auto-update"):
            new = ui.confirm("Enable auto-update on startup?")
            cfg['auto_update'] = new
            utils.save_config(cfg)
            ui.console.print(f"[green]Auto-update {'enabled' if new else 'disabled'}[/]")
        elif choice.startswith("Auto-lock"):
            val = ui.ask("Enter auto-lock timeout in seconds", default=str(cfg.get('auto_lock_timeout', config.DEFAULT_TIMEOUT)))
            try:
                cfg['auto_lock_timeout'] = int(val)
                utils.save_config(cfg)
                ui.console.print("[green]Updated[/]")
            except Exception:
                ui.console.print("[red]Invalid value[/]")
        elif choice.startswith("Clipboard"):
            val = ui.ask("Enter clipboard clear time in seconds", default=str(cfg.get('clipboard_clear_time', config.DEFAULT_CLIP_CLEAR)))
            try:
                cfg['clipboard_clear_time'] = int(val)
                utils.save_config(cfg)
                ui.console.print("[green]Updated[/]")
            except Exception:
                ui.console.print("[red]Invalid value[/]")
        elif choice.startswith("Default backup"):
            path = ui.ask("Enter default backup directory path (leave blank to unset)", default=str(cfg.get('default_backup_path','')))
            cfg['default_backup_path'] = path
            utils.save_config(cfg)
            ui.console.print("[green]Updated[/]")
        elif choice == "Manage Vaults":
            manage_vaults(cfg)
        elif choice == "Back":
            break

def manage_vaults(cfg):
    ui.console.print("[bold]Manage Vaults[/]")
    while True:
        vaults = cfg.get("vaults", {})
        rows = []
        for i,(name,meta) in enumerate(vaults.items(), start=1):
            rows.append([str(i), meta.get("display_name", name), meta.get("path","")])
        ui.show_table("Configured vaults", ["#","Display name","Path"], rows)
        choice = ui.show_menu(["Add Vault", "Select Active Vault", "Delete Vault", "Back"], title="Vaults")
        if choice == "Add Vault":
            name = ui.ask("Internal vault name (no spaces, used as filename)")
            display = ui.ask("Display name", default=name)
            password = ui.ask("Set master password for this new vault", default="")
            if not name or not password:
                ui.console.print("[red]Name and password required[/]")
                continue
            from openvault.vault import Vault
            v = Vault(name)
            created = v.create_new(password)
            if created:
                cfg.setdefault("vaults", {})[name] = {"display_name": display, "path": v.path}
                cfg["active_vault"] = name
                utils.save_config(cfg)
                ui.console.print("[green]Vault created and selected[/]")
            else:
                ui.console.print("[red]Failed to create vault[/]")
        elif choice == "Select Active Vault":
            if not vaults:
                ui.console.print("[yellow]No vaults configured[/]")
                continue
            options = list(meta.get("display_name", n) for n,meta in vaults.items()) + ["Back"]
            sel = ui.show_menu(options, title="Select vault")
            if sel == "Back":
                continue
            
            names = list(vaults.keys())
            idx = options.index(sel)
            chosen_name = names[idx]
            cfg["active_vault"] = chosen_name
            utils.save_config(cfg)
            ui.console.print(f"[green]Active vault: {vaults[chosen_name].get('display_name')}[/]")
        elif choice == "Delete Vault":
            if not vaults:
                ui.console.print("[yellow]No vaults to delete[/]")
                continue
            options = list(meta.get("display_name", n) for n,meta in vaults.items()) + ["Back"]
            sel = ui.show_menu(options, title="Delete vault")
            if sel == "Back":
                continue
            names = list(vaults.keys())
            idx = options.index(sel)
            chosen = names[idx]
            if ui.confirm(f"Delete vault '{vaults[chosen]['display_name']}' permanently? This will remove the vault file."):
                try:
                    os.remove(vaults[chosen]['path'])
                except Exception:
                    pass
                del cfg['vaults'][chosen]
                if cfg.get('active_vault') == chosen:
                    cfg['active_vault'] = None
                utils.save_config(cfg)
                ui.console.print("[green]Deleted[/]")
        elif choice == "Back":
            break
