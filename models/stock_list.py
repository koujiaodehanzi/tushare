from sqlalchemy import Column, BigInteger, String, DateTime, Index
from sqlalchemy.sql import func
from utils.db import Base

class StockList(Base):
    __tablename__ = 'stock_list'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), unique=True, nullable=False, comment='TS代码')
    symbol = Column(String(20), comment='股票代码')
    name = Column(String(100), comment='股票名称')
    area = Column(String(50), comment='地域')
    industry = Column(String(100), comment='所属行业')
    fullname = Column(String(200), comment='股票全称')
    enname = Column(String(200), comment='英文全称')
    cnspell = Column(String(50), comment='拼音缩写')
    market = Column(String(20), comment='市场类型')
    exchange = Column(String(20), comment='交易所代码')
    curr_type = Column(String(20), comment='交易货币')
    list_status = Column(String(10), comment='上市状态')
    list_date = Column(String(8), comment='上市日期')
    delist_date = Column(String(8), comment='退市日期')
    is_hs = Column(String(10), comment='是否沪深港通标的')
    act_name = Column(String(100), comment='实控人名称')
    act_ent_type = Column(String(100), comment='实控人企业性质')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_list_status', 'list_status'),
        Index('idx_industry', 'industry'),
        Index('idx_area', 'area'),
        Index('idx_market', 'market'),
    )
