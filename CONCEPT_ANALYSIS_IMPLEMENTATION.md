# 概念分析功能实现文档

## 功能概述

实现了股票概念关联性分析功能，通过调用大模型API（豆包）分析股票与概念的关联度，并提供可视化展示。

## 技术架构

### 1. 数据库层
- **表名**: `stock_concept_analysis`
- **字段**:
  - `id`: 主键
  - `ts_code`: 股票代码
  - `stock_name`: 股票名称
  - `concept_name`: 概念名称
  - `relevance_score`: 关联度(0-100)
  - `relevance_desc`: 关联性说明
  - `evidence`: 具体事项/佐证材料
  - `created_at`: 创建时间
  - `updated_at`: 更新时间

### 2. LLM抽象层（支持多模型切换）

#### 2.1 基类
- `services/llm/base_llm_client.py`: 抽象基类，定义统一接口

#### 2.2 实现类
- `services/llm/doubao_client.py`: 豆包大模型客户端

#### 2.3 工厂类
- `services/llm/llm_factory.py`: 工厂模式，支持动态注册新模型

### 3. 配置管理
- `config/llm_config.yaml`: LLM配置和Prompt模板
- `config/llm_config.yaml.template`: 配置模板

### 4. 数据访问层
- `repositories/stock_concept_analysis_repository.py`: 数据库操作

### 5. 业务服务层
- `services/concept_analysis_service.py`: 核心业务逻辑
  - 查询已有分析数据
  - 调用LLM生成分析
  - 解析LLM响应
  - 保存到数据库

### 6. API接口
- `GET /api/concept/analysis?ts_code=xxx`: 查询概念分析
- `POST /api/concept/analysis`: 生成概念分析
- `GET /api/config/prompt`: 获取prompt配置
- `PUT /api/config/prompt`: 更新prompt配置

### 7. 前端UI
- 点击概念列显示浮动面板
- 展示关联度、说明、佐证
- 无数据时显示"获取数据"按钮
- 进度条可视化关联度

## 使用说明

### 1. 配置豆包API

复制配置模板：
```bash
cp config/llm_config.yaml.template config/llm_config.yaml
```

编辑 `config/llm_config.yaml`，填写：
- `api_key`: 豆包API密钥
- `model`: 豆包endpoint ID

### 2. 使用功能

1. 访问概念筛选页面: http://localhost:5001/concept.html
2. 筛选股票后，点击"所属概念"列
3. 右侧弹出浮动面板
4. 如无数据，点击"获取数据"按钮
5. 等待大模型生成分析（约10-30秒）
6. 查看分析结果

## 扩展其他大模型

### 步骤1: 创建客户端类

```python
# services/llm/openai_client.py
from .base_llm_client import BaseLLMClient

class OpenAILLMClient(BaseLLMClient):
    def _validate_config(self):
        required_keys = ['api_key', 'model']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"OpenAI配置缺少必需参数: {key}")
    
    def chat(self, system_prompt, user_prompt, temperature=0.7, max_tokens=None):
        # 实现OpenAI API调用逻辑
        pass
    
    def get_model_name(self):
        return self.config['model']
```

### 步骤2: 注册到工厂

```python
# services/llm/llm_factory.py
from .openai_client import OpenAILLMClient

class LLMClientFactory:
    _clients = {
        'doubao': DoubaoLLMClient,
        'openai': OpenAILLMClient,  # 添加这行
    }
```

### 步骤3: 配置文件

```yaml
# config/llm_config.yaml
llm:
  provider: openai  # 切换到OpenAI
  
  openai:
    api_key: "sk-xxx"
    model: "gpt-4"
    timeout: 30
```

## 注意事项

1. **API费用**: 每次生成分析会调用大模型API，产生费用
2. **数据缓存**: 已生成的分析会保存到数据库，避免重复调用
3. **超时设置**: 默认30秒超时，可在配置中调整
4. **Prompt优化**: 可通过API或直接编辑配置文件优化prompt
5. **概念数量**: 建议每次分析不超过20个概念，避免响应过长

## 文件清单

```
models/
  stock_concept_analysis.py          # 数据模型

services/
  llm/
    __init__.py                       # 模块导出
    base_llm_client.py                # 抽象基类
    doubao_client.py                  # 豆包客户端
    llm_factory.py                    # 工厂类
  concept_analysis_service.py         # 业务服务

repositories/
  stock_concept_analysis_repository.py # 数据访问

api/
  concept_api.py                      # API接口（新增4个端点）

config/
  llm_config.yaml                     # LLM配置
  llm_config.yaml.template            # 配置模板

static/
  concept.html                        # 前端页面（新增浮动面板）
```

## 后续优化建议

1. 添加批量生成功能
2. 支持手动编辑分析结果
3. 添加分析历史记录
4. 支持定期自动更新
5. 添加分析质量评分
6. 支持导出分析报告
