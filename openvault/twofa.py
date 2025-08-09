# openvault/twofa.py
import uuid
import datetime
import pyotp
import pyperclip
import urllib.parse
import os
import io
from openvault import utils, ui
from openvault import config
import qrcode

# Optional imports for QR scanning
try:
    import cv2
    from pyzbar.pyzbar import decode as zbar_decode
    _HAS_OPENCV = True
except Exception:
    _HAS_OPENCV = False

def _parse_otpauth_uri(uri: str) -> dict:
    """
    Parse otpauth:// URI into fields.
    Returns dict with secret, issuer, account, algorithm, digits, period
    """
    result = {}
    if not uri.startswith("otpauth://"):
        return result
    try:
        parsed = urllib.parse.urlparse(uri)
        # path like /TYPE/ISSUER:ACCOUNT or /TYPE/LABEL
        label = parsed.path.lstrip("/")
        # label may include issuer:account or just account
        if ":" in label:
            issuer_label, account = label.split(":", 1)
            # sometimes issuer appears in label and query
            result["account"] = urllib.parse.unquote(account)
            result["issuer_from_label"] = urllib.parse.unquote(issuer_label)
        else:
            result["account"] = urllib.parse.unquote(label)

        q = urllib.parse.parse_qs(parsed.query)
        if "secret" in q:
            result["secret"] = q["secret"][0]
        if "issuer" in q:
            result["issuer"] = q["issuer"][0]
        if "algorithm" in q:
            result["algorithm"] = q["algorithm"][0].upper()
        if "digits" in q:
            try:
                result["digits"] = int(q["digits"][0])
            except Exception:
                pass
        if "period" in q:
            try:
                result["period"] = int(q["period"][0])
            except Exception:
                pass
    except Exception:
        pass
    return result

