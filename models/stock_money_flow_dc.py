from sqlalchemy import Column, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StockMoneyFlowDc(Base):
    __tablename__ = 'stock_money_flow_dc'
    
    ts_code = Column(String(10), primary_key=True, comment='股票代码')
    trade_date = Column(Date, primary_key=True, comment='交易日期')
    buy_elg_amount = Column(Float, comment='超大单买入金额(万元)')
    buy_elg_amount_rate = Column(Float, comment='超大单买入金额占比')
    sell_elg_amount = Column(Float, comment='超大单卖出金额(万元)')
    sell_elg_amount_rate = Column(Float, comment='超大单卖出金额占比')
    buy_lg_amount = Column(Float, comment='大单买入金额(万元)')
    buy_lg_amount_rate = Column(Float, comment='大单买入金额占比')
    sell_lg_amount = Column(Float, comment='大单卖出金额(万元)')
    sell_lg_amount_rate = Column(Float, comment='大单卖出金额占比')
    buy_md_amount = Column(Float, comment='中单买入金额(万元)')
    sell_md_amount = Column(Float, comment='中单卖出金额(万元)')
    buy_sm_amount = Column(Float, comment='小单买入金额(万元)')
    sell_sm_amount = Column(Float, comment='小单卖出金额(万元)')
    net_mf_amount = Column(Float, comment='净流入金额(万元)')
