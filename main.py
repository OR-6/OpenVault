# main.py (project root)
import os
from openvault import config, ui
from openvault.ui import console, show_menu, show_header, ask_password, about_panel
from openvault.vault import Vault
from openvault import passwords, twofa, files, notes
from openvault.utils import ClipboardManager

def ensure_dirs():
    os.makedirs(config.CONFIG_DIR, exist_ok=True)
    os.makedirs(config.LOCKER_DIR, exist_ok=True)
    os.makedirs(config.TEMP_DIR, exist_ok=True)

def main():
    ensure_dirs()
    vault = Vault()
    # Setup clipboard manager and attach to UI
    cm = ClipboardManager(clear_seconds=15, on_cleared=lambda: console.print("[dim]Clipboard cleared[/]"))
    ui.set_clipboard_manager(cm)

    # First-run setup
    if not os.path.exists(config.VAULT_FILE):
        show_header(f"{config.APP_NAME} - First time setup")
        vault.vault_data = vault.new_vault_structure()
        vault.set_master_password_interactive(ui.ask_password)
        if vault.save_vault():
            console.print("[green]Vault created![/]")

    while True:
        if vault.master_password is None:
            show_header(f"{config.APP_NAME} - Locked")
            choice = show_menu(["Unlock Vault", "Create New Vault", "About", "Exit"], title="Main")
            if choice == "Unlock Vault":
                pwd = ask_password("Enter your master password")
                if vault.load_vault(pwd):
                    console.print("[green]Unlocked[/]")
                else:
                    console.print("[red]Invalid password or vault error[/]")
            elif choice == "Create New Vault":
                if ui.confirm("This will overwrite existing vault if present. Continue?"):
                    vault.vault_data = vault.new_vault_structure()
                    vault.set_master_password_interactive(ui.ask_password)
                    vault.save_vault()
                    console.print("[green]New vault created[/]")
            elif choice == "About":
                console.print(ui.about_panel(config.APP_NAME, config.APP_VERSION, author="OR-6", repo="https://github.com/OR-6/OpenVault"))
            else:
                return
        else:
            show_header(f"{config.APP_NAME} - Unlocked")
            choice = show_menu([
                "Password Manager",
                "2FA Authenticator",
                "Secure File Locker",
                "Secure Notes",
                "About",
                "Lock Vault",
                "Exit"
            ], title="Main")

            if choice == "Password Manager":
                pm_choice = show_menu(["Add Password", "View Passwords", "Back"], title="Password Manager")
                if pm_choice == "Add Password":
                    passwords.add_password(vault, ui)
                elif pm_choice == "View Passwords":
                    passwords.view_passwords(vault, ui)

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

            elif choice == "About":
                console.print(ui.about_panel(config.APP_NAME, config.APP_VERSION, author="OR-6", repo="https://github.com/OR-6/OpenVault"))

            elif choice == "Lock Vault":
                vault.master_password = None
                vault.vault_data = None
                console.print("[yellow]Vault locked[/]")

            elif choice == "Exit":
                console.print("[green]Goodbye[/]")
                return

if __name__ == "__main__":
    main()
