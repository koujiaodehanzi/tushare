from sqlalchemy import Column, BigInteger, String, DECIMAL, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from utils.db import Base

class StockChip(Base):
    """股票每日筹码分布模型 - 基于cyq_chips接口"""
    __tablename__ = 'stock_chip'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='股票代码')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    price = Column(DECIMAL(20, 4), nullable=False, comment='成本价格')
    percent = Column(DECIMAL(10, 4), comment='价格占比(%)')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', 'price', name='uk_chip'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )
