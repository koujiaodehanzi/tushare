# 快速开始指南

## 1. 系统要求

- Python 3.9+
- MySQL 5.7+
- Tushare Pro账号（需要2000积分以上）

## 2. 安装步骤

### 2.1 安装依赖

```bash
pip3 install -r requirements.txt
```

或者手动安装：

```bash
pip3 install tushare sqlalchemy pymysql pyyaml flask
```

### 2.2 配置数据库

确保MySQL服务正常运行，并创建数据库：

```sql
CREATE DATABASE stock CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2.3 配置Tushare Token

编辑 `config/config.yaml`，将 `your_token_here` 替换为你的真实token：

```yaml
tushare:
  token: "your_real_token_here"  # 在 https://tushare.pro 获取
```

### 2.4 初始化数据库表

```bash
python3 init_db.py
```

### 2.5 运行系统测试

```bash
python3 test_system.py
```

如果所有测试通过，说明系统配置正确。

## 3. 启动服务

```bash
python3 main.py
```

服务将在 `http://localhost:5001` 启动

## 4. 测试API

### 4.1 健康检查

```bash
curl http://localhost:5001/health
```

预期返回：
```json
{
  "status": "ok",
  "timestamp": "2025-12-13T01:00:00.000000"
}
```

### 4.2 同步基础数据

```bash
curl -X POST http://localhost:5001/api/sync/base
```

这将同步：
- 股票列表（约5001只股票）
- 股东持股（每只股票的前十大股东）
- 游资名录

**注意**：基础数据同步需要较长时间（约30-60分钟），请耐心等待。

### 4.3 同步每日数据

同步指定日期的数据：

```bash
curl -X POST http://localhost:5001/api/sync/daily \
  -H "Content-Type: application/json" \
  -d '{"trade_date": "20231213"}'
```

同步日期范围的数据：

```bash
curl -X POST http://localhost:5001/api/sync/daily \
  -H "Content-Type: application/json" \
  -d '{"start_date": "20231201", "end_date": "20231213"}'
```

## 5. 查看数据

连接MySQL数据库查看同步的数据：

```bash
mysql -u root -p stock
```

查询示例：

```sql
-- 查看股票列表
SELECT * FROM stock_list LIMIT 10;

-- 查看某只股票的日线行情
SELECT * FROM stock_daily WHERE ts_code = '000001.SZ' ORDER BY trade_date DESC LIMIT 10;

-- 查看龙虎榜数据
SELECT * FROM stock_lhb_daily WHERE trade_date = '20231213';
```

## 6. 常见问题

### Q1: Tushare API调用失败

**A**: 检查以下几点：
1. Token是否正确配置
2. 账号积分是否足够（需要2000积分以上）
3. 是否触发API限流（默认每分钟120次）

### Q2: 数据库连接失败

**A**: 检查：
1. MySQL服务是否启动
2. 数据库名称、用户名、密码是否正确
3. 数据库是否已创建

### Q3: 同步速度慢

**A**: 这是正常现象，因为：
1. Tushare API有频率限制
2. 数据量大（5001+只股票）
3. 系统自动限流避免被封禁

建议：
- 基础数据同步只需执行一次
- 每日数据可以定时同步（如每天收盘后）
- 使用日期范围同步时，不要跨度太大

### Q4: 某些接口返回空数据

**A**: 可能原因：
1. 该日期不是交易日
2. 该股票当天停牌
3. 某些数据需要更高积分权限

## 7. 下一步

- 根据需求添加新的数据模型
- 实现数据分析和可视化
- 添加定时任务自动同步
- 开发前端页面展示数据

## 8. 技术支持

- Tushare文档：https://tushare.pro/document/2
- 项目README：README.md
- 问题反馈：提交Issue

## 9. 注意事项

⚠️ **重要提示**：

1. **API限流**：严格遵守Tushare API调用频率限制，避免账号被封禁
2. **数据安全**：不要将config.yaml中的token提交到公开仓库
3. **数据库备份**：定期备份数据库，避免数据丢失
4. **合法使用**：仅用于个人学习和研究，不得用于商业用途

## 10. 许可证

MIT License
