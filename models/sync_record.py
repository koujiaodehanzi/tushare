from sqlalchemy import Column, BigInteger, String, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from utils.db import Base

class SyncRecord(Base):
    """数据同步记录表"""
    __tablename__ = 'sync_record'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    sync_type = Column(String(50), nullable=False, comment='同步类型')
    status = Column(String(20), nullable=False, comment='同步状态: success/failed')
    record_count = Column(BigInteger, comment='同步记录数')
    error_msg = Column(String(500), comment='错误信息')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('trade_date', 'sync_type', name='uk_sync_record'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_sync_type', 'sync_type'),
    )
