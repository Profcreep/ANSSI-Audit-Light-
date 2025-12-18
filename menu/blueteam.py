# menu/blueteam.py
import customtkinter
import subprocess
import webbrowser
from core.utils import is_admin

def audit_logs():
    """Fonction backend qui analyse les logs Windows (Light+)"""
    results = [("⏳", "Analyse des logs en cours...", None)]
    try:
        # --- Security log activé ---
        cmd_security = 'powershell -Command "Get-WinEvent -LogName Security -MaxEvents 1"'
        output = subprocess.check_output(cmd_security, shell=True, text=True)
        if output.strip():
            results.append(("✅", "Security log activé", None))
        else:
            results.append(("❌", "Security log désactivé", None))

        # --- Échec de login dernières 24h ---
        cmd_fail = (
            'powershell -Command "(Get-WinEvent -FilterHashtable @{LogName=\'Security\'; Id=4625; '
            'StartTime=(Get-Date).AddDays(-1)} | Measure-Object).Count"'
        )
        count = int(subprocess.check_output(cmd_fail, shell=True, text=True))
        if count == 0:
            results.append(("✅", "Aucun échec login détecté", None))
        else:
            results.append(("⚠️", f"{count} échec(s) de login détecté(s) dernier 24h", None))

        # --- Erreurs System ---
        cmd_sys = 'powershell -Command "Get-WinEvent -LogName System -MaxEvents 5 | Where-Object {$_.LevelDisplayName -eq \'Error\'}"'
        output_sys = subprocess.check_output(cmd_sys, shell=True, text=True)
        if output_sys.strip():
            results.append(("⚠️", "Erreurs système détectées (vérifier)", None))
        else:
            results.append(("✅", "Aucune erreur système critique", None))

        # --- Erreurs Application ---
        cmd_app = 'powershell -Command "Get-WinEvent -LogName Application -MaxEvents 5 | Where-Object {$_.LevelDisplayName -eq \'Error\'}"'
        output_app = subprocess.check_output(cmd_app, shell=True, text=True)
        if output_app.strip():
            results.append(("⚠️", "Erreurs applicatives détectées (vérifier)", None))
        else:
            results.append(("✅", "Aucune erreur applicative critique", None))

    except subprocess.CalledProcessError as e:
        results.append(("⚠️", f"Impossible d'analyser les logs ({e})", None))
    except Exception as e:
        results.append(("⚠️", f"Erreur inattendue lors de l'analyse des logs ({e})", None))

    return results


# --- Fonction GUI ---
def open_blueteam():
    results = audit_logs()

    # Récupérer le thème courant
    current_theme = customtkinter.get_appearance_mode()

    win = customtkinter.CTkToplevel()
    win.title("Analyse Logs")
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

    customtkinter.CTkLabel(top_frame, text="Analyse Logs", font=("Arial", 16)).pack(pady=5)

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


# Pour le rapport HTML
run_blueteam_backend = audit_logs
