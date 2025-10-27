from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG_USERS = ROOT / "config" / "users.yaml"
CFG_SETTINGS = ROOT / "config" / "settings.yaml"
CFG_SCENARIO = ROOT / "config" / "scenario.yaml"
SANDBOX = ROOT / "sandbox"
ASSETS = ROOT / "assets"

def ensure_dirs():
    SANDBOX.mkdir(parents=True, exist_ok=True)
    (ROOT / "logs").mkdir(parents=True, exist_ok=True)

def load_yaml(p: Path):
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_users():
    data = load_yaml(CFG_USERS)
    return data.get("users", [])

def load_settings():
    data = load_yaml(CFG_SETTINGS)
    return data or {}

def load_scenario():
    data = load_yaml(CFG_SCENARIO)
    return data or {}
