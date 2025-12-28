from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMClient(ABC):
    """LLM客户端抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化LLM客户端
        
        Args:
            config: 配置字典，包含API密钥、endpoint等
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """验证配置是否完整"""
        pass
    
    @abstractmethod
    def chat(self, 
             system_prompt: str, 
             user_prompt: str,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None) -> str:
        """
        调用LLM进行对话
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数，控制随机性
            max_tokens: 最大token数
            
        Returns:
            LLM返回的文本内容
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """获取当前使用的模型名称"""
        pass
