import customtkinter
import subprocess
from pathlib import Path
import yaml
import threading
import os

# ---------------- BACKEND ----------------
BASE_DIR = Path(__file__).resolve().parent.parent
#YAML_FILE = BASE_DIR / "rules" / "anssi.yml"
USER_DOCS = Path(os.getenv("USERPROFILE")) / "Documents" / "anssi"
YAML_FILE = USER_DOCS / "rules" / "anssi.yml"

# ---------------- INIT DOSSIERS ----------------
ANSII_ROOT = USER_DOCS
REPORTS_DIR = ANSII_ROOT / "reports"
RULES_DIR = ANSII_ROOT / "rules"

def load_yaml():
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------------- ENV DETECTION ----------------

def is_domain_joined():
    try:
        cmd = (
            'powershell -Command '
            '"(Get-CimInstance Win32_ComputerSystem).PartOfDomain"'
        )
        out = subprocess.check_output(cmd, shell=True, text=True).strip()
        return out.lower() == "true"
    except Exception:
        return False


# ---------------- AUDIT FUNCTIONS ----------------

def audit_password_policy(rules):
    results = [("⏳", "Checking password policy...", None)]
    min_len = rules["password_policy"]["min_length"]

    if is_domain_joined():
        results.append(("✅", "Password policy managed by Active Directory (recommended)", None))
        results.append(("❌", "Domain password policy not verified locally", None))
        return results
    else:
        results.append(("❌", "La machine n'est pas dans le domaine !", None))

    try:
        out = subprocess.check_output("net accounts", shell=True, text=True)
        for line in out.splitlines():
            if "Minimum password length" in line:
                val = int(line.split()[-1])
                if val >= min_len:
                    results.append(("✅", f"Local password length OK ({val})", None))
                else:
                    results.append(("❌", f"Local password length too short ({val})", None))
    except Exception as e:
        results.append(("❌", f"Password policy audit failed ({e})", None))

    return results

def audit_account_lockout(threshold):
    results = [("⏳", "Checking account lockout policy...", None)]

    if is_domain_joined():
        results.append(("✅", "Account lockout managed by Active Directory", None))
        results.append(("⚠️", "Lockout threshold not verified locally", None))
        return results

    else:
        results.append(("⚠️", "La machine n'est pas dans le domaine !", None))


    try:
        out = subprocess.check_output("net accounts", shell=True, text=True)
        for line in out.splitlines():
            if "Lockout threshold" in line:
                val = int(line.split()[-1])
                if val <= threshold:
                    results.append(("✅", f"Lockout threshold OK ({val})", None))
                else:
                    results.append(("❌", f"Lockout threshold too high ({val})", None))
    except Exception as e:
        results.append(("❌", f"Lockout audit failed ({e})", None))

    return results

# ---------------- NOUVEAUX TESTS ----------------

def audit_local_admins():
    results = [("⏳", "Vérification des administrateurs locaux en cours...", None)]
    try:
        # Récupérer tous les membres du groupe Administrateurs locaux (SID universel)
        cmd = (
            'powershell -Command '
            '"Get-LocalGroupMember -SID S-1-5-32-544 | Select-Object -ExpandProperty Name"'
        )
        output = subprocess.check_output(cmd, shell=True, text=True).strip()
        admins = output.splitlines()

        if not admins:
            results.append(("⚠️", "Aucun administrateur local détecté", None))
        else:
            for admin in admins:
                name_lower = admin.lower()
                if "admin" in name_lower or "adm" in name_lower:
                    results.append(("✅", f"Compte admin légitime : {admin}", None))
                else:
                    results.append(("❌", f"Compte local suspect : {admin}", None))

    except subprocess.CalledProcessError:
        results.append(("❌", "Impossible de lire les administrateurs locaux (droits insuffisants)", None))

    return results



def audit_uac():
    results = [("⏳", "Checking UAC configuration...", None)]
    try:
        out = subprocess.check_output(
            'powershell -Command "(Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System).EnableLUA"',
            shell=True, text=True
        ).strip()

        if out == "1":
            results.append(("✅", "UAC enabled", None))
        else:
            results.append(("❌", "UAC disabled", None))

    except Exception as e:
        results.append(("❌", f"UAC audit failed ({e})", None))

    return results

