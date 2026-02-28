# OpenClaw 消息推送 MCP
from mcp.server.fastmcp import FastMCP
import requests
import json
import sys
import logging
from pathlib import Path

# 配置路径
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
            return {**default_config, **config}
    except:
        return default_config

config = load_config()
OPENCLAW_URL = config.get("OPENCLAW_URL", "http://38.76.206.70:18789")
HOOK_TOKEN = config.get("HOOK_TOKEN", "openclaw123")

logger = logging.getLogger('log')

if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

mcp = FastMCP("OpenClaw-MCP")

@mcp.tool()
def 发送消息(message: str) -> dict:
    """
    发送消息给 OpenClaw，AI 会处理并返回结果。
    可以问问题、让 AI 执行命令、操作文件等。
    
    :param message: 任何你想让 AI 处理的消息
    :return: AI 的回复
    """
    # 每次读取最新配置
    current_config = load_config()
    url = current_config.get("OPENCLAW_URL", OPENCLAW_URL)
    token = current_config.get("HOOK_TOKEN", HOOK_TOKEN)
    
    payload = {
        "message": message,
        "name": "XiaoZhi",
        "deliver": True,
        "wakeMode": "now"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{url}/hooks/agent",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 202:
            logger.info(f"消息发送成功: {message}")
            return {"success": True, "message": "消息已发送给 OpenClaw"}
        else:
            logger.error(f"发送失败: {response.status_code}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        logger.error("连接 OpenClaw 失败")
        return {"success": False, "error": "连接失败"}
    except Exception as e:
        logger.error(f"异常: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print(f"[OpenClaw MCP] 启动成功，地址: {OPENCLAW_URL}", flush=True)
    mcp.run(transport="stdio")
