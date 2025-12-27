#!/usr/bin/env python3
"""测试同花顺板块和成分同步功能"""

import requests
import json

API_BASE = "http://localhost:5001"

def test_ths_index_sync():
    """测试同花顺板块同步"""
    print("=" * 60)
    print("测试1: 同步所有A股概念板块")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/api/sync/ths_index",
        json={"exchange": "A", "type": "N"}
    )
    
    if response.ok:
        data = response.json()
        print(f"✓ 同步成功！共 {data['count']} 条记录")
    else:
        print(f"✗ 同步失败: {response.json()}")
    print()

def test_ths_member_sync():
    """测试同花顺板块成分同步"""
    print("=" * 60)
    print("测试2: 同步电子元件板块成分 (885800.TI)")
    print("=" * 60)
    
    response = requests.post(
        f"{API_BASE}/api/sync/ths_member",
        json={"ts_code": "885800.TI"}
    )
    
    if response.ok:
        data = response.json()
        print(f"✓ 同步成功！共 {data['count']} 条记录")
    else:
        print(f"✗ 同步失败: {response.json()}")
    print()

def test_ths_index_query():
    """测试查询板块数据"""
    print("=" * 60)
    print("测试3: 查询数据库中的板块数据")
    print("=" * 60)
    
    import pymysql
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='Jk98!po78&lm',
        database='stock',
        charset='utf8mb4'
    )
    
    try:
        with conn.cursor() as cursor:
            # 查询板块总数
            cursor.execute("SELECT COUNT(*) FROM ths_industry_and_block")
            total = cursor.fetchone()[0]
            print(f"板块总数: {total}")
            
            # 查询前5个板块
            cursor.execute("SELECT ts_code, name, count, type FROM ths_industry_and_block LIMIT 5")
            print("\n前5个板块:")
            for row in cursor.fetchall():
                print(f"  {row[0]} - {row[1]} (成分数: {row[2]}, 类型: {row[3]})")
            
            # 查询电子元件板块成分数
            cursor.execute("SELECT COUNT(*) FROM ths_industry_and_block_detail WHERE ts_code='885800.TI'")
            member_count = cursor.fetchone()[0]
            print(f"\n电子元件板块成分数: {member_count}")
            
            # 查询前5个成分
            cursor.execute("SELECT con_code, con_name FROM ths_industry_and_block_detail WHERE ts_code='885800.TI' LIMIT 5")
            print("\n前5个成分股:")
            for row in cursor.fetchall():
                print(f"  {row[0]} - {row[1]}")
    finally:
        conn.close()
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("同花顺板块和成分同步功能测试")
    print("=" * 60 + "\n")
    
    # 测试板块同步
    test_ths_index_sync()
    
    # 测试成分同步
    test_ths_member_sync()
    
    # 测试数据查询
    test_ths_index_query()
    
    print("=" * 60)
    print("所有测试完成！")
    print("=" * 60)
