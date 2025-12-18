# menu/automation.py
import customtkinter
import subprocess
import yaml
from pathlib import Path
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

# Création si inexistants
ANSII_ROOT.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
RULES_DIR.mkdir(exist_ok=True)


def load_yaml():
    with open(YAML_FILE, "r") as f:
        return yaml.safe_load(f)

def run_automation_backend():
    """Fonction backend Automatisation - Light+"""
    results = [("⏳", "Vérification automatisation en cours...", None)]
    rules = load_yaml()
    auto_rules = rules.get("automation", {})

    # --- Scan interval ---
    interval = auto_rules.get("scan_interval_minutes", 60)
    if interval > 0:
        results.append(("✅", f"Intervalle de scan défini : {interval} minutes", None))
    else:
        results.append(("❌", "Intervalle de scan invalide", None))

    # --- Rapport automatique ---
    auto_report = auto_rules.get("auto_report", True)
    if auto_report:
        results.append(("✅", "Rapport automatique activé", None))
    else:
        results.append(("⚠️", "Rapport automatique désactivé", None))

    # --- Vérification dossier rapport ---
    report_path = Path(auto_rules.get("report_path", REPORTS_DIR))

    if not report_path.exists():
        try:
            report_path.mkdir(parents=True, exist_ok=True)
            results.append(("✅", f"Dossier rapport créé : {report_path}", None))
        except Exception as e:
            results.append(("❌", f"Impossible de créer le dossier rapport ({e})", None))
    else:
        results.append(("✅", f"Dossier rapport accessible : {report_path}", None))


    # --- Vérification tâches planifiées Windows ---
    try:
        cmd_tasks = 'powershell -Command "Get-ScheduledTask | Select-Object TaskName | ConvertTo-Json"'
        output = subprocess.check_output(cmd_tasks, shell=True, text=True)
        tasks = yaml.safe_load(output)
        if tasks:
            results.append(("✅", f"{len(tasks)} tâche(s) planifiée(s) détectée(s)", None))
        else:
            results.append(("⚠️", "Aucune tâche planifiée détectée", None))
    except Exception as e:
        results.append(("⚠️", f"Impossible de vérifier les tâches planifiées ({e})", None))

    return results

# ---------------- GUI ----------------
def open_automation():
    results = run_automation_backend()
    current_theme = customtkinter.get_appearance_mode()

    win = customtkinter.CTkToplevel()
    win.title("Automatisation")
    win.geometry("700x500")
    win.resizable(True, True)
    win.overrideredirect(True)
    customtkinter.set_appearance_mode(current_theme)

    # ---- Déplacement fenêtre ----
    def start_move(event):
        win.x = event.x
        win.y = event.y

    def do_move(event):
        x = win.winfo_x() + (event.x - win.x)
        y = win.winfo_y() + (event.y - win.y)
        win.geometry(f"+{x}+{y}")

    # ---------------- TOP BAR ----------------
    top_frame = customtkinter.CTkFrame(win, height=40)
    top_frame.pack(fill="x")
    top_frame.bind("<Button-1>", start_move)
    top_frame.bind("<B1-Motion>", do_move)

    customtkinter.CTkLabel(top_frame, text="Automatisation", font=("Arial", 16)).pack(pady=5)

    # ---------------- MAIN CONTENT ----------------
    scroll_frame = customtkinter.CTkScrollableFrame(win)
    scroll_frame.pack(expand=True, fill="both", padx=20, pady=20)

    for status, msg, _ in results:
        color = {"✅": "green", "❌": "red", "⚠️": "orange", "⏳": "gray"}.get(status, "white")
        customtkinter.CTkLabel(
            scroll_frame,
            text=f"{status} {msg}",
            text_color=color,
            anchor="w",
            justify="left",
            font=("Arial", 13)
        ).pack(fill="x", pady=2)

    # ---------------- BOTTOM FRAME ----------------
    bottom_frame = customtkinter.CTkFrame(win, height=50)
    bottom_frame.pack(fill="x", side="bottom")

    close_button = customtkinter.CTkButton(
        bottom_frame,
        text="❌ Close",
        fg_color="red",
        hover_color="#aa0000",
        command=win.destroy,
        width=100
    )
    close_button.pack(pady=10, padx=10, side="right")
