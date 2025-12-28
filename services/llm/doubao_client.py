import requests
from typing import Optional
from .base_llm_client import BaseLLMClient
from utils.logger import logger


class DoubaoLLMClient(BaseLLMClient):
    """豆包大模型客户端"""
    
    def _validate_config(self):
        """验证配置"""
        required_keys = ['api_key', 'endpoint', 'model']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"豆包配置缺少必需参数: {key}")
    
    def chat(self, 
             system_prompt: str, 
             user_prompt: str,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None) -> str:
        """
        调用豆包API进行对话
        
        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            豆包返回的文本内容
        """
        url = self.config['endpoint']
        headers = {
            'Authorization': f"Bearer {self.config['api_key']}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.config['model'],
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': temperature,
            'stream': False  # 不使用流式响应，便于解析JSON
        }
        
        # 如果配置了max_completion_tokens，添加到payload
        if max_tokens or self.config.get('max_completion_tokens'):
            payload['max_completion_tokens'] = max_tokens or self.config.get('max_completion_tokens', 65535)
        
        # 重试配置
        max_retries = 3
        retry_delay = 2  # 初始延迟2秒
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"第 {attempt + 1} 次重试...")
                    import time
                    time.sleep(retry_delay * attempt)  # 指数退避
                
                logger.info(f"调用豆包API: model={self.config['model']}")
                logger.info(f"请求URL: {url}")
                logger.info(f"请求Headers: {headers}")
                logger.info(f"请求Payload: {payload}")
                
                # 禁用代理
                session = requests.Session()
                session.trust_env = False
                
                response = session.post(
                    url, 
                    json=payload, 
                    headers=headers,
                    timeout=self.config.get('timeout', 30),
                    verify=True,
                    proxies={'http': None, 'https': None}  # 明确禁用代理
                )
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"响应状态码: {response.status_code}")
                logger.info(f"响应内容: {result}")
                
                content = result['choices'][0]['message']['content']
                logger.info(f"豆包API调用成功，返回内容长度: {len(content)}")
                return content
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    # 请求过于频繁，需要重试
                    logger.warning(f"豆包API请求频率过高(429)，等待后重试...")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        raise Exception(f"豆包API请求频率过高，已重试{max_retries}次，请稍后再试")
                else:
                    logger.error(f"豆包API HTTP错误: {str(e)}")
                    raise Exception(f"豆包API调用失败: {str(e)}")
            except requests.exceptions.SSLError as e:
                logger.error(f"豆包API SSL错误: {str(e)}")
                raise Exception(f"豆包API SSL连接错误，请检查网络环境或API配置")
            except requests.exceptions.Timeout as e:
                logger.error(f"豆包API超时: {str(e)}")
                raise Exception(f"豆包API调用超时，请稍后重试")
            except requests.exceptions.RequestException as e:
                logger.error(f"豆包API调用失败: {str(e)}")
                raise Exception(f"豆包API调用失败: {str(e)}")
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config['model']
