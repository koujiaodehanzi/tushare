from sqlalchemy import Column, BigInteger, String, DECIMAL, Integer, Text, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from utils.db import Base

# 6. 个股资金流向模型 - moneyflow接口
class StockMoneyFlow(Base):
    __tablename__ = 'stock_money_flow'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    buy_sm_vol = Column(Integer, comment='小单买入量(手)')
    buy_sm_amount = Column(DECIMAL(20, 4), comment='小单买入金额(万元)')
    sell_sm_vol = Column(Integer, comment='小单卖出量(手)')
    sell_sm_amount = Column(DECIMAL(20, 4), comment='小单卖出金额(万元)')
    buy_md_vol = Column(Integer, comment='中单买入量(手)')
    buy_md_amount = Column(DECIMAL(20, 4), comment='中单买入金额(万元)')
    sell_md_vol = Column(Integer, comment='中单卖出量(手)')
    sell_md_amount = Column(DECIMAL(20, 4), comment='中单卖出金额(万元)')
    buy_lg_vol = Column(Integer, comment='大单买入量(手)')
    buy_lg_amount = Column(DECIMAL(20, 4), comment='大单买入金额(万元)')
    sell_lg_vol = Column(Integer, comment='大单卖出量(手)')
    sell_lg_amount = Column(DECIMAL(20, 4), comment='大单卖出金额(万元)')
    buy_elg_vol = Column(Integer, comment='特大单买入量(手)')
    buy_elg_amount = Column(DECIMAL(20, 4), comment='特大单买入金额(万元)')
    sell_elg_vol = Column(Integer, comment='特大单卖出量(手)')
    sell_elg_amount = Column(DECIMAL(20, 4), comment='特大单卖出金额(万元)')
    net_mf_vol = Column(Integer, comment='净流入量(手)')
    net_mf_amount = Column(DECIMAL(20, 4), comment='净流入额(万元)')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uk_money_flow'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )


# 7. 同花顺板块资金流向模型 - ths_hot接口
class BlockThsMoneyFlow(Base):
    __tablename__ = 'block_ths_money_flow'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    ts_code = Column(String(20), nullable=False, comment='板块代码')
    name = Column(String(100), comment='板块名称')
    lead_stock = Column(String(100), comment='领涨股票名称')
    close_price = Column(DECIMAL(10, 4), comment='最新价')
    pct_change = Column(DECIMAL(10, 4), comment='行业涨跌幅(%)')
    industry_index = Column(DECIMAL(20, 4), comment='板块指数')
    company_num = Column(BigInteger, comment='公司数量')
    pct_change_stock = Column(DECIMAL(10, 4), comment='领涨股涨跌幅(%)')
    net_buy_amount = Column(DECIMAL(20, 4), comment='流入资金(亿元)')
    net_sell_amount = Column(DECIMAL(20, 4), comment='流出资金(亿元)')
    net_amount = Column(DECIMAL(20, 4), comment='净额(亿元)')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('trade_date', 'ts_code', name='uk_block_money_flow'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_ts_code', 'ts_code'),
    )


# 8. 同花顺行业资金流向模型 - ths_industry接口
class IndustryThsMoneyFlow(Base):
    __tablename__ = 'industry_ths_money_flow'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    ts_code = Column(String(20), nullable=False, comment='板块代码')
    industry = Column(String(100), comment='板块名称')
    lead_stock = Column(String(100), comment='领涨股票名称')
    close = Column(DECIMAL(20, 4), comment='收盘指数')
    pct_change = Column(DECIMAL(10, 4), comment='指数涨跌幅')
    company_num = Column(BigInteger, comment='公司数量')
    pct_change_stock = Column(DECIMAL(10, 4), comment='领涨股涨跌幅')
    close_price = Column(DECIMAL(10, 4), comment='领涨股最新价')
    net_buy_amount = Column(DECIMAL(20, 4), comment='流入资金(亿元)')
    net_sell_amount = Column(DECIMAL(20, 4), comment='流出资金(亿元)')
    net_amount = Column(DECIMAL(20, 4), comment='净额(亿元)')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('trade_date', 'ts_code', name='uk_industry_money_flow'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_ts_code', 'ts_code'),
    )


# 9. 龙虎榜每日统计单模型 - top_list接口
class StockLhbDaily(Base):
    __tablename__ = 'stock_lhb_daily'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    name = Column(String(100), comment='股票名称')
    close = Column(DECIMAL(20, 4), comment='收盘价')
    pct_change = Column(DECIMAL(10, 4), comment='涨跌幅(%)')
    turnover_rate = Column(DECIMAL(10, 4), comment='换手率(%)')
    amount = Column(DECIMAL(20, 4), comment='总成交额(万)')
    l_sell = Column(DECIMAL(20, 4), comment='龙虎榜卖出额(万)')
    l_buy = Column(DECIMAL(20, 4), comment='龙虎榜买入额(万)')
    l_amount = Column(DECIMAL(20, 4), comment='龙虎榜成交额(万)')
    net_amount = Column(DECIMAL(20, 4), comment='龙虎榜净买入额(万)')
    net_rate = Column(DECIMAL(10, 4), comment='龙虎榜净买额占比(%)')
    amount_rate = Column(DECIMAL(10, 4), comment='龙虎榜成交额占比(%)')
    float_values = Column(DECIMAL(20, 4), comment='当日流通市值(万)')
    reason = Column(String(500), comment='上榜原因')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', 'reason', name='uk_lhb_daily'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )


