from sqlalchemy import Column, String, Float, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StockMoneyFlowThs(Base):
    __tablename__ = 'stock_money_flow_ths'
    
    ts_code = Column(String(20), primary_key=True, comment='股票代码')
    trade_date = Column(String(8), primary_key=True, comment='交易日期')
    name = Column(String(100), comment='股票名称')
    pct_change = Column(Float, comment='涨跌幅')
    latest = Column(Float, comment='最新价')
    net_amount = Column(Float, comment='资金净流入(万元)')
    net_d5_amount = Column(Float, comment='5日主力净额(万元)')
    buy_lg_amount = Column(Float, comment='今日大单净流入额(万元)')
    buy_lg_amount_rate = Column(Float, comment='今日大单净流入占比(%)')
    buy_md_amount = Column(Float, comment='今日中单净流入额(万元)')
    buy_md_amount_rate = Column(Float, comment='今日中单净流入占比(%)')
    buy_sm_amount = Column(Float, comment='今日小单净流入额(万元)')
    buy_sm_amount_rate = Column(Float, comment='今日小单净流入占比(%)')
    
    __table_args__ = (
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
        {'comment': '同花顺个股资金流向'}
    )
