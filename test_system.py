#!/usr/bin/env python3
"""
系统测试脚本
"""

import sys

def test_imports():
    """测试所有模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    print("=" * 50)
    
    try:
        from config import config
        print("✓ 配置模块导入成功")
        
        from utils import engine, SessionLocal, get_logger
        print("✓ 工具模块导入成功")
        
        import models
        print("✓ 数据模型导入成功")
        
        import repositories
        print("✓ 仓储层导入成功")
        
        from services.tushare_client import TushareClient
        print("✓ Tushare客户端导入成功")
        
        from services.data_access import DataAccessService
        print("✓ 数据接入服务导入成功")
        
        from services.data_sync import DataSyncService
        print("✓ 数据同步服务导入成功")
        
        from api.app import app
        print("✓ API应用导入成功")
        
        print("\n所有模块导入成功！")
        return True
    except Exception as e:
        print(f"\n✗ 模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """测试数据库连接"""
    print("\n" + "=" * 50)
    print("测试数据库连接...")
    print("=" * 50)
    
    try:
        from utils import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 数据库连接成功")
            return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def test_tables():
    """测试数据库表"""
    print("\n" + "=" * 50)
    print("测试数据库表...")
    print("=" * 50)
    
    try:
        from utils import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'stock_list', 'stock_holder', 'stock_daily', 'stock_chip',
            'stock_tech_factor', 'stock_money_flow', 'block_ths_money_flow',
            'industry_ths_money_flow', 'stock_lhb_daily', 'stock_lhb_inst',
            'stock_limit_status', 'stock_limit_ladder', 'block_limit_strong',
            'stock_hot_money'
        ]
        
        print(f"数据库中的表: {len(tables)}个")
        for table in expected_tables:
            if table in tables:
                print(f"  ✓ {table}")
            else:
                print(f"  ✗ {table} (缺失)")
        
        missing = set(expected_tables) - set(tables)
        if missing:
            print(f"\n缺失的表: {missing}")
            return False
        else:
            print("\n所有表都已创建！")
            return True
    except Exception as e:
        print(f"✗ 表检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("\n" + "=" * 50)
    print("Tushare股票数据采集系统 - 系统测试")
    print("=" * 50)
    
    results = []
    
    # 测试模块导入
    results.append(("模块导入", test_imports()))
    
    # 测试数据库连接
    results.append(("数据库连接", test_database()))
    
    # 测试数据库表
    results.append(("数据库表", test_tables()))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "=" * 50)
        print("所有测试通过！系统可以正常使用。")
        print("=" * 50)
        print("\n下一步:")
        print("1. 在 config/config.yaml 中配置你的 Tushare token")
        print("2. 运行 python3 main.py 启动API服务")
        print("3. 访问 http://localhost:5000/health 检查服务状态")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("部分测试失败，请检查错误信息。")
        print("=" * 50)
        sys.exit(1)

if __name__ == '__main__':
    main()