# 10. 龙虎榜机构交易单模型 - top_inst接口
class StockLhbInst(Base):
    __tablename__ = 'stock_lhb_inst'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    ts_code = Column(String(20), nullable=False, comment='TS代码')
    exalter = Column(String(200), nullable=False, comment='营业部名称')
    side = Column(String(10), comment='买卖类型')
    buy = Column(DECIMAL(20, 4), comment='买入额(元)')
    buy_rate = Column(DECIMAL(10, 4), comment='买入占总成交比例')
    sell = Column(DECIMAL(20, 4), comment='卖出额(元)')
    sell_rate = Column(DECIMAL(10, 4), comment='卖出占总成交比例')
    net_buy = Column(DECIMAL(20, 4), comment='净成交额(元)')
    reason = Column(String(200), comment='上榜理由')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', 'exalter', 'side', name='uk_lhb_inst'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_exalter', 'exalter'),
    )


# 11. 股票涨跌停和炸板数据模型 - limit_list_d接口
class StockLimitStatus(Base):
    __tablename__ = 'stock_limit_status'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    ts_code = Column(String(20), nullable=False, comment='股票代码')
    industry = Column(String(100), comment='所属行业')
    name = Column(String(100), comment='股票名称')
    close = Column(DECIMAL(20, 4), comment='收盘价')
    pct_chg = Column(DECIMAL(10, 4), comment='涨跌幅')
    amount = Column(DECIMAL(20, 4), comment='成交额')
    limit_amount = Column(DECIMAL(20, 4), comment='板上成交金额')
    float_mv = Column(DECIMAL(20, 4), comment='流通市值')
    total_mv = Column(DECIMAL(20, 4), comment='总市值')
    turnover_ratio = Column(DECIMAL(10, 4), comment='换手率')
    fd_amount = Column(DECIMAL(20, 4), comment='封单金额')
    first_time = Column(String(10), comment='首次封板时间')
    last_time = Column(String(10), comment='最后封板时间')
    open_times = Column(Integer, comment='炸板次数')
    up_stat = Column(String(20), comment='涨停统计')
    limit_times = Column(Integer, comment='连板数')
    limit = Column(String(10), comment='D跌停U涨停Z炸板')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uk_limit_status'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )


# 12. 涨停股票连板天梯模型 - limit_list接口
class StockLimitLadder(Base):
    __tablename__ = 'stock_limit_ladder'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='代码')
    name = Column(String(100), comment='名称')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    nums = Column(String(10), comment='连板次数')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('ts_code', 'trade_date', name='uk_limit_ladder'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_trade_date', 'trade_date'),
    )


# 13. 涨停板块最强统计模型 - limit_cpt_list接口  
class BlockLimitStrong(Base):
    __tablename__ = 'block_limit_strong'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ts_code = Column(String(20), nullable=False, comment='板块代码')
    name = Column(String(100), comment='板块名称')
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    days = Column(Integer, comment='上榜天数')
    up_stat = Column(String(20), comment='连板高度')
    cons_nums = Column(Integer, comment='连板家数')
    up_nums = Column(String(20), comment='涨停家数')
    pct_chg = Column(DECIMAL(10, 4), comment='涨跌幅%')
    rank = Column(String(10), comment='板块热点排名')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('trade_date', 'ts_code', name='uk_block_limit_strong'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_ts_code', 'ts_code'),
    )


# 14. 股票游资名录模型 - hot_inst_cons接口
class StockHotMoney(Base):
    __tablename__ = 'stock_hot_money'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, comment='游资名称')
    orgs = Column(Text, comment='关联营业部')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_name', 'name'),
    )

# 15. 游资每日明细模型 - hm_detail接口
class StockHotMoneyDaily(Base):
    __tablename__ = 'stock_hot_money_daily'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    trade_date = Column(String(8), nullable=False, comment='交易日期')
    ts_code = Column(String(20), nullable=False, comment='股票代码')
    ts_name = Column(String(100), comment='股票名称')
    buy_amount = Column(DECIMAL(20, 4), comment='买入金额(元)')
    sell_amount = Column(DECIMAL(20, 4), comment='卖出金额(元)')
    net_amount = Column(DECIMAL(20, 4), comment='净买卖(元)')
    hm_name = Column(String(200), nullable=False, comment='游资名称')
    hm_orgs = Column(String(500), comment='关联机构')
    tag = Column(String(200), comment='标签')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        UniqueConstraint('trade_date', 'ts_code', 'hm_name', name='uk_hm_daily'),
        Index('idx_trade_date', 'trade_date'),
        Index('idx_ts_code', 'ts_code'),
        Index('idx_hm_name', 'hm_name'),
    )
