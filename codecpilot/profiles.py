import json
import os
from pathlib import Path
from typing import Dict, Optional

PROFILES_DIR = Path.home() / ".codecpilot"
PROFILES_FILE = PROFILES_DIR / "profiles.json"

def _ensure_profiles_file():
    if not PROFILES_DIR.exists():
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    if not PROFILES_FILE.exists():
        with open(PROFILES_FILE, "w") as f:
            json.dump({}, f)

def load_profiles() -> Dict[str, str]:
    """Load all saved profiles from the JSON file."""
    _ensure_profiles_file()
    try:
        with open(PROFILES_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_profile(name: str, command: str) -> bool:
    """Save a successfully run command as a profile."""
    _ensure_profiles_file()
    profiles = load_profiles()
    profiles[name] = command
    try:
        with open(PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=4)
        return True
    except Exception:
        return False

def get_profile(name: str) -> Optional[str]:
    """Get a specific profile's command string."""
    profiles = load_profiles()
    return profiles.get(name)
