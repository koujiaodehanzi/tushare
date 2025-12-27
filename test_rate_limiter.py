#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试滑动时间窗口限流器
"""

import time
from utils.rate_limiter import RateLimiter

def test_rate_limiter():
    """测试限流器"""
    # 创建限流器：每10秒最多5次调用
    limiter = RateLimiter(max_calls=5, period=10)
    
    print("测试1：快速调用6次（应该在第6次时等待）")
    for i in range(6):
        start = time.time()
        limiter.acquire('test_api')
        elapsed = time.time() - start
        print(f"第{i+1}次调用，等待时间: {elapsed:.2f}秒")
        stats = limiter.get_stats('test_api')
        print(f"  当前窗口内调用次数: {stats['calls_in_window']}/{stats['max_calls']}")
    
    print("\n测试2：不同接口独立限流")
    limiter2 = RateLimiter(max_calls=3, period=5)
    
    print("接口A调用3次：")
    for i in range(3):
        limiter2.acquire('api_a')
        print(f"  api_a 第{i+1}次调用")
    
    print("接口B调用3次（不受接口A影响）：")
    for i in range(3):
        limiter2.acquire('api_b')
        print(f"  api_b 第{i+1}次调用")
    
    print("\n接口A再次调用（应该等待）：")
    start = time.time()
    limiter2.acquire('api_a')
    elapsed = time.time() - start
    print(f"  api_a 第4次调用，等待时间: {elapsed:.2f}秒")
    
    print("\n测试3：查看所有接口统计")
    all_stats = limiter2.get_stats()
    for iface, stats in all_stats.items():
        print(f"{iface}: {stats['calls_in_window']}/{stats['max_calls']} 调用")

if __name__ == '__main__':
    test_rate_limiter()
