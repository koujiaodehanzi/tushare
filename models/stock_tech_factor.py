from sqlalchemy import Column, BigInteger, String, DECIMAL, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from utils.db import Base

class StockTechFactor(Base):
    """股票技术面因子模型 - 基于stk_factor接口"""
    __tablename__ = 'stock_tech_factor'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='股票代码')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    close = Column(DECIMAL(20, 4), comment='收盘价')
    open = Column(DECIMAL(20, 4), comment='开盘价')
    high = Column(DECIMAL(20, 4), comment='最高价')
    low = Column(DECIMAL(20, 4), comment='最低价')
    pre_close = Column(DECIMAL(20, 4), comment='昨收价')
    change = Column(DECIMAL(20, 4), comment='涨跌额')
    pct_change = Column(DECIMAL(10, 4), comment='涨跌幅')
    vol = Column(DECIMAL(20, 2), comment='成交量(手)')
    amount = Column(DECIMAL(20, 4), comment='成交额(千元)')
    adj_factor = Column(DECIMAL(20, 10), comment='复权因子')
    open_hfq = Column(DECIMAL(20, 4), comment='开盘价后复权')
    open_qfq = Column(DECIMAL(20, 4), comment='开盘价前复权')
    close_hfq = Column(DECIMAL(20, 4), comment='收盘价后复权')
    close_qfq = Column(DECIMAL(20, 4), comment='收盘价前复权')
    high_hfq = Column(DECIMAL(20, 4), comment='最高价后复权')
    high_qfq = Column(DECIMAL(20, 4), comment='最高价前复权')
    low_hfq = Column(DECIMAL(20, 4), comment='最低价后复权')
    low_qfq = Column(DECIMAL(20, 4), comment='最低价前复权')
    pre_close_hfq = Column(DECIMAL(20, 4), comment='昨收价后复权')
    pre_close_qfq = Column(DECIMAL(20, 4), comment='昨收价前复权')
    macd_dif = Column(DECIMAL(10, 4), comment='MACD_DIF')
    macd_dea = Column(DECIMAL(10, 4), comment='MACD_DEA')
    macd = Column(DECIMAL(10, 4), comment='MACD')
    kdj_k = Column(DECIMAL(10, 4), comment='KDJ_K')
    kdj_d = Column(DECIMAL(10, 4), comment='KDJ_D')
    kdj_j = Column(DECIMAL(10, 4), comment='KDJ_J')
    rsi_6 = Column(DECIMAL(10, 4), comment='RSI_6')
    rsi_12 = Column(DECIMAL(10, 4), comment='RSI_12')
    rsi_24 = Column(DECIMAL(10, 4), comment='RSI_24')
    boll_upper = Column(DECIMAL(20, 4), comment='BOLL_UPPER')
    boll_mid = Column(DECIMAL(20, 4), comment='BOLL_MID')
    boll_lower = Column(DECIMAL(20, 4), comment='BOLL_LOWER')
    cci = Column(DECIMAL(10, 4), comment='CCI')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uk_tech_factor'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )
