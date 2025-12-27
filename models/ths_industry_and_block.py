from sqlalchemy import Column, String, Integer, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ThsIndustryAndBlock(Base):
    __tablename__ = 'ths_industry_and_block'
    
    ts_code = Column(String(20), primary_key=True, comment='指数代码')
    name = Column(String(100), comment='名称')
    count = Column(Integer, comment='成分个数')
    exchange = Column(String(10), comment='交易所')
    list_date = Column(String(8), comment='上市日期')
    type = Column(String(10), comment='指数类型')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        {'comment': '同花顺行业和概念板块'}
    )
