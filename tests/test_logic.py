import json
import os
root_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(root_dir, '..', 'config/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)
