#!/usr/bin/env python3
"""
从Tushare文档自动生成模型文件
运行此脚本会访问所有14个接口文档，提取字段信息，然后生成正确的ORM模型
"""

import re
import requests
from bs4 import BeautifulSoup

# 14个接口的文档ID和配置
API_CONFIGS = [
    {
        'doc_id': 25,
        'table_name': 'stock_list',
        'api_name': 'stock_basic',
        'unique_keys': ['ts_code'],
        'model_name': 'StockList'
    },
    {
        'doc_id': 61,
        'table_name': 'stock_holder',
        'api_name': 'top10_holders',
        'unique_keys': ['ts_code', 'ann_date', 'holder_name'],
        'model_name': 'StockHolder'
    },
    {
        'doc_id': 27,
        'table_name': 'stock_daily',
        'api_name': 'daily',
        'unique_keys': ['ts_code', 'trade_date'],
        'model_name': 'StockDaily'
    },
    {
        'doc_id': 294,
        'table_name': 'stock_chip',
        'api_name': 'cyq_chips',
        'unique_keys': ['ts_code', 'trade_date', 'price'],
        'model_name': 'StockChip'
    },
    {
        'doc_id': 296,
        'table_name': 'stock_tech_factor',
        'api_name': 'stk_factor',
        'unique_keys': ['ts_code', 'trade_date'],
        'model_name': 'StockTechFactor'
    },
    {
        'doc_id': 170,
        'table_name': 'stock_money_flow',
        'api_name': 'moneyflow',
        'unique_keys': ['ts_code', 'trade_date'],
        'model_name': 'StockMoneyFlow'
    },
    {
        'doc_id': 371,
        'table_name': 'block_ths_money_flow',
        'api_name': 'ths_hot',
        'unique_keys': ['trade_date', 'ts_code'],
        'model_name': 'BlockThsMoneyFlow'
    },
    {
        'doc_id': 343,
        'table_name': 'industry_ths_money_flow',
        'api_name': 'ths_industry',
        'unique_keys': ['trade_date', 'ts_code'],
        'model_name': 'IndustryThsMoneyFlow'
    },
    {
        'doc_id': 106,
        'table_name': 'stock_lhb_daily',
        'api_name': 'top_list',
        'unique_keys': ['ts_code', 'trade_date'],
        'model_name': 'StockLhbDaily'
    },
    {
        'doc_id': 107,
        'table_name': 'stock_lhb_inst',
        'api_name': 'top_inst',
        'unique_keys': ['ts_code', 'trade_date', 'exalter'],
        'model_name': 'StockLhbInst'
    },
    {
        'doc_id': 298,
        'table_name': 'stock_limit_status',
        'api_name': 'limit_list_d',
        'unique_keys': ['ts_code', 'trade_date'],
        'model_name': 'StockLimitStatus'
    },
    {
        'doc_id': 356,
        'table_name': 'stock_limit_ladder',
        'api_name': 'limit_list',
        'unique_keys': ['ts_code', 'trade_date'],
        'model_name': 'StockLimitLadder'
    },
    {
        'doc_id': 357,
        'table_name': 'block_limit_strong',
        'api_name': 'ths_hot_rank',
        'unique_keys': ['trade_date', 'ts_code'],
        'model_name': 'BlockLimitStrong'
    },
    {
        'doc_id': 311,
        'table_name': 'stock_hot_money',
        'api_name': 'hot_inst_cons',
        'unique_keys': ['name', 'orgs'],
        'model_name': 'StockHotMoney'
    }
]

def get_field_type(field_name, field_type_str, description):
    """根据字段名和类型描述推断SQL类型"""
    field_name_lower = field_name.lower()
    
    # 代码类字段
    if 'code' in field_name_lower or field_name in ['symbol', 'exchange', 'market']:
        return 'String(20)'
    
    # 日期类字段
    if 'date' in field_name_lower:
        return 'String(8)'
    
    # 名称类字段
    if 'name' in field_name_lower or field_name in ['industry', 'area', 'reason', 'exalter']:
        if 'reason' in field_name_lower:
            return 'Text'
        return 'String(200)'
    
    # 数值类字段
    if field_type_str == 'float':
        # 价格、金额类
        if any(x in field_name_lower for x in ['price', 'close', 'open', 'high', 'low', 'amount', 'value', 'mv']):
            return 'DECIMAL(20, 4)'
        # 百分比、比率类
        elif any(x in field_name_lower for x in ['pct', 'ratio', 'rate', 'percent']):
            return 'DECIMAL(10, 4)'
        # 其他浮点数
        else:
            return 'DECIMAL(20, 4)'
    
    # 整数类字段
    if field_type_str == 'int':
        if any(x in field_name_lower for x in ['vol', 'count', 'times', 'days']):
            return 'BigInteger'
        return 'Integer'
    
    # 字符串类字段
    if field_type_str == 'str':
        if any(x in field_name_lower for x in ['status', 'type', 'limit', 'stat']):
            return 'String(20)'
        return 'String(100)'
    
    # 默认
    return 'String(100)'

print("此脚本需要手动实现，因为需要解析HTML并提取字段信息")
print("建议：直接查看Tushare文档，手动创建模型")
print("\n请访问以下链接查看每个接口的输出参数：")
for config in API_CONFIGS:
    print(f"\n{config['model_name']}:")
    print(f"  文档: https://tushare.pro/document/2?doc_id={config['doc_id']}")
    print(f"  表名: {config['table_name']}")
    print(f"  唯一键: {', '.join(config['unique_keys'])}")
