#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试同步记录功能"""

from utils.db import SessionLocal
from repositories import SyncRecordRepository
from datetime import datetime, timedelta

def test_sync_record():
    """测试同步记录功能"""
    db = SessionLocal()
    repo = SyncRecordRepository(db)
    
    try:
        print("\n" + "="*50)
        print("测试同步记录功能")
        print("="*50)
        
        # 测试日期
        test_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        sync_type = 'daily'
        
        # 1. 检查是否已同步
        print(f"\n1. 检查日期 {test_date} ({sync_type}) 是否已同步...")
        is_synced = repo.is_synced(test_date, sync_type)
        print(f"   结果: {'已同步' if is_synced else '未同步'}")
        
        # 2. 标记为已同步
        print(f"\n2. 标记日期 {test_date} ({sync_type}) 为已同步...")
        repo.record_sync(test_date, sync_type, 'success', 100)
        print("   完成")
        
        # 3. 再次检查
        print(f"\n3. 再次检查日期 {test_date} ({sync_type}) 是否已同步...")
        is_synced = repo.is_synced(test_date, sync_type)
        print(f"   结果: {'已同步' if is_synced else '未同步'}")
        
        # 4. 获取未同步日期
        date_list = [(datetime.now() - timedelta(days=i)).strftime('%Y%m%d') for i in range(5)]
        print(f"\n4. 获取未同步的日期 ({sync_type})...")
        print(f"   检查日期列表: {date_list}")
        unsynced = repo.get_unsynced_dates(date_list, sync_type)
        print(f"   未同步日期: {unsynced}")
        
        print("\n" + "="*50)
        print("测试完成！")
        print("="*50)
        
    finally:
        db.close()

if __name__ == '__main__':
    test_sync_record()
