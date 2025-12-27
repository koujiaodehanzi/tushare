from sqlalchemy.orm import Session
from models.sync_record import SyncRecord
from .base_repository import BaseRepository
from typing import List

class SyncRecordRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(SyncRecord, db)
    
    def is_synced(self, trade_date: str, sync_type: str) -> bool:
        """检查指定日期和类型是否已同步成功"""
        record = self.db.query(self.model).filter(
            self.model.trade_date == trade_date,
            self.model.sync_type == sync_type,
            self.model.status == 'success'
        ).first()
        return record is not None
    
    def get_unsynced_dates(self, date_list: List[str], sync_type: str) -> List[str]:
        """获取未同步的日期列表"""
        synced_dates = self.db.query(self.model.trade_date).filter(
            self.model.trade_date.in_(date_list),
            self.model.sync_type == sync_type,
            self.model.status == 'success'
        ).all()
        synced_dates_set = {d[0] for d in synced_dates}
        return [d for d in date_list if d not in synced_dates_set]
    
    def record_sync(self, trade_date: str, sync_type: str, status: str, record_count: int = 0, error_msg: str = None):
        """记录同步结果"""
        existing = self.db.query(self.model).filter(
            self.model.trade_date == trade_date,
            self.model.sync_type == sync_type
        ).first()
        
        if existing:
            existing.status = status
            existing.record_count = record_count
            existing.error_msg = error_msg
        else:
            record = SyncRecord(
                trade_date=trade_date,
                sync_type=sync_type,
                status=status,
                record_count=record_count,
                error_msg=error_msg
            )
            self.db.add(record)
        
        self.db.commit()
