# Tushare股票数据采集系统

## 项目简介

这是一个基于Tushare Pro API的股票数据采集、存储、处理和展示系统，采用分层架构设计。

## 系统架构

```
tushare/
├── config/              # 配置文件
│   ├── __init__.py
│   └── config.yaml      # 数据库、Tushare配置
├── models/              # 数据模型（ORM）
│   ├── __init__.py
│   ├── stock_list.py    # 股票列表模型
│   ├── stock_holder.py  # 股东持股模型
│   ├── stock_daily.py   # 日线行情模型
│   └── remaining_models.py  # 其他11个模型
├── repositories/        # 仓储层
│   ├── __init__.py
│   ├── base_repository.py
│   ├── stock_list_repository.py
│   └── ...              # 其他Repository
├── services/            # 业务逻辑层
│   ├── tushare_client.py    # Tushare API封装
│   ├── data_access/         # 数据接入模块
│   │   ├── __init__.py
│   │   └── data_access_service.py
│   └── data_sync/           # 数据同步模块
│       ├── __init__.py
│       └── data_sync_service.py
├── api/                 # 对外接口模块
│   └── app.py           # Flask API
├── utils/               # 工具类
│   ├── __init__.py
│   ├── db.py            # 数据库连接
│   ├── logger.py        # 日志工具
│   ├── rate_limiter.py  # 限流器
│   └── retry.py         # 重试装饰器
├── init_db.py           # 数据库初始化脚本
├── main.py              # 主入口
└── README.md            # 项目文档
```

## 数据模型

系统包含14个数据模型：

1. **stock_list** - 股票列表
2. **stock_holder** - 股东持股
3. **stock_daily** - 日线行情
4. **stock_chip** - 股票每日筹码
5. **stock_tech_factor** - 股票技术面因子
6. **stock_money_flow** - 个股资金流向
7. **block_ths_money_flow** - 同花顺板块资金流向
8. **industry_ths_money_flow** - 同花顺行业资金流向
9. **stock_lhb_daily** - 龙虎榜每日统计单
10. **stock_lhb_inst** - 龙虎榜机构交易单
11. **stock_limit_status** - 股票涨跌停和炸板数据
12. **stock_limit_ladder** - 涨停股票连板天梯
13. **block_limit_strong** - 涨停板块最强统计
14. **stock_hot_money** - 股票游资名录

## 安装部署

### 1. 安装依赖

```bash
pip3 install tushare sqlalchemy pymysql pyyaml flask
```

### 2. 配置文件

编辑 `config/config.yaml`，填写数据库和Tushare配置：

```yaml
database:
  host: localhost
  port: 3306
  user: root
  password: "Jk98!po78&lm"
  database: stock
  charset: utf8mb4

tushare:
  token: "your_tushare_token_here"  # 替换为你的Tushare token
  api_limit: 120
  retry_times: 3
  retry_delay: 1
```

### 3. 初始化数据库

```bash
python3 init_db.py
```

### 4. 启动服务

```bash
python3 main.py
```

服务将在 `http://localhost:5001` 启动

## API接口

### 1. 健康检查

```bash
GET http://localhost:5001/health
```

### 2. 基础数据全量同步

同步股票列表、股东持股、游资名录

```bash
POST http://localhost:5001/api/sync/base
```

### 3. 每日数据同步

#### 按指定日期同步

```bash
POST http://localhost:5001/api/sync/daily
Content-Type: application/json

{
  "trade_date": "20231213"
}
```

#### 按日期范围同步

```bash
POST http://localhost:5001/api/sync/daily
Content-Type: application/json

{
  "start_date": "20231201",
  "end_date": "20231213"
}
```

## 核心功能

### 仓储层

每个模型都有对应的Repository，提供：
- 批量插入/更新（upsert）
- 条件查询
- 数据过滤

### 数据接入模块

封装Tushare Pro API的14个接口：
- 自动限流（每分钟120次）
- 失败重试（最多3次）
- 日志记录

### 数据同步模块

#### 基础数据同步
- 股票列表全量同步
- 股东持股增量同步（只同步最新ann_date）
- 游资名录全量同步（orgs字段自动拆分）

#### 每日数据同步
- 支持按日期或日期范围同步
- 11类交易数据自动同步
- 批量处理提升效率

## 技术特性

- **ORM框架**: SQLAlchemy
- **数据库**: MySQL
- **API限流**: 自定义限流器，避免触发Tushare封禁
- **失败重试**: 自动重试机制
- **批量操作**: 使用 `INSERT ... ON DUPLICATE KEY UPDATE` 实现高效upsert
- **日志记录**: 完整的操作日志

## 注意事项

1. **Tushare Token**: 需要在 `config/config.yaml` 中配置有效的Tushare token
2. **API限流**: 默认每分钟120次调用，根据你的积分等级调整
3. **数据量**: 全量同步需要较长时间，建议分批执行
4. **数据库**: 确保MySQL服务正常运行，数据库 `stock` 已创建

## 使用示例

### 1. 初始化系统

```bash
# 创建数据库表
python3 init_db.py

# 启动API服务
python3 main.py
```

### 2. 同步基础数据

```bash
curl -X POST http://localhost:5001/api/sync/base
```

### 3. 同步每日数据

```bash
# 同步指定日期
curl -X POST http://localhost:5000/api/sync/daily \
  -H "Content-Type: application/json" \
  -d '{"trade_date": "20231213"}'

# 同步日期范围
curl -X POST http://localhost:5000/api/sync/daily \
  -H "Content-Type: application/json" \
  -d '{"start_date": "20231201", "end_date": "20231213"}'
```

## 日志

日志级别：INFO
日志格式：`时间 - 模块名 - 级别 - 消息`

查看日志可以了解：
- API调用情况
- 数据同步进度
- 错误信息

## 扩展开发

### 添加新的数据模型

1. 在 `models/` 创建新模型
2. 在 `repositories/` 创建对应Repository
3. 在 `services/data_access/` 添加API接口
4. 在 `services/data_sync/` 添加同步逻辑
5. 在 `api/app.py` 添加HTTP接口

## 许可证

MIT License