def _extract_secret_from_qr_image_pil(pil_image) -> str:
    """Use pyzbar (if available) on PIL image bytes to decode QR -> returns first payload"""
    try:
        # convert PIL image to opencv-compatible if needed
        img_bytes = io.BytesIO()
        pil_image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        import numpy as np
        import cv2
        arr = np.frombuffer(img_bytes.getvalue(), dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        decoded = zbar_decode(img)
        for d in decoded:
            try:
                return d.data.decode("utf-8")
            except Exception:
                continue
    except Exception:
        pass
    return None

def _scan_qr_from_webcam(timeout_seconds: int = 20) -> str:
    """Open webcam and scan for QR codes. Returns data or None."""
    if not _HAS_OPENCV:
        return None
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    start = datetime.datetime.now()
    ui.console.print("[yellow]Scanning webcam for QR code. Press 'q' to quit scanning early.[/]")
    data = None
    while (datetime.datetime.now() - start).seconds < timeout_seconds:
        ret, frame = cap.read()
        if not ret:
            continue
        decoded = zbar_decode(frame)
        if decoded:
            try:
                data = decoded[0].data.decode("utf-8")
                break
            except Exception:
                pass
        cv2.imshow("OpenVault - QR Scanner (press q to stop)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    return data

def _scan_qr_from_file(path: str) -> str:
    """Try to decode QR from image file (supports multiple libs)."""
    # Try pyzbar with cv2
    try:
        if _HAS_OPENCV:
            import cv2
            img = cv2.imread(path)
            decoded = zbar_decode(img)
            if decoded:
                return decoded[0].data.decode("utf-8")
    except Exception:
        pass
    # Fallback: try PIL + pyzbar (pyzbar can accept PIL images)
    try:
        from PIL import Image
        img = Image.open(path)
        try:
            decoded2 = zbar_decode(img)
            if decoded2:
                return decoded2[0].data.decode("utf-8")
        except Exception:
            # try pillow->opencv route in helper
            return _extract_secret_from_qr_image_pil(img)
    except Exception:
        pass
    return None

def add_twofa(vault, ui_module):
    ui_module.console.print("[bold]Add new 2FA entry[/]")
    method = ui_module.show_menu(["Enter secret/URI manually", "Import QR from image file", "Scan QR with webcam (requires opencv+pyzbar)", "Back"], title="Import method")
    if method == "Back":
        return
    secret = None
    parsed = {}
    if method == "Enter secret/URI manually":
        raw = ui_module.ask("Enter the secret key or full otpauth:// URI")
        # if it's an otpauth URI, parse it
        if raw.startswith("otpauth://"):
            parsed = _parse_otpauth_uri(raw)
            secret = parsed.get("secret")
        else:
            secret = raw.strip()
    elif method == "Import QR from image file":
        # file selection: try tkinter, fallback to text input
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.update()
            path = filedialog.askopenfilename(title="Select QR code image", filetypes=[("Image Files","*.png;*.jpg;*.jpeg;*.bmp;*.gif"),("All files","*.*")])
            root.destroy()
        except Exception:
            path = ui_module.ask("Enter full path to image file")
        if not path:
            ui_module.console.print("[yellow]No file selected[/]")
            return
        data = _scan_qr_from_file(path)
        if data and data.startswith("otpauth://"):
            parsed = _parse_otpauth_uri(data)
            secret = parsed.get("secret")
        elif data:
            # maybe raw secret encoded in QR
            secret = data.strip()
        else:
            ui_module.console.print("[red]No QR data detected in the image[/]")
            return
    elif method == "Scan QR with webcam (requires opencv+pyzbar)":
        if not _HAS_OPENCV:
            ui_module.console.print("[red]opencv or pyzbar not available. Install opencv-python and pyzbar to use webcam scanning[/]")
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

    # Try to auto-fill fields from parsed metadata
    default_issuer = parsed.get("issuer") or parsed.get("issuer_from_label") or ""
    default_account = parsed.get("account") or ""
    default_algo = parsed.get("algorithm") or "SHA1"
    default_digits = parsed.get("digits") or 6
    default_period = parsed.get("period") or 30

    # ask/confirm fields (pre-filled)
    issuer = ui_module.ask("Issuer (service provider)", default=default_issuer)
    account = ui_module.ask("Account name/email", default=default_account)
    if not secret:
        secret = ui_module.ask("Enter the 2FA secret key")
    # algorithm choices, prefer detected
    algo = ui_module.show_menu(["SHA1", "SHA256", "SHA512"], title=f"Select algorithm (detected: {default_algo})")
    digits = int(ui_module.show_menu(["6","8"], title=f"Digits (detected: {default_digits})"))
    period = int(ui_module.ask("Period (seconds)", default=str(default_period)))
    category = ui_module.show_menu(vault.vault_data["categories"], title="Select category")

    # store entry
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
    if vault.save_vault():
        ui_module.console.print(f"[green]2FA entry saved ({issuer or account})[/]")
        # Show code immediately with countdown
        try:
            digest = utils.ALGO_MAP.get(algo)
            totp = pyotp.TOTP(secret, digits=digits, interval=period, digest=digest)
            code = totp.now()
            # compute seconds left
            remaining = period - (int(datetime.datetime.now().timestamp()) % period)
            ui_module.console.print(f"[bold]Current code:[/] [green]{code}[/]  (expires in {remaining}s)")
        except Exception:
            pass

def view_twofa(vault, ui_module):
    if not vault.vault_data["twofa"]:
        ui_module.console.print("[yellow]No 2FA entries[/]")
        return
    cat = ui_module.show_menu(["All"] + vault.vault_data["categories"], title="Filter by category")
    rows = []
    mapping = {}
    for i,(eid,entry) in enumerate(vault.vault_data["twofa"].items(), start=1):
        if cat != "All" and entry["category"] != cat:
            continue
        rows.append([str(i), entry.get("name","-"), entry.get("issuer","-"), entry.get("account","-"), entry["category"]])
        mapping[str(i)] = eid
    ui_module.show_table("Saved 2FA", ["#","Name","Issuer","Account","Category"], rows)
    sel = ui_module.ask("Enter number to manage (blank to go back)", default="")
    if not sel:
        return
    eid = mapping.get(sel)
    if not eid:
        ui_module.console.print("[red]Invalid selection[/]")
        return
    view_twofa_details(vault, eid, ui_module)

def view_twofa_details(vault, entry_id, ui_module):
    entry = vault.vault_data["twofa"][entry_id]
    secret = entry["secret"]
    algo = entry.get("algo","SHA1")
    digits = entry.get("digits",6)
    period = entry.get("period",30)
    issuer = entry.get("issuer","")
    account = entry.get("account","")
    ui_module.console.print(f"[bold cyan]{entry['name']}[/]")
    ui_module.console.print(f"Issuer: {issuer or '-'}")
    ui_module.console.print(f"Account: {account or '-'}")
    ui_module.console.print(f"Category: {entry.get('category','-')}")
    ui_module.console.print(f"Algorithm: {algo} | Digits: {digits} | Period: {period}s")
    try:
        digest = utils.ALGO_MAP.get(algo)
        totp = pyotp.TOTP(secret, digits=digits, interval=period, digest=digest)
        code = totp.now()
        remaining = period - (int(datetime.datetime.now().timestamp()) % period)
        # color by remaining
        if remaining > period * 0.6:
            color = "green"
        elif remaining > period * 0.3:
            color = "yellow"
        else:
            color = "red"
        ui_module.console.print(f"[bold]Code:[/] [{color}]{code}[/{color}] (expires in {remaining}s)")
    except Exception as e:
        ui_module.console.print(f"[red]Error generating code: {e}[/]")
    opts = ["Copy Code", "Show Secret", "Export as QR", "Edit Entry", "Delete Entry", "Back"]
    choice = ui_module.show_menu(opts, title="2FA options")
    if choice == "Copy Code":
        try:
            pyperclip.copy(code)
            ui_module.console.print("[green]Code copied to clipboard[/]")
            ui_module.schedule_clipboard_clear()
        except Exception:
            ui_module.console.print("[red]Failed to copy[/]")
    elif choice == "Show Secret":
        ui_module.console.print(f"[yellow]{secret}[/]")
    elif choice == "Export as QR":
        _export_qr(entry, ui_module)
    elif choice == "Edit Entry":
        _edit_entry(vault, entry_id, ui_module)
    elif choice == "Delete Entry":
        if ui_module.confirm(f"Delete '{entry['name']}'?"):
            del vault.vault_data["twofa"][entry_id]
            vault.save_vault()
            ui_module.console.print("[green]Deleted[/]")

def _export_qr(entry, ui_module):
    try:
        label = f"{entry.get('issuer','')}:{entry.get('account','')}" if entry.get('issuer') and entry.get('account') else entry['name']
        uri = pyotp.TOTP(entry['secret'], digits=entry['digits'], interval=entry['period']).provisioning_uri(name=label, issuer_name=entry.get('issuer',''))
        img = qrcode.make(uri)
        os.makedirs(config.TEMP_DIR, exist_ok=True)
        path = os.path.join(config.TEMP_DIR, f"otp_{entry['name']}.png")
        img.save(path)
        ui_module.console.print(f"[green]QR exported to {path} (temporary)[/]")
    except Exception as e:
        ui_module.console.print(f"[red]Failed to export QR: {e}[/]")

def _edit_entry(vault, entry_id, ui_module):
    entry = vault.vault_data["twofa"][entry_id]
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
        "name": name, "issuer": issuer, "account": account, "secret": secret,
        "algo": algo, "digits": int(digits), "period": int(period),
        "category": category, "modified": datetime.datetime.now().isoformat()
    })
    if vault.save_vault():
        ui_module.console.print("[green]2FA entry updated[/]")
