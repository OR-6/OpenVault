# openvault/twofa.py
import uuid
import datetime
import pyotp
import pyperclip
import urllib.parse
import os
import io
from openvault import utils, ui, config
import qrcode
import openvault


try:
    import cv2
    from pyzbar.pyzbar import decode as zbar_decode
    _HAS_OPENCV = True
except Exception:
    _HAS_OPENCV = False

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    from PIL import Image
    _HAS_PYZBAR = True
except Exception:
    _HAS_PYZBAR = False

def _parse_otpauth_uri(uri: str) -> dict:
    """Parse otpauth:// URI into fields."""
    res = {}
    try:
        parsed = urllib.parse.urlparse(uri)
        label = parsed.path.lstrip("/")
        if ":" in label:
            issuer_label, account = label.split(":", 1)
            res["issuer_from_label"] = urllib.parse.unquote(issuer_label)
            res["account"] = urllib.parse.unquote(account)
        else:
            res["account"] = urllib.parse.unquote(label)
        q = urllib.parse.parse_qs(parsed.query)
        if "secret" in q:
            res["secret"] = q["secret"][0]
        if "issuer" in q:
            res["issuer"] = q["issuer"][0]
        if "algorithm" in q:
            res["algorithm"] = q["algorithm"][0].upper()
        if "digits" in q:
            try:
                res["digits"] = int(q["digits"][0])
            except Exception:
                pass
        if "period" in q:
            try:
                res["period"] = int(q["period"][0])
            except Exception:
                pass
    except Exception:
        pass
    return res

def _decode_qr_from_image(path: str) -> str:
    """Attempt to decode QR content from image file. Returns payload or None."""
    
    try:
        if _HAS_PYZBAR:
            img = Image.open(path)
            decoded = pyzbar_decode(img)
            if decoded:
                return decoded[0].data.decode("utf-8")
    except Exception:
        pass
    
    try:
        if _HAS_OPENCV:
            import cv2
            img = cv2.imread(path)
            decoded = zbar_decode(img)
            if decoded:
                return decoded[0].data.decode("utf-8")
    except Exception:
        pass
    return None

