from sqlalchemy import Column, String, Float, Integer, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DcIndustryAndBlock(Base):
    __tablename__ = 'dc_industry_and_block'
    
    ts_code = Column(String(20), primary_key=True, comment='概念代码')
    trade_date = Column(Date, primary_key=True, comment='交易日期')
    name = Column(String(100), comment='概念名称')
    leading = Column(String(100), comment='领涨股票名称')
    leading_code = Column(String(10), comment='领涨股票代码')
    pct_change = Column(Float, comment='涨跌幅')
    leading_pct = Column(Float, comment='领涨股票涨跌幅')
    total_mv = Column(Float, comment='总市值(万元)')
    turnover_rate = Column(Float, comment='换手率')
    up_num = Column(Integer, comment='上涨家数')
    down_num = Column(Integer, comment='下降家数')
