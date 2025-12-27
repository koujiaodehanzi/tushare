from sqlalchemy.orm import Session
from sqlalchemy import func
from models.stock_holder import StockHolder
from .base_repository import BaseRepository
from typing import List, Dict, Any

class StockHolderRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(StockHolder, db)
    
    def upsert(self, data_list: List[Dict[str, Any]]):
        """插入或更新，根据联合索引"""
        return self.batch_upsert(data_list, ['ts_code', 'ann_date', 'holder_name'])
    
    def get_latest_by_ts_code(self, ts_code: str):
        """根据TS代码查询最新ann_date的股东持股数据列表"""
        # 先查询最新的ann_date
        latest_ann_date = self.db.query(func.max(self.model.ann_date)).filter(
            self.model.ts_code == ts_code
        ).scalar()
        
        if not latest_ann_date:
            return []
        
        # 查询该日期的所有记录
        return self.db.query(self.model).filter(
            self.model.ts_code == ts_code,
            self.model.ann_date == latest_ann_date
        ).all()