def _scan_qr_from_webcam(timeout_seconds: int = 20) -> str:
    """Open webcam and scan QR codes; returns payload or None."""
    if not _HAS_OPENCV:
        return None
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    start = datetime.datetime.now()
    ui.console.print("[yellow]Scanning webcam for QR code. Press 'q' to quit early.[/]")
    payload = None
    while (datetime.datetime.now() - start).seconds < timeout_seconds:
        ret, frame = cap.read()
        if not ret:
            continue
        decoded = zbar_decode(frame)
        if decoded:
            payload = decoded[0].data.decode("utf-8")
            break
        cv2.imshow("OpenVault - QR Scanner (press q to stop)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    return payload

def add_twofa(vault: "openvault.vault.Vault", ui_module):
    ui_module.console.print("[bold]Add new 2FA entry[/]")
    method = ui_module.show_menu([
        "Enter secret/URI manually",
        "Import QR from image file",
        "Scan QR with webcam (optional)",
        "Back"
    ], title="Import method")
    if method == "Back":
        return
    secret = None
    parsed = {}
    if method == "Enter secret/URI manually":
        raw = ui_module.ask("Enter the secret key or otpauth:// URI")
        if raw.startswith("otpauth://"):
            parsed = _parse_otpauth_uri(raw)
            secret = parsed.get("secret")
        else:
            secret = raw.strip()
    elif method == "Import QR from image file":
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk(); root.withdraw(); root.update()
            path = filedialog.askopenfilename(title="Select QR image", filetypes=[("Images","*.png;*.jpg;*.jpeg;*.bmp;*.gif"),("All","*.*")])
            root.destroy()
        except Exception:
            path = ui_module.ask("Enter path to image file")
        if not path:
            ui_module.console.print("[yellow]No file selected[/]")
            return
        data = _decode_qr_from_image(path)
        if not data:
            ui_module.console.print("[red]No QR data detected[/]")
            return
        if data.startswith("otpauth://"):
            parsed = _parse_otpauth_uri(data)
            secret = parsed.get("secret")
        else:
            secret = data.strip()
    elif method == "Scan QR with webcam (optional)":
        if not _HAS_OPENCV:
            ui_module.console.print("[red]Webcam scanning requires opencv + pyzbar[/]")
            return
        data = _scan_qr_from_webcam()
        if not data:
            ui_module.console.print("[yellow]No QR detected[/]")
            return
        if data.startswith("otpauth://"):
            parsed = _parse_otpauth_uri(data)
            secret = parsed.get("secret")
        else:
            secret = data.strip()

    default_issuer = parsed.get("issuer") or parsed.get("issuer_from_label") or ""
    default_account = parsed.get("account") or ""
    default_algo = parsed.get("algorithm") or "SHA1"
    default_digits = parsed.get("digits") or 6
    default_period = parsed.get("period") or 30

    issuer = ui_module.ask("Issuer (service)", default=default_issuer)
    account = ui_module.ask("Account (email/username)", default=default_account)
    if not secret:
        secret = ui_module.ask("Enter the 2FA secret key")
    algo = ui_module.show_menu(["SHA1","SHA256","SHA512"], title=f"Select algorithm (detected: {default_algo})")
    digits = int(ui_module.show_menu(["6","8"], title=f"Digits (detected: {default_digits})"))
    period = int(ui_module.ask("Period (seconds)", default=str(default_period)))
    category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    entry_id = str(uuid.uuid4())
    ts = datetime.datetime.now().isoformat()
    vault.vault_data["twofa"][entry_id] = {
        "name": f"{issuer or account or '2FA'}",
        "secret": secret,
        "issuer": issuer,
        "account": account,
        "algo": algo,
        "digits": digits,
        "period": period,
        "category": category,
        "created": ts,
        "modified": ts
    }
    if vault.save():
        ui_module.console.print(f"[green]2FA '{issuer or account}' saved[/]")
        try:
            digest = utils.ALGO_MAP.get(algo)
            totp = pyotp.TOTP(secret, digits=digits, interval=period, digest=digest)
            code = totp.now()
            remaining = period - (int(datetime.datetime.now().timestamp()) % period)
            ui_module.console.print(f"[bold]Current code:[/] [green]{code}[/] (expires in {remaining}s)")
        except Exception:
            pass

def view_twofa(vault, ui_module):
    entries = vault.vault_data.get("twofa", {})
    if not entries:
        ui_module.console.print("[yellow]No 2FA entries[/]")
        return
    cat = ui_module.show_menu(["All"] + vault.vault_data["categories"], title="Filter by category")
    rows = []; mapping = {}
    for i,(eid,entry) in enumerate(entries.items(), start=1):
        if cat != "All" and entry["category"] != cat:
            continue
        rows.append([str(i), entry.get("name","-"), entry.get("issuer","-"), entry.get("account","-"), entry.get("category","-")])
        mapping[str(i)] = eid
    ui_module.show_table("Saved 2FA", ["#","Name","Issuer","Account","Category"], rows)
    sel = ui_module.ask("Enter number to manage (blank to go back)", default="")
    if not sel:
        return
    eid = mapping.get(sel)
    if not eid:
        ui_module.console.print("[red]Invalid selection[/]")
        return
    _view_twofa_details(vault, eid, ui_module)

def _view_twofa_details(vault, eid, ui_module):
    entry = vault.vault_data["twofa"][eid]
    secret = entry["secret"]; algo = entry.get("algo","SHA1"); digits = entry.get("digits",6); period = entry.get("period",30)
    ui_module.console.print(f"[bold]{entry.get('name','')}[/]")
    ui_module.console.print(f"Issuer: {entry.get('issuer','-')}")
    ui_module.console.print(f"Account: {entry.get('account','-')}")
    ui_module.console.print(f"Category: {entry.get('category','-')}")
    try:
        digest = utils.ALGO_MAP.get(algo)
        totp = pyotp.TOTP(secret, digits=digits, interval=period, digest=digest)
        code = totp.now()
        remaining = period - (int(datetime.datetime.now().timestamp()) % period)
        color = "green" if remaining > period*0.6 else ("yellow" if remaining > period*0.3 else "red")
        ui_module.console.print(f"[bold]Code:[/] [{color}]{code}[/{color}] (expires in {remaining}s)")
    except Exception as e:
        ui_module.console.print(f"[red]Error generating code: {e}[/]")
    opts = ["Copy Code", "Show Secret", "Export as QR", "Edit", "Delete", "Back"]
    choice = ui_module.show_menu(opts, title="2FA options")
    if choice == "Copy Code":
        try:
            pyperclip.copy(code)
            ui_module.console.print("[green]Code copied[/]")
            ui_module.schedule_clipboard_clear()
        except Exception:
            ui_module.console.print("[red]Failed to copy[/]")
    elif choice == "Show Secret":
        ui_module.console.print(f"[yellow]{secret}[/]")
    elif choice == "Export as QR":
        _export_qr(entry, ui_module)
    elif choice == "Edit":
        _edit_entry(vault, eid, ui_module)
    elif choice == "Delete":
        if ui_module.confirm(f"Delete '{entry.get('name')}'?"):
            del vault.vault_data["twofa"][eid]
            vault.save()
            ui_module.console.print("[green]Deleted[/]")

def _export_qr(entry, ui_module):
    try:
        label = f"{entry.get('issuer','')}:{entry.get('account','')}" if entry.get('issuer') and entry.get('account') else entry.get('name')
        uri = pyotp.TOTP(entry['secret'], digits=entry['digits'], interval=entry['period']).provisioning_uri(name=label, issuer_name=entry.get('issuer',''))
        img = qrcode.make(uri)
        os.makedirs(config.TEMP_DIR, exist_ok=True)
        path = os.path.join(config.TEMP_DIR, f"otp_{entry['name']}.png")
        img.save(path)
        ui_module.console.print(f"[green]QR exported to {path} (temporary)[/]")
    except Exception as e:
        ui_module.console.print(f"[red]Failed to export QR: {e}[/]")

def _edit_entry(vault, eid, ui_module):
    entry = vault.vault_data["twofa"][eid]
    ui_module.console.print("[dim]Press Enter to keep current value[/]")
    name = ui_module.ask("Name", default=entry.get("name",""))
    issuer = ui_module.ask("Issuer", default=entry.get("issuer",""))
    account = ui_module.ask("Account", default=entry.get("account",""))
    secret = entry.get("secret")
    if ui_module.confirm("Change secret?"):
        secret = ui_module.ask("New secret")
    algo = entry.get("algo","SHA1")
    if ui_module.confirm("Change algorithm?"):
        algo = ui_module.show_menu(["SHA1","SHA256","SHA512"], title="Select algorithm")
    digits = entry.get("digits",6)
    if ui_module.confirm("Change digits?"):
        digits = int(ui_module.show_menu(["6","8"], title="Select digits"))
    period = int(ui_module.ask("Period (seconds)", default=str(entry.get("period",30))))
    category = entry.get("category")
    if ui_module.confirm("Change category?"):
        category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")
    entry.update({
        "name": name, "issuer": issuer, "account": account,
        "secret": secret, "algo": algo, "digits": int(digits),
        "period": int(period), "category": category,
        "modified": datetime.datetime.now().isoformat()
    })
    if vault.save():
        ui_module.console.print("[green]2FA entry updated[/]")
