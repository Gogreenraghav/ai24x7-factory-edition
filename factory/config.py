import json, os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {
        "factory_name": "Demo Factory",
        "cameras": [],
        "shifts": {},
        "alert_contacts": {}
    }
