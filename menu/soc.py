# menu/soc.py
import customtkinter
import subprocess
import json
import psutil  # pip install psutil
import webbrowser
from pathlib import Path

# ---------------- BACKEND SOC ----------------
def run_soc_backend():
    """Fonction backend SOC - Light+"""
    results = [("⏳", "Vérification SOC en cours...", None)]

    # --- Firewall par profil ---
    try:
        cmd_fw = 'powershell -Command "Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json"'
        output_fw = subprocess.check_output(cmd_fw, shell=True, text=True)
        fw_list = json.loads(output_fw)
        for fw in fw_list:
            name = fw.get("Name")
            enabled = fw.get("Enabled")
            if enabled:
                results.append(("✅", f"Firewall activé ({name})", None))
            else:
                results.append(("❌", f"Firewall inactif ({name})", None))
    except Exception as e:
        results.append(("⚠️", f"Impossible de vérifier le firewall ({e})", None))

    # --- Antivirus ---
    try:
        cmd_av = (
            'powershell -Command "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct | '
            'Select-Object displayName,productState | ConvertTo-Json"'
        )
        output_av = subprocess.check_output(cmd_av, shell=True, text=True)
        av_list = json.loads(output_av) if output_av.strip() else []

        if not av_list:
            results.append(("❌", "Aucun antivirus détecté", None))
        else:
            if isinstance(av_list, dict):
                av_list = [av_list]  # Cas d’un seul antivirus
            for av in av_list:
                name = av.get("displayName", "Inconnu")
                state = av.get("productState", 0)
                if state != 0:
                    results.append(("✅", f"Antivirus actif : {name}", None))
                else:
                    results.append(("❌", f"Antivirus désactivé : {name}", None))
    except Exception as e:
        results.append(("⚠️", f"Impossible de vérifier l'antivirus ({e})", None))

    # --- Ressources système ---
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage("C:/").percent

        results.append(("⚠️" if cpu_usage > 90 else "✅", f"CPU usage: {cpu_usage}%", None))
        results.append(("⚠️" if ram_usage > 85 else "✅", f"RAM usage: {ram_usage}%", None))
        results.append(("⚠️" if disk_usage > 80 else "✅", f"Disk C: usage: {disk_usage}%", None))
    except Exception as e:
        results.append(("⚠️", f"Impossible de vérifier les ressources système ({e})", None))

    return results

# ---------------- GUI SOC ----------------
def open_soc():
    results = run_soc_backend()
    current_theme = customtkinter.get_appearance_mode()

    win = customtkinter.CTkToplevel()
    win.title("SOC Monitoring")
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

    customtkinter.CTkLabel(top_frame, text="SOC Monitoring", font=("Arial", 16)).pack(pady=5)

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
