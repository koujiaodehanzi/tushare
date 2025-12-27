from sqlalchemy import Column, String, Float, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ThsIndustryAndBlockDaily(Base):
    __tablename__ = 'ths_industry_and_block_daily'
    
    ts_code = Column(String(20), primary_key=True, comment='指数代码')
    trade_date = Column(String(8), primary_key=True, comment='交易日期')
    close = Column(Float, comment='收盘点位')
    open = Column(Float, comment='开盘点位')
    high = Column(Float, comment='最高点位')
    low = Column(Float, comment='最低点位')
    pre_close = Column(Float, comment='昨日收盘点')
    avg_price = Column(Float, comment='平均价')
    change = Column(Float, comment='涨跌点位')
    pct_change = Column(Float, comment='涨跌幅')
    vol = Column(Float, comment='成交量')
    turnover_rate = Column(Float, comment='换手率')
    total_mv = Column(Float, comment='总市值')
    float_mv = Column(Float, comment='流通市值')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
        {'comment': '同花顺板块每日行情'}
    )
