import yaml
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from utils.db import get_db_session
from utils.logger import logger
from repositories.stock_concept_analysis_repository import StockConceptAnalysisRepository
from services.llm import LLMClientFactory


class ConceptAnalysisService:
    """概念分析服务"""
    
    def __init__(self):
        self.db = get_db_session()
        self.repository = StockConceptAnalysisRepository(self.db)
        self._load_config()
        self._init_llm_client()
    
    def _load_config(self):
        """加载配置"""
        config_path = Path(__file__).parent.parent / 'config' / 'llm_config.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def _init_llm_client(self):
        """初始化LLM客户端"""
        provider = self.config['llm']['provider']
        provider_config = self.config['llm'][provider]
        self.llm_client = LLMClientFactory.create_client(provider, provider_config)
    
    def get_analysis(self, ts_code: str) -> Dict[str, Any]:
        """
        获取股票概念分析数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            {
                'has_data': bool,
                'data': [
                    {
                        'concept': str,
                        'score': int,
                        'description': str,
                        'evidence': str
                    }
                ]
            }
        """
        records = self.repository.get_by_stock(ts_code)
        
        if not records:
            return {'has_data': False, 'data': []}
        
        data = [
            {
                'concept': r.concept_name,
                'score': r.relevance_score,
                'description': r.relevance_desc,
                'evidence': r.evidence
            }
            for r in records
        ]
        
        return {'has_data': True, 'data': data}
    
    def generate_analysis(self, ts_code: str, stock_name: str, concepts: List[str]) -> List[Dict[str, Any]]:
        """
        调用LLM生成概念分析
        
        Args:
            ts_code: 股票代码
            stock_name: 股票名称
            concepts: 概念列表
            
        Returns:
            分析结果列表
        """
        # 构建prompt
        system_prompt = self.config['prompts']['stock_concept_analysis']['system_prompt']
        user_prompt_template = self.config['prompts']['stock_concept_analysis']['user_prompt_template']
        
        concepts_str = '\n'.join([f"- {c}" for c in concepts])
        user_prompt = user_prompt_template.format(
            stock_name=stock_name,
            ts_code=ts_code,
            concepts=concepts_str
        )
        
        logger.info(f"开始生成概念分析: {stock_name}({ts_code}), 概念数量: {len(concepts)}")
        
        # 调用LLM
        try:
            response = self.llm_client.chat(system_prompt, user_prompt, temperature=0.3)
            logger.info(f"LLM返回内容: {response[:200]}...")
            
            # 解析响应
            analysis_data = self._parse_llm_response(response)
            
            # 保存到数据库
            self._save_analysis(ts_code, stock_name, analysis_data)
            
            logger.info(f"概念分析生成完成: {stock_name}({ts_code}), 成功解析 {len(analysis_data)} 个概念")
            
            # 从数据库重新查询，确保按关联度排序
            sorted_data = self.get_analysis(ts_code)
            return sorted_data['data']
            
        except Exception as e:
            logger.error(f"生成概念分析失败: {str(e)}")
            raise
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """
        解析LLM返回的JSON
        
        Args:
            response: LLM返回的文本
            
        Returns:
            解析后的数据列表
        """
        # 尝试提取JSON（可能包含在markdown代码块中）
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = response.strip()
        
        try:
            data = json.loads(json_str)
            
            # 验证数据格式
            if not isinstance(data, list):
                raise ValueError("返回数据不是数组格式")
            
            validated_data = []
            for item in data:
                if not all(k in item for k in ['concept', 'score', 'description', 'evidence']):
                    logger.warning(f"跳过格式不完整的数据: {item}")
                    continue
                
                # 验证score范围
                score = int(item['score'])
                if not 0 <= score <= 100:
                    logger.warning(f"评分超出范围，调整为合理值: {score}")
                    score = max(0, min(100, score))
                
                validated_data.append({
                    'concept': str(item['concept']),
                    'score': score,
                    'description': str(item['description']),
                    'evidence': str(item['evidence'])
                })
            
            return validated_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {str(e)}, 原始内容: {response}")
            raise ValueError(f"LLM返回内容不是有效的JSON格式")
    
    def _save_analysis(self, ts_code: str, stock_name: str, analysis_data: List[Dict[str, Any]]):
        """
        保存分析结果到数据库
        
        Args:
            ts_code: 股票代码
            stock_name: 股票名称
            analysis_data: 分析数据
        """
        records = [
            {
                'ts_code': ts_code,
                'stock_name': stock_name,
                'concept_name': item['concept'],
                'relevance_score': item['score'],
                'relevance_desc': item['description'],
                'evidence': item['evidence']
            }
            for item in analysis_data
        ]
        
        self.repository.batch_upsert(records)
        logger.info(f"保存概念分析到数据库: {len(records)} 条记录")
    
    def reload_config(self):
        """重新加载配置（用于配置更新后）"""
        self._load_config()
        self._init_llm_client()
        logger.info("配置已重新加载")
    
    def get_prompt_config(self) -> Dict[str, Any]:
        """获取当前prompt配置"""
        return self.config['prompts']['stock_concept_analysis']
    
    def update_prompt_config(self, system_prompt: str, user_prompt_template: str):
        """
        更新prompt配置
        
        Args:
            system_prompt: 系统提示词
            user_prompt_template: 用户提示词模板
        """
        config_path = Path(__file__).parent.parent / 'config' / 'llm_config.yaml'
        
        self.config['prompts']['stock_concept_analysis']['system_prompt'] = system_prompt
        self.config['prompts']['stock_concept_analysis']['user_prompt_template'] = user_prompt_template
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        
        logger.info("Prompt配置已更新")
    
    def delete_analysis(self, ts_code: str):
        """
        删除股票的概念分析数据
        
        Args:
            ts_code: 股票代码
        """
        self.repository.delete_by_stock(ts_code)
        logger.info(f"已删除股票 {ts_code} 的概念分析数据")
