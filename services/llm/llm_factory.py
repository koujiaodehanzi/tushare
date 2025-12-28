from typing import Dict, Any
from .base_llm_client import BaseLLMClient
from .doubao_client import DoubaoLLMClient
from .mock_client import MockLLMClient
from utils.logger import logger


class LLMClientFactory:
    """LLM客户端工厂类"""
    
    _clients = {
        'doubao': DoubaoLLMClient,
        'mock': MockLLMClient,
        # 后续可以添加其他模型
        # 'openai': OpenAILLMClient,
        # 'qwen': QwenLLMClient,
        # 'glm': GLMLLMClient,
    }
    
    @classmethod
    def create_client(cls, provider: str, config: Dict[str, Any]) -> BaseLLMClient:
        """
        创建LLM客户端实例
        
        Args:
            provider: 提供商名称 (doubao, openai, qwen等)
            config: 配置字典
            
        Returns:
            LLM客户端实例
            
        Raises:
            ValueError: 不支持的提供商
        """
        if provider not in cls._clients:
            raise ValueError(f"不支持的LLM提供商: {provider}，支持的提供商: {list(cls._clients.keys())}")
        
        client_class = cls._clients[provider]
        logger.info(f"创建LLM客户端: provider={provider}, model={config.get('model', 'unknown')}")
        return client_class(config)
    
    @classmethod
    def register_client(cls, provider: str, client_class: type):
        """
        注册新的LLM客户端类
        
        Args:
            provider: 提供商名称
            client_class: 客户端类（必须继承BaseLLMClient）
        """
        if not issubclass(client_class, BaseLLMClient):
            raise ValueError(f"客户端类必须继承BaseLLMClient")
        
        cls._clients[provider] = client_class
        logger.info(f"注册LLM客户端: {provider}")
