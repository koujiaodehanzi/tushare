from sqlalchemy import Column, BigInteger, String, Float, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from utils.db import Base

class StockHolder(Base):
    __tablename__ = 'stock_holder'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    ann_date = Column(String(8), nullable=False, comment='公告日期')
    end_date = Column(String(8), comment='报告期')
    holder_name = Column(String(200), nullable=False, comment='股东名称')
    hold_amount = Column(Float, comment='持有数量')
    hold_ratio = Column(Float, comment='占总股本比例')
    hold_float_ratio = Column(Float, comment='占流通股本比例')
    hold_change = Column(Float, comment='持股变动')
    holder_type = Column(String(50), comment='股东类型')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'ann_date', 'holder_name', name='uk_holder'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_ann_date', 'ann_date'),
    )
