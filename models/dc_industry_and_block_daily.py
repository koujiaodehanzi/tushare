from sqlalchemy import Column, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DcIndustryAndBlockDaily(Base):
    __tablename__ = 'dc_industry_and_block_daily'
    
    ts_code = Column(String(20), primary_key=True, comment='板块代码')
    trade_date = Column(Date, primary_key=True, comment='交易日')
    close = Column(Float, comment='收盘点位')
    open = Column(Float, comment='开盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    change = Column(Float, comment='涨跌点位')
    pct_change = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量')
    amount = Column(Float, comment='成交额')
    swing = Column(Float, comment='振幅')
    turnover_rate = Column(Float, comment='换手率')
