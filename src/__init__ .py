import yaml
from pathlib import Path

def load_settings():
    """Load settings from config/settings.yaml"""
    cfg_path = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
