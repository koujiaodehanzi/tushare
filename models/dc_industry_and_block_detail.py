from sqlalchemy import Column, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DcIndustryAndBlockDetail(Base):
    __tablename__ = 'dc_industry_and_block_detail'
    
    trade_date = Column(Date, primary_key=True, comment='交易日期')
    ts_code = Column(String(20), primary_key=True, comment='概念代码')
    con_code = Column(String(10), primary_key=True, comment='成分代码')
    name = Column(String(100), comment='成分股名称')
