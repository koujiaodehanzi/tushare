from repositories.base_repository import BaseRepository
from models.stock_concept_analysis import StockConceptAnalysis
from typing import List, Optional


class StockConceptAnalysisRepository(BaseRepository):
    """股票概念分析数据访问层"""
    
    def __init__(self, db_session):
        super().__init__(StockConceptAnalysis, db_session)
    
    def get_by_stock(self, ts_code: str) -> List[StockConceptAnalysis]:
        """
        查询股票的所有概念分析
        
        Args:
            ts_code: 股票代码
            
        Returns:
            概念分析列表
        """
        return self.db.query(StockConceptAnalysis).filter(
            StockConceptAnalysis.ts_code == ts_code
        ).order_by(StockConceptAnalysis.relevance_score.desc()).all()
    
    def get_by_stock_and_concept(self, ts_code: str, concept_name: str) -> Optional[StockConceptAnalysis]:
        """
        查询股票特定概念的分析
        
        Args:
            ts_code: 股票代码
            concept_name: 概念名称
            
        Returns:
            概念分析记录，不存在返回None
        """
        return self.db.query(StockConceptAnalysis).filter(
            StockConceptAnalysis.ts_code == ts_code,
            StockConceptAnalysis.concept_name == concept_name
        ).first()
    
    def batch_upsert(self, records: List[dict]):
        """
        批量插入或更新概念分析
        
        Args:
            records: 记录列表，每条记录包含ts_code, stock_name, concept_name等字段
        """
        if not records:
            return
        
        for record in records:
            existing = self.get_by_stock_and_concept(
                record['ts_code'], 
                record['concept_name']
            )
            
            if existing:
                # 更新
                for key, value in record.items():
                    setattr(existing, key, value)
            else:
                # 插入
                new_record = StockConceptAnalysis(**record)
                self.db.add(new_record)
        
        self.db.commit()
    
    def delete_by_stock(self, ts_code: str):
        """
        删除股票的所有概念分析
        
        Args:
            ts_code: 股票代码
        """
        self.db.query(StockConceptAnalysis).filter(
            StockConceptAnalysis.ts_code == ts_code
        ).delete()
        self.db.commit()
