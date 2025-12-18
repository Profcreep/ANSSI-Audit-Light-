# Auteur : Profcreep.
# ANSSI light diagnostic
# Python

#Librairie
import customtkinter
from PIL import Image
import webbrowser
from pathlib import Path
import os

#Configuration + raccourci
from core.config import IMG_DIR
from core.report import Report

#Backend Methode
from menu.audit import run_audit_backend
from menu.blueteam import run_blueteam_backend
from menu.soc import run_soc_backend
from menu.automation import run_automation_backend

#Menu Option
from menu.audit import open_audit
from menu.blueteam import open_blueteam
from menu.soc import open_soc
from menu.automation import open_automation

from core.config import load_yaml, REPORTS_DIR

from core.config import IMG_DIR, load_yaml

rules = load_yaml()



# ---------------- CONFIG ----------------

lune = IMG_DIR / "lune.png"
soleil = IMG_DIR / "soleil.png"

customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("blue")

# ---------------- FONCTIONS ----------------
def button_theme():
    if customtkinter.get_appearance_mode() == "Light":
        customtkinter.set_appearance_mode("Dark")
    else:
        customtkinter.set_appearance_mode("Light")

def open_github():
    webbrowser.open("https://github.com/Profcreep/ANSSI-Audit-Light-")


def open_info():
    rules = load_yaml()
    meta = rules.get("metadata", {})

    current_theme = customtkinter.get_appearance_mode()

    win = customtkinter.CTkToplevel(app)
    win.geometry("420x260")
    win.resizable(False, False)
    win.overrideredirect(True)
    customtkinter.set_appearance_mode(current_theme)

    # ---- déplacement fenêtre ----
    def start_move(event):
        win.x = event.x
        win.y = event.y

    def do_move(event):
        x = win.winfo_x() + (event.x - win.x)
        y = win.winfo_y() + (event.y - win.y)
        win.geometry(f"+{x}+{y}")

    # ---------------- TOP BAR ----------------
    top = customtkinter.CTkFrame(win, height=35)
    top.pack(fill="x")
    top.bind("<Button-1>", start_move)
    top.bind("<B1-Motion>", do_move)

    customtkinter.CTkLabel(
        top, text="Informations", font=("Arial", 14)
    ).pack(pady=5)

    # ---------------- CONTENT ----------------
    frame = customtkinter.CTkFrame(win)
    frame.pack(expand=True, fill="both", padx=20, pady=15)

    info_text = (
        f"Auteur : {meta.get('author', 'Profcreep')}\n"
        f"Version : {meta.get('version', '0.3')}\n\n"
        f"{meta.get('description', '')}"
    )

    customtkinter.CTkLabel(
        frame,
        text=info_text,
        justify="left",
        anchor="w",
        font=("Arial", 13)
    ).pack(fill="x", pady=10)

    # ---------------- BUTTONS ----------------
    btn_frame = customtkinter.CTkFrame(frame)
    btn_frame.pack(fill="x", pady=10)
    btn_frame.grid_columnconfigure((0, 1), weight=1)

    def open_rules():
        os.startfile(RULES_DIR)

    customtkinter.CTkButton(
        btn_frame,
        text="📂 Ouvrir rules",
        command=open_rules
    ).grid(row=0, column=0, padx=5)

    customtkinter.CTkButton(
        btn_frame,
        text="❌ Close",
        fg_color="red",
        hover_color="#aa0000",
        command=win.destroy
    ).grid(row=0, column=1, padx=5)


def close_app():
    app.destroy()

# ---- déplacement fenêtre ----
def start_move(event):
    app.x = event.x
    app.y = event.y

def do_move(event):
    x = app.winfo_x() + (event.x - app.x)
    y = app.winfo_y() + (event.y - app.y)
    app.geometry(f"+{x}+{y}")


def generate_report():
    report = Report()
    report.add_section("Audit", run_audit_backend())
    report.add_section("Analyse Logs", run_blueteam_backend())
    report.add_section("SOC", run_soc_backend())
    report.add_section("Automatisation", run_automation_backend())

    path = report.generate()
    print(f"Report generated: {path}")
    webbrowser.open(path.resolve().as_uri())




# ---------------- FENÊTRE ----------------
app = customtkinter.CTk()
app.geometry("600x400")
app.resizable(True, True)
app.overrideredirect(True)

# ---------------- GRID ROOT ----------------
app.grid_rowconfigure(1, weight=1)
app.grid_columnconfigure(0, weight=1)

# ---------------- TOP BAR ----------------
top_frame = customtkinter.CTkFrame(app, height=50)
top_frame.grid(row=0, column=0, sticky="ew")
top_frame.grid_columnconfigure((0, 1), weight=1)

# Bind déplacement
top_frame.bind("<Button-1>", start_move)
top_frame.bind("<B1-Motion>", do_move)

theme_image = customtkinter.CTkImage(
    light_image=Image.open(lune),
    dark_image=Image.open(soleil),
    size=(22, 22)
)


theme_button = customtkinter.CTkButton(
    top_frame,
    image=theme_image,
    text="",
    width=40,
    command=button_theme
)
theme_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")

github_button = customtkinter.CTkButton(
    top_frame,
    text="GitHub",
    command=open_github
)
github_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

# Bind aussi les widgets enfants
for widget in (theme_button, github_button):
    widget.bind("<Button-1>", start_move)
    widget.bind("<B1-Motion>", do_move)

# ---------------- MAIN CONTENT ----------------
main_frame = customtkinter.CTkFrame(app)
main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
main_frame.grid_columnconfigure((0,1,2,3), weight=1)

buttons = [
    ("Audit", open_audit),
    ("Analyse Log", open_blueteam),
    ("SOC", open_soc),
    ("Automatisation", open_automation),
]
for i, (label, callback) in enumerate(buttons):
    customtkinter.CTkButton(
        main_frame,
        text=label,
        height=60,
        command=callback
    ).grid(row=0, column=i, padx=10, pady=10, sticky="ew")

# ---------------- CLOSE BUTTON ----------------
bottom_frame = customtkinter.CTkFrame(app, height=50)
bottom_frame.grid(row=2, column=0, sticky="ew")
bottom_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(1, weight=1)

report_button = customtkinter.CTkButton(
    bottom_frame,
    text="📄 Générer rapport",
    command=generate_report,
    width=160
)
report_button.grid(row=0, column=0, padx=60, pady=10, sticky="w")

info_button = customtkinter.CTkButton(
    bottom_frame,
    text="ℹ️",
    width=40,
    command=open_info
)
info_button.grid(row=0, column=0, padx=15, pady=10, sticky="w")


close_button = customtkinter.CTkButton(
    bottom_frame,
    text="❌ Close",
    fg_color="red",
    hover_color="#aa0000",
    command=close_app,
    width=100
)
close_button.grid(row=0, column=1, padx=15, pady=10, sticky="e")

# ---------------- LANCEMENT ----------------
app.mainloop()

