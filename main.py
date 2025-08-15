# main.py
import os
from openvault import config, ui
from openvault.ui import console, show_menu, show_header, ask_password
from openvault.vault import Vault
from openvault import passwords, twofa, files, notes, settings, updater, backups
from openvault.utils import load_config, save_config, ClipboardManager

def ensure_dirs():
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    os.makedirs(config.VAULTS_DIR, exist_ok=True)
    os.makedirs(config.LOCKER_DIR, exist_ok=True)
    os.makedirs(config.TEMP_DIR, exist_ok=True)
    os.makedirs(config.BACKUPS_DIR, exist_ok=True)

def startup_update_check(cfg):
    
    if not cfg.get('auto_update', True):
        return
    console.print("[dim]Checking for updates...[/]")
    checked, applied, msg = updater.run_update_check(os.getcwd(), cfg, auto_apply=True)
    if checked and applied:
        console.print(f"[green]{msg}[/]")
        console.print("[yellow]Please restart the application to apply changes.[/]")
    elif checked:
        console.print(f"[cyan]{msg}[/]")
    else:
        console.print(f"[red]{msg}[/]")

def load_active_vault(cfg):
    name = cfg.get("active_vault")
    if not name:
        return None
    meta = cfg.get("vaults", {}).get(name)
    if not meta:
        return None
    v = Vault(name)
    v.path = meta.get("path") or v.path
    return v

def main():
    ensure_dirs()
    cfg = load_config()
    
    cm = ClipboardManager(clear_seconds=cfg.get("clipboard_clear_time", config.DEFAULT_CLIP_CLEAR), on_cleared=lambda: console.print("[dim]Clipboard cleared[/]"))
    ui.set_clipboard_manager(cm)

    
    startup_update_check(cfg)

    
    while True:
        active_vault = load_active_vault(cfg)
        if not active_vault:
            show_header(f"{config.APP_NAME} - No vault selected")
            choice = show_menu(["Create Vault", "Settings", "About", "Exit"], title="Startup")
            if choice == "Create Vault":
                from openvault.vault import Vault
                name = ui.ask("Internal vault name (no spaces)")
                display = ui.ask("Display name", default=name)
                password = ui.ask("Set master password")
                if not name or not password:
                    console.print("[red]Name and password required[/]")
                    continue
                v = Vault(name)
                if v.create_new(password):
                    cfg.setdefault("vaults", {})[name] = {"display_name": display, "path": v.path}
                    cfg['active_vault'] = name
                    save_config(cfg)
                    console.print("[green]Vault created and selected[/]")
                    active_vault = v
                    break
                else:
                    console.print("[red]Failed to create vault[/]")
            elif choice == "Settings":
                settings.open_settings_menu(cfg)
            elif choice == "About":
                console.print(ui.about_panel(config.APP_NAME, config.APP_VERSION, author="OR-6", repo=f"https://github.com/{config.GITHUB_REPO}"))
            else:
                return
        else:
            break

    vault = active_vault

    
    while True:
        show_header(f"{config.APP_NAME} - Locked", subtitle=vault.vault_name)
        pwd = ask_password("Enter your master password (or blank to exit)")
        if not pwd:
            return
        if vault.load(pwd):
            console.print("[green]Vault unlocked[/]")
            break
        else:
            console.print("[red]Invalid password[/]")

    
    while True:
        show_header(f"{config.APP_NAME} - Unlocked", subtitle=vault.vault_name)
        choice = show_menu([
            "Password Manager",
            "2FA Authenticator",
            "Secure File Locker",
            "Secure Notes",
            "Backups",
            "Settings",
            "About",
            "Lock Vault",
            "Exit"
        ], title="Main")
        if choice == "Password Manager":
            pm_choice = show_menu(["Add Password", "View Passwords", "Search Passwords", "Back"], title="Password Manager")
            if pm_choice == "Add Password":
                passwords.add_password(vault, ui)
            elif pm_choice == "View Passwords":
                passwords.view_passwords(vault, ui)
            elif pm_choice == "Search Passwords":
                passwords.search_passwords(vault, ui)
        elif choice == "2FA Authenticator":
            tf_choice = show_menu(["Add 2FA", "View 2FA", "Back"], title="2FA Authenticator")
            if tf_choice == "Add 2FA":
                twofa.add_twofa(vault, ui)
            elif tf_choice == "View 2FA":
                twofa.view_twofa(vault, ui)
        elif choice == "Secure File Locker":
            fl = show_menu(["Upload File", "View Files", "Back"], title="Secure File Locker")
            if fl == "Upload File":
                files.upload_file(vault, ui)
            elif fl == "View Files":
                files.view_files(vault, ui)
        elif choice == "Secure Notes":
            nn = show_menu(["Add Note", "View Notes", "Back"], title="Secure Notes")
            if nn == "Add Note":
                notes.add_note(vault, ui)
            elif nn == "View Notes":
                notes.view_notes(vault, ui)
        elif choice == "Backups":
            b_choice = show_menu(["Save Backup", "Load Backup", "Back"], title="Backups")
            if b_choice == "Save Backup":
                backups.save_backup_for_vault(vault)
            elif b_choice == "Load Backup":
                backups.load_backup_for_vault(vault)
        elif choice == "Settings":
            settings.open_settings_menu(cfg)
        elif choice == "About":
            console.print(ui.about_panel(config.APP_NAME, config.APP_VERSION, author="OR-6", repo=f"https://github.com/{config.GITHUB_REPO}"))
        elif choice == "Lock Vault":
            vault.master_password = None
            vault.vault_data = None
            console.print("[yellow]Vault locked[/]")
            
            while True:
                show_header(f"{config.APP_NAME} - Locked", subtitle=vault.vault_name)
                pwd = ask_password("Enter your master password (or blank to exit)")
                if not pwd:
                    return
                if vault.load(pwd):
                    console.print("[green]Vault unlocked[/]")
                    break
                else:
                    console.print("[red]Invalid password[/]")
        elif choice == "Exit":
            console.print("[green]Goodbye[/]")
            return

if __name__ == "__main__":
    main()