def audit_firewall():
    results = [("⏳", "Checking Windows Firewall...", None)]
    try:
        out = subprocess.check_output(
            'powershell -Command "Get-NetFirewallProfile | Select Name, Enabled | ConvertTo-Json"',
            shell=True, text=True
        )
        profiles = yaml.safe_load(out)

        for p in profiles:
            if p["Enabled"]:
                results.append(("✅", f"Firewall enabled ({p['Name']})", None))
            else:
                results.append(("❌", f"Firewall disabled ({p['Name']})", None))

    except Exception as e:
        results.append(("❌", f"Firewall audit failed ({e})", None))

    return results

def audit_antivirus():
    results = [("⏳", "Vérification antivirus...", None)]
    try:
        cmd = (
            'powershell -Command '
            '"Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | '
            'Select-Object displayName,productState | ConvertTo-Json"'
        )
        output = subprocess.check_output(cmd, shell=True, text=True)
        av_list = yaml.safe_load(output)  # on peut aussi utiliser json.loads()

        if not av_list:
            results.append(("❌", "Aucun antivirus détecté", None))
        else:
            # Pour chaque antivirus détecté
            if isinstance(av_list, dict):
                av_list = [av_list]  # cas 1 AV
            for av in av_list:
                name = av.get("displayName", "Inconnu")
                state = av.get("productState", 0)
                if state != 0:
                    results.append(("✅", f"Antivirus actif : {name}", None))
                else:
                    results.append(("❌", f"Antivirus désactivé : {name}", None))
    except Exception as e:
        results.append(("⚠️", f"Impossible de vérifier l'antivirus ({e})", None))

    return results


# ---------------- BACKEND (REPORT) ----------------

def run_audit_backend():
    rules = load_yaml()["audit"]
    results = []
    results += audit_password_policy(rules)
    results += audit_account_lockout(rules["account_lockout"]["threshold"])
    results += audit_local_admins()
    results += audit_uac()
    results += audit_firewall()
    results += audit_antivirus()
    

    # Nettoyage (pas de ⏳ dans le rapport)
    return [(s, m) for s, m, _ in results if s != "⏳"]

# ---------------- GUI ----------------

def open_audit():
    rules = load_yaml()["audit"]

    win = customtkinter.CTkToplevel()
    win.geometry("750x550")
    win.overrideredirect(True)
    win.resizable(True, True)

    # ---------------- Déplacement fenêtre ----------------
    def start_move(e):
        win.x = e.x
        win.y = e.y

    def do_move(e):
        x = win.winfo_x() + e.x - win.x
        y = win.winfo_y() + e.y - win.y
        win.geometry(f"+{x}+{y}")

    # ---------------- TOP BAR ----------------
    top_frame = customtkinter.CTkFrame(win, height=40)
    top_frame.pack(fill="x")
    top_frame.bind("<Button-1>", start_move)
    top_frame.bind("<B1-Motion>", do_move)

    customtkinter.CTkLabel(
        top_frame,
        text="Audit – ANSSI Light+",
        font=("Arial", 16)
    ).pack(pady=5)

    # ---------------- SCROLLABLE CONTENT ----------------
    scroll_frame = customtkinter.CTkScrollableFrame(
        win,
        label_text="Résultats de l'audit",
        label_font=("Arial", 14)
    )
    scroll_frame.pack(expand=True, fill="both", padx=20, pady=10)

    def run_gui_audit():
        tests = []
        tests += audit_password_policy(rules)
        tests += audit_account_lockout(rules["account_lockout"]["threshold"])
        tests += audit_local_admins()
        tests += audit_uac()
        tests += audit_firewall()
        tests += audit_antivirus()

        for status, msg, _ in tests:
            color = {
                "✅": "green",
                "❌": "red",
                "⚠️": "orange",
                "⏳": "gray"
            }.get(status, "white")

            customtkinter.CTkLabel(
                scroll_frame,
                text=f"{status} {msg}",
                text_color=color,
                anchor="w",
                justify="left",
                font=("Arial", 13)
            ).pack(fill="x", pady=2)

    # Lancer l’audit en thread
    import threading
    threading.Thread(target=run_gui_audit, daemon=True).start()

    # ---------------- BOTTOM BAR ----------------
    bottom_frame = customtkinter.CTkFrame(win, height=45)
    bottom_frame.pack(fill="x")

    bottom_frame.grid_columnconfigure(0, weight=1)

    close_button = customtkinter.CTkButton(
        bottom_frame,
        text="❌ Close",
        fg_color="red",
        hover_color="#aa0000",
        width=120,
        command=win.destroy
    )
    close_button.pack(pady=8, padx=15, side="right")
