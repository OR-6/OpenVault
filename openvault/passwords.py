# openvault/passwords.py
import uuid
import datetime
import pyperclip
from typing import Dict
from openvault import utils
from openvault import ui

def add_password(vault, ui_module):
    name = ui_module.ask("Enter a name for this password")
    username = ui_module.ask("Enter username/email")
    password = ui_module.ask("Enter password")
    url = ui_module.ask("Enter website URL (optional)", default="")
    notes = ui_module.ask("Enter notes (optional)", default="")
    category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    entry_id = str(uuid.uuid4())
    ts = datetime.datetime.now().isoformat()
    vault.vault_data["passwords"][entry_id] = {
        "name": name, "username": username, "password": password,
        "url": url, "notes": notes, "category": category,
        "created": ts, "modified": ts
    }
    if vault.save_vault():
        ui_module.console.print(f"[green]Password '{name}' added[/]")

def view_passwords(vault, ui_module):
    if not vault.vault_data["passwords"]:
        ui_module.console.print("[yellow]No passwords saved yet[/]")
        return
    # Allow category filter
    cat = ui_module.show_menu(["All"] + vault.vault_data["categories"], title="Filter by category")
    rows = []
    mapping = {}
    for i, (eid, entry) in enumerate(vault.vault_data["passwords"].items(), start=1):
        if cat != "All" and entry["category"] != cat:
            continue
        rows.append([str(i), entry["name"], entry["username"], entry["category"]])
        mapping[str(i)] = eid
    if not rows:
        ui_module.console.print("[yellow]No entries for that category[/]")
        return
    ui_module.show_table("Saved Passwords", ["#", "Name", "Username", "Category"], rows)
    sel = ui_module.ask("Enter number to view details (or blank to go back)", default="")
    if not sel:
        return
    eid = mapping.get(sel)
    if not eid:
        ui_module.console.print("[red]Invalid selection[/]")
        return
    view_password_details(vault, eid, ui_module)

def view_password_details(vault, entry_id, ui_module):
    entry = vault.vault_data["passwords"][entry_id]
    ui_module.console.print(f"[bold cyan]{entry['name']}[/]")
    ui_module.console.print(f"Username: [green]{entry['username']}[/]")
    ui_module.console.print(f"URL: [blue]{entry['url'] or '-'}[/]")
    ui_module.console.print(f"Category: {entry['category']}")
    ui_module.console.print(f"Notes: {entry['notes'] or '-'}")
    ui_module.console.print(f"Created: {utils.format_timestamp(entry['created'])}")
    ui_module.console.print(f"Modified: {utils.format_timestamp(entry['modified'])}")
    opts = ["Show Password", "Copy Password", "Copy Username", "Edit Entry", "Delete Entry", "Back"]
    choice = ui_module.show_menu(opts, title="Password options")
    if choice == "Show Password":
        ui_module.console.print(f"[bold yellow]Password:[/] {entry['password']}")
    elif choice == "Copy Password":
        pyperclip.copy(entry['password'])
        ui_module.console.print("[green]Password copied to clipboard[/]")
        ui_module.schedule_clipboard_clear()
    elif choice == "Copy Username":
        pyperclip.copy(entry['username'])
        ui_module.console.print("[green]Username copied to clipboard[/]")
        ui_module.schedule_clipboard_clear()
    elif choice == "Edit Entry":
        edit_password(vault, entry_id, ui_module)
    elif choice == "Delete Entry":
        delete_password(vault, entry_id, ui_module)

def edit_password(vault, entry_id, ui_module):
    entry = vault.vault_data["passwords"][entry_id]
    ui_module.console.print("[dim]Press Enter to keep current value[/]")
    name = ui_module.ask("Name", default=entry['name'])
    username = ui_module.ask("Username/Email", default=entry['username'])
    if ui_module.confirm("Change password?"):
        password = ui_module.ask("New password")
    else:
        password = entry['password']
    url = ui_module.ask("URL", default=entry['url'])
    notes = ui_module.ask("Notes", default=entry['notes'])
    if ui_module.confirm("Change category?"):
        category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    else:
        category = entry['category']
    entry.update({
        "name": name,
        "username": username,
        "password": password,
        "url": url,
        "notes": notes,
        "category": category,
        "modified": datetime.datetime.now().isoformat()
    })
    if vault.save_vault():
        ui_module.console.print("[green]Entry updated[/]")

def delete_password(vault, entry_id, ui_module):
    entry = vault.vault_data["passwords"][entry_id]
    if ui_module.confirm(f"Delete '{entry['name']}'?"):
        del vault.vault_data["passwords"][entry_id]
        if vault.save_vault():
            ui_module.console.print("[green]Deleted[/]")
