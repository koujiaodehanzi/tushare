# 同花顺板块功能快速使用指南

## 快速开始

### 1. 启动服务
```bash
cd /Users/wyk/selfspace/code/tushare
python3 main.py
```

服务将在 http://localhost:5001 启动

### 2. 使用Web界面

访问 http://localhost:5001，找到以下两个新增模块：

#### 📊 同花顺板块
- **板块代码**: 留空则同步全部，或输入特定代码如 `885800.TI`
- **市场类型**: 选择 A股/港股/美股 或全部
- **指数类型**: 选择 概念指数/行业指数/特色指数 或全部
- 点击"开始同步"

**示例**: 同步所有A股概念板块
- 板块代码: 留空
- 市场类型: A股
- 指数类型: 概念指数

#### 📋 同花顺板块成分
- **板块代码**: 必填，如 `885800.TI` (电子元件)
- 点击"开始同步"

**注意**: 每次同步会先删除该板块的旧成分，再插入新数据

### 3. 使用API接口

#### 同步板块数据
```bash
# 同步所有A股概念板块
curl -X POST http://localhost:5001/api/sync/ths_index \
  -H "Content-Type: application/json" \
  -d '{"exchange": "A", "type": "N"}'

# 同步特定板块
curl -X POST http://localhost:5001/api/sync/ths_index \
  -H "Content-Type: application/json" \
  -d '{"ts_code": "885800.TI"}'
```

#### 同步板块成分
```bash
curl -X POST http://localhost:5001/api/sync/ths_member \
  -H "Content-Type: application/json" \
  -d '{"ts_code": "885800.TI"}'
```

### 4. 查询数据

```sql
-- 查询所有板块
SELECT * FROM ths_industry_and_block;

-- 查询A股概念板块
SELECT * FROM ths_industry_and_block WHERE exchange='A' AND type='N';

-- 查询特定板块的成分股
SELECT * FROM ths_industry_and_block_detail WHERE ts_code='885800.TI';

-- 查询某只股票所属的所有板块
SELECT b.ts_code, b.name, b.type 
FROM ths_industry_and_block_detail d
JOIN ths_industry_and_block b ON d.ts_code = b.ts_code
WHERE d.con_code = '000001.SZ';
```

## 常见板块代码

| 代码 | 名称 | 类型 |
|------|------|------|
| 885800.TI | 电子元件 | 概念 |
| 885472.TI | 上海自贸区 | 概念 |
| 885788.TI | 网络直播 | 概念 |
| 885881.TI | 云办公 | 概念 |
| 885785.TI | 小米概念 | 概念 |

## 参数说明

### exchange (市场类型)
- `A`: A股
- `HK`: 港股
- `US`: 美股

### type (指数类型)
- `N`: 概念指数
- `I`: 行业指数
- `R`: 地域指数
- `S`: 同花顺特色指数
- `ST`: 同花顺风格指数
- `TH`: 同花顺主题指数
- `BB`: 同花顺宽基指数

## 运行测试

```bash
python3 test_ths_sync.py
```

测试脚本会自动执行：
1. 同步A股概念板块
2. 同步电子元件板块成分
3. 查询并验证数据

## 注意事项

1. **API权限**: 需要Tushare积分6000+
2. **调用频率**: 每分钟最多200次
3. **数据版权**: 归属同花顺，商业用途需授权
4. **成分更新**: 建议定期同步以保持数据最新

## 故障排查

### 问题1: 同步失败，提示权限不足
**解决**: 检查Tushare token积分是否达到6000

### 问题2: 数据为空
**解决**: 检查参数是否正确，某些板块可能不存在

### 问题3: 前端无响应
**解决**: 
1. 检查服务是否启动: `curl http://localhost:5001/health`
2. 查看日志: `tail -f /tmp/tushare_app.log`

## 技术支持

- 查看实现文档: `THS_IMPLEMENTATION.md`
- 查看API日志: `/tmp/tushare_app.log`
- Tushare文档: https://tushare.pro/document/2?doc_id=259
