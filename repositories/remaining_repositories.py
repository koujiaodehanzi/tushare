from sqlalchemy.orm import Session
from models.remaining_models import *
from models.stock_daily import StockDaily
from models.stock_chip import StockChip
from models.stock_tech_factor import StockTechFactor
from .base_repository import BaseRepository
from typing import List, Dict, Any

# 3. 日线行情Repository
class StockDailyRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockDaily, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date'])
    
    def get_by_ts_code_and_date_range(self, ts_code: str, start_date: str, end_date: str):
        """根据TS代码和日期范围查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).all()


# 4. 股票每日筹码Repository
class StockChipRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockChip, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date'])
    
    def get_by_ts_code_and_date_range(self, ts_code: str, start_date: str, end_date: str):
        """根据TS代码和日期范围查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).all()


# 5. 股票技术面因子Repository
class StockTechFactorRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockTechFactor, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date'])
    
    def get_by_ts_code_and_date_range(self, ts_code: str, start_date: str, end_date: str):
        """根据TS代码和日期范围查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).all()
    
    def get_by_ts_code_and_trade_date(self, ts_code: str, trade_date: str):
        """根据TS代码和交易日期查询单个数据"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date == trade_date
        ).first()


# 6. 个股资金流向Repository
class StockMoneyFlowRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockMoneyFlow, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date'])
    
    def get_by_ts_code_and_trade_date(self, ts_code: str, trade_date: str):
        """根据TS代码和交易日期查询单个数据"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date == trade_date
        ).first()
    
    def get_by_ts_code_and_date_range(self, ts_code: str, start_date: str, end_date: str):
        """根据TS代码和日期范围查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).all()


# 7. 同花顺板块资金流向Repository
class BlockThsMoneyFlowRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(BlockThsMoneyFlow, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['trade_date', 'block_code'])
    
    def get_by_block_code_and_trade_date(self, block_code: str, trade_date: str):
        """根据板块代码和交易日期查询"""
        return self.db.query(self.model).filter(
            self.model.block_code == block_code,
            self.model.trade_date == trade_date
        ).all()
    
    def get_by_block_code_and_date_range(self, block_code: str, start_date: str, end_date: str):
        """根据板块代码和日期范围查询，按block_code和trade_date分组"""
        return self.db.query(self.model).filter(
            self.model.block_code == block_code,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).order_by(self.model.block_code, self.model.trade_date).all()


# 8. 同花顺行业资金流向Repository
class IndustryThsMoneyFlowRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(IndustryThsMoneyFlow, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['trade_date', 'industry'])
    
    def get_by_industry_and_trade_date(self, industry: str, trade_date: str):
        """根据行业名称和交易日期查询"""
        return self.db.query(self.model).filter(
            self.model.industry == industry,
            self.model.trade_date == trade_date
        ).all()
    
    def get_by_industry_and_date_range(self, industry: str, start_date: str, end_date: str):
        """根据行业名称和日期范围查询，按industry和trade_date分组"""
        return self.db.query(self.model).filter(
            self.model.industry == industry,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).order_by(self.model.industry, self.model.trade_date).all()


# 9. 龙虎榜每日统计单Repository
class StockLhbDailyRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockLhbDaily, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date', 'reason'])
    
    def get_by_ts_code_and_trade_date(self, ts_code: str, trade_date: str):
        """根据TS代码和交易日期查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date == trade_date
        ).all()
    
    def get_by_ts_code_and_date_range(self, ts_code: str, start_date: str, end_date: str):
        """根据TS代码和日期范围查询，按trade_date分组"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date >= start_date,
            self.model.trade_date <= end_date
        ).order_by(self.model.trade_date).all()


# 10. 龙虎榜机构交易单Repository
class StockLhbInstRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockLhbInst, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date', 'seq'])
    
    def get_by_ts_code_and_trade_date(self, ts_code: str, trade_date: str):
        """根据TS代码和交易日期查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date == trade_date
        ).all()
    
    def get_by_ts_code_trade_date_and_exalter(self, ts_code: str, trade_date: str, exalter: str):
        """根据TS代码、交易日期和营业部名称查询"""
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.trade_date == trade_date,
            self.model.exalter.like(f'%{exalter}%')
        ).all()


# 11. 股票涨跌停和炸板数据Repository
class StockLimitStatusRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockLimitStatus, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date'])
    
    def get_by_trade_date(self, trade_date: str):
        """根据trade_date查询"""
        return self.db.query(self.model).filter(
            self.model.trade_date == trade_date
        ).all()


# 12. 涨停股票连板天梯Repository
class StockLimitLadderRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockLimitLadder, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['ts_code', 'trade_date'])
    
    def get_by_trade_date(self, trade_date: str):
        """根据trade_date查询"""
        return self.db.query(self.model).filter(
            self.model.trade_date == trade_date
        ).all()


# 13. 涨停板块最强统计Repository
class BlockLimitStrongRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(BlockLimitStrong, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['trade_date', 'ts_code'])
    
    def get_by_trade_date(self, trade_date: str):
        """根据trade_date查询"""
        return self.db.query(self.model).filter(
            self.model.trade_date == trade_date
        ).all()


# 14. 股票游资名录Repository
class StockHotMoneyRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockHotMoney, db)
    
    def upsert(self, data_list: List[Dict[str, Any]]):
        """全量更新和增量更新"""
        return self.batch_upsert(data_list, ['name', 'orgs'])
    
    def get_by_name(self, name: str):
        """根据游资名称查询"""
        return self.db.query(self.model).filter(
            self.model.name.like(f'%{name}%')
        ).all()

# 15. 游资每日明细Repository
class StockHotMoneyDailyRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockHotMoneyDaily, db)
    
    def batch_upsert_data(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        return self.batch_upsert(data_list, ['trade_date', 'ts_code', 'hm_name'])
    
    def get_by_trade_date(self, trade_date: str):
        """根据交易日期查询"""
        return self.db.query(self.model).filter(
            self.model.trade_date == trade_date
        ).all()
