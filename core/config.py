# core/config.py
import os
from pathlib import Path
import yaml

# ---------------- BASE PROJET ----------------
BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
IMG_DIR = ASSETS_DIR / "img"

DEFAULT_RULES_DIR = BASE_DIR / "rules"
DEFAULT_YAML = DEFAULT_RULES_DIR / "anssi.yml"

# ---------------- ENV UTILISATEUR ----------------
USER_HOME = Path(os.getenv("USERPROFILE"))
USER_DOCS = USER_HOME / "Documents"

ANSSI_DIR = USER_DOCS / "anssi"
REPORTS_DIR = ANSSI_DIR / "reports"
RULES_DIR = ANSSI_DIR / "rules"
YAML_FILE = RULES_DIR / "anssi.yml"

# ---------------- INIT ----------------
def ensure_user_environment():
    """Crée l'arborescence utilisateur si absente"""
    ANSSI_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    RULES_DIR.mkdir(parents=True, exist_ok=True)


    # Copier le YAML par défaut s'il n'existe pas
    if not YAML_FILE.exists():
        if DEFAULT_YAML.exists():
            YAML_FILE.write_text(
                DEFAULT_YAML.read_text(encoding="utf-8"),
                encoding="utf-8"
            )
        else:
            raise FileNotFoundError("anssi.yml par défaut introuvable")

def load_yaml():
    ensure_user_environment()
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
