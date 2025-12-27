from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from models.stock_list import StockList
from .base_repository import BaseRepository
from typing import List, Dict, Any

class StockListRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockList, db)
    
    def upsert(self, data_list: List[Dict[str, Any]]):
        """全量更新和增量更新"""
        return self.batch_upsert(data_list, ['ts_code'])
    
    def get_by_ts_code_listed(self, ts_code: str = None):
        """根据TS代码查询上市状态的股票列表"""
        query = self.db.query(self.model).filter(self.model.list_status == 'L')
        if ts_code:
            query = query.filter(self.model.ts_code == ts_code)
        return query.all()
    
    def get_by_ts_code(self, ts_code: str):
        """根据TS代码查询单个股票"""
        return self.db.query(self.model).filter(self.model.ts_code == ts_code).first()
    
    def get_by_symbol(self, symbol: str):
        """根据股票代码查询单个股票"""
        return self.db.query(self.model).filter(self.model.symbol == symbol).first()
    
    def get_by_name(self, name: str):
        """根据股票名称查询单个股票"""
        return self.db.query(self.model).filter(self.model.name == name).first()
    
    def get_by_industry_listed(self, industry: str):
        """根据所属行业查询上市状态的股票列表"""
        return self.db.query(self.model).filter(
            self.model.industry == industry,
            self.model.list_status == 'L'
        ).all()
    
    def get_by_area_listed(self, area: str):
        """根据地域查询上市状态的股票列表"""
        return self.db.query(self.model).filter(
            self.model.area == area,
            self.model.list_status == 'L'
        ).all()
    
    def get_by_market_listed(self, market: str):
        """根据市场类型查询上市状态的股票列表"""
        return self.db.query(self.model).filter(
            self.model.market == market,
            self.model.list_status == 'L'
        ).all()
    
    def get_all_stocks(self):
        """查询股票全量列表"""
        return self.get_all()
