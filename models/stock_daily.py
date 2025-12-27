from sqlalchemy import Column, BigInteger, String, DECIMAL, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from utils.db import Base

class StockDaily(Base):
    __tablename__ = 'stock_daily'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    open = Column(DECIMAL(20, 4), comment='开盘价')
    high = Column(DECIMAL(20, 4), comment='最高价')
    low = Column(DECIMAL(20, 4), comment='最低价')
    close = Column(DECIMAL(20, 4), comment='收盘价')
    pre_close = Column(DECIMAL(20, 4), comment='昨收价')
    change = Column(DECIMAL(20, 4), comment='涨跌额')
    pct_chg = Column(DECIMAL(10, 4), comment='涨跌幅')
    vol = Column(DECIMAL(20, 2), comment='成交量')
    amount = Column(DECIMAL(20, 4), comment='成交额')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uk_daily'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )
