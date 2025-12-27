# Tushare API 文档链接清单

需要根据以下14个接口文档创建正确的数据模型：

## 1. 股票列表 (stock_list)
- 接口名: stock_basic
- 文档链接: https://tushare.pro/document/2?doc_id=25
- 表名: stock_list
- 唯一索引: ts_code

## 2. 股东持股 (stock_holder)
- 接口名: top10_holders
- 文档链接: https://tushare.pro/document/2?doc_id=61
- 表名: stock_holder
- 联合唯一索引: ts_code + ann_date + holder_name

## 3. 日线行情 (stock_daily)
- 接口名: daily
- 文档链接: https://tushare.pro/document/2?doc_id=27
- 表名: stock_daily
- 联合唯一索引: ts_code + trade_date

## 4. 股票每日筹码 (stock_chip)
- 接口名: cyq_chips
- 文档链接: https://tushare.pro/document/2?doc_id=294
- 表名: stock_chip
- 联合唯一索引: ts_code + trade_date + price
- 注意: 输出字段只有4个 (ts_code, trade_date, price, percent)

## 5. 股票技术面因子 (stock_tech_factor)
- 接口名: stk_factor
- 文档链接: https://tushare.pro/document/2?doc_id=296
- 表名: stock_tech_factor
- 联合唯一索引: ts_code + trade_date

## 6. 个股资金流向 (stock_money_flow)
- 接口名: moneyflow
- 文档链接: https://tushare.pro/document/2?doc_id=170
- 表名: stock_money_flow
- 联合唯一索引: ts_code + trade_date

## 7. 同花顺板块资金流向 (block_ths_money_flow)
- 接口名: ths_hot
- 文档链接: https://tushare.pro/document/2?doc_id=371
- 表名: block_ths_money_flow
- 联合唯一索引: trade_date + block_code

## 8. 同花顺行业资金流向 (industry_ths_money_flow)
- 接口名: ths_industry
- 文档链接: https://tushare.pro/document/2?doc_id=343
- 表名: industry_ths_money_flow
- 联合唯一索引: trade_date + industry

## 9. 龙虎榜每日统计单 (stock_lhb_daily)
- 接口名: top_list
- 文档链接: https://tushare.pro/document/2?doc_id=106
- 表名: stock_lhb_daily
- 联合唯一索引: ts_code + trade_date

## 10. 龙虎榜机构交易单 (stock_lhb_inst)
- 接口名: top_inst
- 文档链接: https://tushare.pro/document/2?doc_id=107
- 表名: stock_lhb_inst
- 联合唯一索引: ts_code + trade_date + exalter

## 11. 股票涨跌停和炸板数据 (stock_limit_status)
- 接口名: limit_list_d
- 文档链接: https://tushare.pro/document/2?doc_id=298
- 表名: stock_limit_status
- 联合唯一索引: ts_code + trade_date

## 12. 涨停股票连板天梯 (stock_limit_ladder)
- 接口名: limit_list
- 文档链接: https://tushare.pro/document/2?doc_id=356
- 表名: stock_limit_ladder
- 联合唯一索引: ts_code + trade_date

## 13. 涨停板块最强统计 (block_limit_strong)
- 接口名: ths_hot_rank
- 文档链接: https://tushare.pro/document/2?doc_id=357
- 表名: block_limit_strong
- 联合唯一索引: trade_date + ts_code

## 14. 股票游资名录 (stock_hot_money)
- 接口名: hot_inst_cons
- 文档链接: https://tushare.pro/document/2?doc_id=311
- 表名: stock_hot_money
- 唯一索引: name + orgs

---

## 下一步操作

我需要逐个访问这些链接，查看"输出参数"部分，然后创建正确的ORM模型。

每个模型需要：
1. 严格按照文档的输出参数创建字段
2. 字段类型根据文档说明选择合适的SQL类型
3. 添加正确的唯一索引
4. 添加created_at和updated_at系统字段
