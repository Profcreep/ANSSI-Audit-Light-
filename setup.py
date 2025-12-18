# setup.py
from core.config import ensure_user_environment, YAML_FILE

def main():
    ensure_user_environment()
    print("✅ Environnement ANSSI initialisé")
    print(f"📁 Règles : {YAML_FILE.parent}")
    print(f"📄 Fichier : {YAML_FILE}")

if __name__ == "__main__":
    main()
