import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".xiaozhi_mcp_config.json"

def load_config():
    default_config = {
        "MCP_ENDPOINT": "wss://api.xiaozhi.me/mcp/?token=...",
        "ZHIPU_API_KEY": "",
        "OPENCLAW_URL": "http://38.76.206.70:18789",
        "HOOK_TOKEN": "openclaw123"
    }
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 合并默认配置
            return {**default_config, **config}
    except (FileNotFoundError, json.JSONDecodeError):
        return default_config

def save_config(config):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
