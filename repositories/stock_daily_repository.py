from sqlalchemy.orm import Session
from models.stock_daily import StockDaily
from .base_repository import BaseRepository
from typing import List, Dict, Any

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
