# server.py
from mcp.server.fastmcp import FastMCP
import sys
import logging

logger = logging.getLogger('log')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

import math
import random
import requests
from bs4 import BeautifulSoup
from zhipuai import ZhipuAI
from config_manager import load_config

# Create an MCP server·12
mcp = FastMCP("mcps")

# Add an addition tool
# 修改原有的ZhipuAI初始化
@mcp.tool()
def 联网查询(query_text: str) -> list:
    """
    通过智谱AI Web Search API查询信息
    查询最近新闻、金价、热播电影电视等一切用户需要联网查询的内容。
    :param query_text: 客户端传来的查询文字
    :return: 查询结果
    """
    config = load_config()
    client = ZhipuAI(api_key=config["ZHIPU_API_KEY"])

    response = client.web_search.web_search(
        search_engine="search_std",
        search_query=query_text,
        count=15,  # 返回结果的条数，范围1-50，默认10
        search_domain_filter="www.sohu.com",  # 只访问指定域名的内容
        search_recency_filter="noLimit",  # 搜索指定日期范围内的内容
        content_size="high"  # 控制网页摘要的字数，默认medium
    )
    
    content_list = []
    if hasattr(response, 'search_result'):
        for result in response.search_result:
            if hasattr(result, 'content'):
                content_list.append(result.content)
    
    logger.info(f"联网查询完成，查询内容: {content_list}")
    return {"success": True, "result": content_list}





# Start the server
if __name__ == "__main__":
    mcp.run(transport="stdio")


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:  # Add encoding
        return json.load(f)

def save_log(message):
    with open('query.log', 'a', encoding='utf-8') as f:  # Add encoding
        f.write(f"{datetime.now()} - {message}\n")
