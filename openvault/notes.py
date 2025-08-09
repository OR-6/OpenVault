# openvault/notes.py
import uuid
import datetime
from openvault import ui, utils

def add_note(vault, ui_module):
    title = ui_module.ask("Enter note title")
    ui_module.console.print("[yellow]Enter note content (end with a blank line):[/]")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        lines.append(line)
    content = "\n".join(lines)
    category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    nid = str(uuid.uuid4())
    ts = datetime.datetime.now().isoformat()
    vault.vault_data["notes"][nid] = {
        "title": title, "content": content, "category": category,
        "created": ts, "modified": ts
    }
    if vault.save_vault():
        ui_module.console.print(f"[green]Note '{title}' saved[/]")

def view_notes(vault, ui_module):
    notes = vault.vault_data.get("notes", {})
    if not notes:
        ui_module.console.print("[yellow]No notes stored[/]")
        return
    cat = ui_module.show_menu(["All"] + vault.vault_data["categories"], title="Filter by category")
    rows = []
    mapping = {}
    for i,(nid, note) in enumerate(notes.items(), start=1):
        if cat != "All" and note["category"] != cat:
            continue
        preview = note["content"].replace("\n"," ")[:40] + ("..." if len(note["content"])>40 else "")
        rows.append([str(i), note["title"], preview, note["category"], utils.format_timestamp(note["modified"])])
        mapping[str(i)] = nid
    if not rows:
        ui_module.console.print("[yellow]No notes for that category[/]")
        return
    ui_module.show_table("Notes", ["#","Title","Preview","Category","Modified"], rows)
    sel = ui_module.ask("Enter number to view (blank to go back)", default="")
    if not sel:
        return
    nid = mapping.get(sel)
    if not nid:
        ui_module.console.print("[red]Invalid selection[/]")
        return
    view_note_details(vault, nid, ui_module)

def view_note_details(vault, note_id, ui_module):
    note = vault.vault_data["notes"][note_id]
    ui_module.console.print(f"[bold]{note['title']}[/]")
    ui_module.console.print(note["content"])
    opts = ["Edit Note", "Delete Note", "Back"]
    choice = ui_module.show_menu(opts, title="Note options")
    if choice == "Edit Note":
        edit_note(vault, note_id, ui_module)
    elif choice == "Delete Note":
        if ui_module.confirm(f"Delete '{note['title']}'?"):
            del vault.vault_data["notes"][note_id]
            if vault.save_vault():
                ui_module.console.print("[green]Deleted[/]")

def edit_note(vault, note_id, ui_module):
    note = vault.vault_data["notes"][note_id]
    title = ui_module.ask("Title", default=note['title'])
    ui_module.console.print("Enter new content (end with blank line):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            break
        lines.append(line)
    content = "\n".join(lines) if lines else note['content']
    category = note['category']
    if ui_module.confirm("Change category?"):
        category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    note.update({"title": title, "content": content, "category": category, "modified": datetime.datetime.now().isoformat()})
    if vault.save_vault():
        ui_module.console.print("[green]Note updated[/]")
