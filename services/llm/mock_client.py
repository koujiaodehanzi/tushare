import json
from typing import Optional
from .base_llm_client import BaseLLMClient
from utils.logger import logger


class MockLLMClient(BaseLLMClient):
    """模拟LLM客户端，用于测试"""
    
    def _validate_config(self):
        """验证配置"""
        pass
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None) -> str:
        """
        返回模拟的分析结果
        """
        logger.info(f"使用模拟LLM客户端生成分析")
        
        # 从prompt中提取概念列表
        concepts = []
        for line in user_prompt.split('\n'):
            if line.strip().startswith('- '):
                concepts.append(line.strip()[2:])
        
        # 生成模拟数据
        mock_data = []
        for i, concept in enumerate(concepts):
            score = 85 - i * 5  # 递减的分数
            mock_data.append({
                "concept": concept,
                "score": max(30, score),
                "description": f"该股票在{concept}领域有重要布局，相关业务占比较高",
                "evidence": f"公司主营业务涉及{concept}相关产品和服务，已有多个项目落地"
            })
        
        return json.dumps(mock_data, ensure_ascii=False)
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return "mock-model"
