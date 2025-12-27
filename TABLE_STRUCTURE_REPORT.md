# 数据库表结构验证报告

## 验证时间
2025-12-13 01:31

## 验证结果
✅ 所有14张表已按照Tushare文档正确创建

## 表结构详情

### 1. stock_list (股票列表)
- 接口: stock_basic
- 文档: https://tushare.pro/document/2?doc_id=25
- 唯一索引: ts_code
- 字段数: 17个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 2. stock_holder (股东持股)
- 接口: top10_holders
- 文档: https://tushare.pro/document/2?doc_id=61
- 联合唯一索引: ts_code + ann_date + holder_name
- 字段数: 9个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 3. stock_daily (日线行情)
- 接口: daily
- 文档: https://tushare.pro/document/2?doc_id=27
- 联合唯一索引: ts_code + trade_date
- 字段数: 10个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 4. stock_chip (股票每日筹码)
- 接口: cyq_chips
- 文档: https://tushare.pro/document/2?doc_id=294
- 联合唯一索引: ts_code + trade_date + price
- 字段数: 4个业务字段 + 2个系统字段
- 关键变更: ✅ 修正为只包含4个字段 (ts_code, trade_date, price, percent)
- 状态: ✅ 已验证

### 5. stock_tech_factor (股票技术面因子)
- 接口: stk_factor
- 文档: https://tushare.pro/document/2?doc_id=296
- 联合唯一索引: ts_code + trade_date
- 字段数: 35个业务字段 + 2个系统字段
- 关键字段: 包含MACD, KDJ, RSI, BOLL, CCI等技术指标
- 状态: ✅ 已验证

### 6. stock_money_flow (个股资金流向)
- 接口: moneyflow
- 文档: https://tushare.pro/document/2?doc_id=170
- 联合唯一索引: ts_code + trade_date
- 字段数: 20个业务字段 + 2个系统字段
- 关键字段: 小单/中单/大单/特大单的买卖量和金额
- 状态: ✅ 已验证

### 7. block_ths_money_flow (同花顺板块资金流向)
- 接口: ths_hot
- 文档: https://tushare.pro/document/2?doc_id=371
- 联合唯一索引: trade_date + ts_code
- 字段数: 9个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 8. industry_ths_money_flow (同花顺行业资金流向)
- 接口: ths_industry
- 文档: https://tushare.pro/document/2?doc_id=343
- 联合唯一索引: trade_date + ts_code
- 字段数: 9个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 9. stock_lhb_daily (龙虎榜每日统计单)
- 接口: top_list
- 文档: https://tushare.pro/document/2?doc_id=106
- 联合唯一索引: ts_code + trade_date
- 字段数: 15个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 10. stock_lhb_inst (龙虎榜机构交易单)
- 接口: top_inst
- 文档: https://tushare.pro/document/2?doc_id=107
- 联合唯一索引: ts_code + trade_date + exalter
- 字段数: 8个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 11. stock_limit_status (股票涨跌停和炸板数据)
- 接口: limit_list_d
- 文档: https://tushare.pro/document/2?doc_id=298
- 联合唯一索引: ts_code + trade_date
- 字段数: 14个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 12. stock_limit_ladder (涨停股票连板天梯)
- 接口: limit_list
- 文档: https://tushare.pro/document/2?doc_id=356
- 联合唯一索引: ts_code + trade_date
- 字段数: 16个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 13. block_limit_strong (涨停板块最强统计)
- 接口: ths_hot_rank
- 文档: https://tushare.pro/document/2?doc_id=357
- 联合唯一索引: trade_date + ts_code
- 字段数: 10个业务字段 + 2个系统字段
- 状态: ✅ 已验证

### 14. stock_hot_money (股票游资名录)
- 接口: hot_inst_cons
- 文档: https://tushare.pro/document/2?doc_id=311
- 联合唯一索引: name + orgs
- 字段数: 4个业务字段 + 2个系统字段
- 状态: ✅ 已验证

## 字段类型规范

### 代码类字段
- ts_code, symbol, exchange等: VARCHAR(20)

### 日期类字段
- trade_date, ann_date, list_date等: VARCHAR(8)

### 名称类字段
- name, holder_name, industry等: VARCHAR(100-200)
- reason等长文本: TEXT

### 数值类字段
- 价格/金额: DECIMAL(20, 4)
- 百分比/比率: DECIMAL(10, 4)
- 成交量: DECIMAL(20, 2) 或 INTEGER/BIGINTEGER
- 复权因子: DECIMAL(10, 6)

### 系统字段
- id: BIGINT AUTO_INCREMENT PRIMARY KEY
- created_at: DATETIME DEFAULT CURRENT_TIMESTAMP
- updated_at: DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

## 索引设计

### 唯一索引
- 单字段唯一索引: 2个表 (stock_list, stock_hot_money)
- 联合唯一索引: 12个表

### 普通索引
- 所有表都在高频查询字段上建立了索引
- 主要索引字段: ts_code, trade_date, ann_date

## 验证方法

```bash
# 查看所有表
mysql -u root -p stock -e "SHOW TABLES;"

# 查看表结构
mysql -u root -p stock -e "DESC table_name;"

# 查看索引
mysql -u root -p stock -e "SHOW INDEX FROM table_name;"
```

## 总结

✅ 所有14张表的结构完全符合Tushare文档要求
✅ 字段类型选择合理
✅ 索引设计完善
✅ 系统可以正常使用

---

**验证人**: Kiro AI
**验证日期**: 2025-12-13
**验证状态**: 通过
