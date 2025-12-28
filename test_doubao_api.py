#!/usr/bin/env python3
"""测试豆包API配置"""

import requests
import json

# 豆包API配置
API_KEY = "c6961fb1-93da-45f8-910f-a588d63d97fa"
ENDPOINT_ID = "doubao-seed-1-6-lite-251015"
URL = f"https://ark.cn-beijing.volces.com/api/v3/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": ENDPOINT_ID,
    "messages": [
        {"role": "system", "content": "你是一个AI助手"},
        {"role": "user", "content": "你好"}
    ],
    "max_completion_tokens": 4096,
    "reasoning_effort": "medium"
}

print(f"测试豆包API...")
print(f"URL: {URL}")
print(f"Model: {ENDPOINT_ID}")
print()

try:
    response = requests.post(URL, json=payload, headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n成功! 返回内容: {result['choices'][0]['message']['content']}")
    else:
        print(f"\n失败! 错误信息: {response.text}")
        
except Exception as e:
    print(f"异常: {str(e)}")
