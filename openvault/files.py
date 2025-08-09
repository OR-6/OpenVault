# openvault/files.py
import os
import uuid
import datetime
import pyperclip
from openvault import config, encryption, utils, ui

def upload_file(vault, ui_module):
    """Upload a file to the secure locker. Try tkinter dialog first, fallback to manual path."""
    path = None
    # First try tkinter file dialog
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        # On some platforms you need to update the root to get dialogs to appear reliably
        root.update()
        path = filedialog.askopenfilename(title="Select file to encrypt")
        root.destroy()
    except Exception:
        path = None

    if not path:
        # Fallback: ask user to type path
        path = ui_module.ask("Enter full path to file (or leave blank to cancel)", default="")
        if not path:
            ui_module.console.print("[yellow]File upload canceled[/]")
            return

    if not os.path.exists(path):
        ui_module.console.print("[red]File not found[/]")
        return

    file_name = os.path.basename(path)
    category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    encrypted_file_name = f"{uuid.uuid4().hex}.enc"
    encrypted_path = os.path.join(config.LOCKER_DIR, encrypted_file_name)
    file_size = os.path.getsize(path)

    # Show a simple progress text while encrypting (progress callback optional)
    def progress_cb(percent):
        # percent is 0..100; we will render a minimal progress bar with carriage return
        try:
            ui_module.console.print(f"[blue]Encrypting {file_name}: {percent}%[/]", end="\r")
        except Exception:
            pass

    ok = encryption.VaultEncryption.encrypt_file(path, encrypted_path, vault.master_password, progress_callback=progress_cb)
    if ok:
        # record file metadata
        file_id = str(uuid.uuid4())
        ts = datetime.datetime.now().isoformat()
        vault.vault_data.setdefault("files", {})[file_id] = {
            "name": file_name,
            "size": file_size,
            "encrypted_name": encrypted_file_name,
            "category": category,
            "created": ts,
            "modified": ts
        }
        if vault.save_vault():
            ui_module.console.print(f"\n[green]File '{file_name}' encrypted and stored ({utils.format_size(file_size)})[/]")
    else:
        if os.path.exists(encrypted_path):
            try:
                os.remove(encrypted_path)
            except Exception:
                pass
        ui_module.console.print("[red]Failed to encrypt/store file[/]")

def view_files(vault, ui_module):
    files = vault.vault_data.get("files", {})
    if not files:
        ui_module.console.print("[yellow]No files stored[/]")
        return
    cat = ui_module.show_menu(["All"] + vault.vault_data["categories"], title="Filter by category")
    rows = []
    mapping = {}
    for i,(fid, info) in enumerate(files.items(), start=1):
        if cat != "All" and info["category"] != cat:
            continue
        rows.append([str(i), info["name"], utils.format_size(info["size"]), info["category"], utils.format_timestamp(info["created"])])
        mapping[str(i)] = fid
    ui_module.show_table("Stored Files", ["#","Name","Size","Category","Created"], rows)
    sel = ui_module.ask("Enter number to manage (blank to go back)", default="")
    if not sel:
        return
    fid = mapping.get(sel)
    if not fid:
        ui_module.console.print("[red]Invalid selection[/]")
        return
    view_file_details(vault, fid, ui_module)

def view_file_details(vault, file_id, ui_module):
    info = vault.vault_data["files"][file_id]
    ui_module.console.print(f"[bold]{info['name']}[/]")
    ui_module.console.print(f"Size: {utils.format_size(info['size'])}")
    ui_module.console.print(f"Category: {info['category']}")
    ui_module.console.print(f"Created: {utils.format_timestamp(info['created'])}")
    opts = ["Decrypt & Save", "Delete File", "Back"]
    choice = ui_module.show_menu(opts, title="File options")
    if choice == "Decrypt & Save":
        out_dir = ui_module.ask("Enter directory to save decrypted file", default=config.TEMP_DIR)
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception:
                ui_module.console.print("[red]Cannot create output directory[/]")
                return
        out_path = os.path.join(out_dir, info["name"])
        enc_path = os.path.join(config.LOCKER_DIR, info["encrypted_name"])
        def progress_cb(p):
            try:
                ui_module.console.print(f"[blue]Decrypting: {p}%[/]", end="\r")
            except Exception:
                pass
        ok = encryption.VaultEncryption.decrypt_file(enc_path, out_path, vault.master_password, progress_callback=progress_cb)
        if ok:
            ui_module.console.print(f"\n[green]Decrypted and saved to {out_path}[/]")
            if ui_module.confirm("Open file now?"):
                try:
                    import platform, subprocess
                    system = platform.system()
                    if system == "Windows":
                        os.startfile(out_path)
                    elif system == "Darwin":
                        subprocess.call(["open", out_path])
                    else:
                        subprocess.call(["xdg-open", out_path])
                except Exception as e:
                    ui_module.console.print(f"[red]Failed to open file: {e}[/]")
        else:
            ui_module.console.print("[red]Failed to decrypt file[/]")
    elif choice == "Delete File":
        if ui_module.confirm(f"Delete '{info['name']}'?"):
            enc_path = os.path.join(config.LOCKER_DIR, info["encrypted_name"])
            try:
                if os.path.exists(enc_path):
                    os.remove(enc_path)
            except Exception:
                pass
            del vault.vault_data["files"][file_id]
            if vault.save_vault():
                ui_module.console.print("[green]Deleted[/]")
