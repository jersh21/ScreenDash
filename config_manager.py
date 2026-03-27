import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "hotkeys": {
        "move_top_right": "ctrl+shift+right",
        "move_to_next_monitor": "ctrl+shift+z",
        "minimize_window": "ctrl+shift+down",
        "maximize_window": "ctrl+shift+up",
        "close_window": "ctrl+shift+x",
        "restore_all_minimized": "ctrl+shift+r",
        "alt_maximize": "alt+scroll_up",
        "alt_minimize": "alt+scroll_down",
        "alt_move_left": "alt+scroll_left",
        "alt_move_right": "alt+scroll_right",
        "alt_next_monitor": "ctrl+alt+mouse_middle",
        "alt_close": "alt+mouse_middle",
        "gather_all_windows": "ctrl+shift+g",
        "alt_gather_windows": "ctrl+alt+g"
    },
    "enabled": {
        "move_top_right": True,
        "move_to_next_monitor": True,
        "minimize_window": True,
        "maximize_window": True,
        "close_window": True,
        "restore_all_minimized": True,
        "alt_maximize": True,
        "alt_minimize": True,
        "alt_move_left": True,
        "alt_move_right": True,
        "alt_next_monitor": True,
        "alt_close": True,
        "gather_all_windows": True,
        "alt_gather_windows": True
    }
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    # Try multiple times in case of filesystem locking/sync issues
    import time
    for _ in range(3):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            time.sleep(0.05)
            
    return DEFAULT_CONFIG.copy()

def save_config(config_data):
    temp_file = CONFIG_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)
    os.replace(temp_file, CONFIG_FILE)
