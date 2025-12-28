from sqlalchemy import Column, String, Integer, Text, DateTime, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class StockConceptAnalysis(Base):
    """股票概念关联分析表"""
    __tablename__ = 'stock_concept_analysis'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    ts_code = Column(String(20), nullable=False, comment='股票代码')
    stock_name = Column(String(50), nullable=False, comment='股票名称')
    concept_name = Column(String(100), nullable=False, comment='概念名称')
    relevance_score = Column(Integer, nullable=False, comment='关联度(0-100)')
    relevance_desc = Column(Text, comment='关联性说明')
    evidence = Column(Text, comment='具体事项/佐证材料')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'concept_name', name='uk_stock_concept'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_concept_name', 'concept_name'),
        {'comment': '股票概念关联分析表'}
    )
