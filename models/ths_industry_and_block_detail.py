from sqlalchemy import Column, String, Float, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ThsIndustryAndBlockDetail(Base):
    __tablename__ = 'ths_industry_and_block_detail'
    
    ts_code = Column(String(20), primary_key=True, comment='指数代码')
    con_code = Column(String(20), primary_key=True, comment='股票代码')
    con_name = Column(String(100), comment='股票名称')
    weight = Column(Float, comment='权重')
    in_date = Column(String(8), comment='纳入日期')
    out_date = Column(String(8), comment='剔除日期')
    is_new = Column(String(1), comment='是否最新')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_con_code', 'con_code'),
        {'comment': '同花顺板块成分'}
    )
