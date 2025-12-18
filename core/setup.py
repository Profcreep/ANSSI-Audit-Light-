
import os
from pathlib import Path
import yaml

# ---------------- Répertoires ----------------
USER_DOCS = Path(os.getenv("USERPROFILE")) / "Documents"
ANSSI_DIR = USER_DOCS / "anssi"
REPORTS_DIR = ANSSI_DIR / "reports"
RULES_DIR = ANSSI_DIR / "rules"
YAML_FILE = RULES_DIR / "anssi.yml"

# Crée les dossiers s'ils n'existent pas
for folder in [ANSSI_DIR, REPORTS_DIR, RULES_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# ---------------- Chargement YAML ----------------
def load_yaml():
    """Charge le fichier YAML ANSSI"""
    if not YAML_FILE.exists():
        raise FileNotFoundError(f"Le fichier YAML n'existe pas. Lancez setup.py pour le créer : {YAML_FILE}")
    
    with open(YAML_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------------- Raccourcis ----------------
def get_paths():
    """Retourne un dictionnaire des chemins utiles"""
    return {
        "anssi_dir": ANSSI_DIR,
        "reports_dir": REPORTS_DIR,
        "rules_dir": RULES_DIR,
        "yaml_file": YAML_FILE
    }

# ---------------- Exemple d'utilisation ----------------
# rules = load_yaml()
# paths = get_paths()
