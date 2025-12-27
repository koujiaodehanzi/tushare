from repositories.base_repository import BaseRepository
from models.ths_industry_and_block import ThsIndustryAndBlock
from sqlalchemy import text

class ThsIndustryAndBlockRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(ThsIndustryAndBlock, session)
    
    def batch_upsert(self, data_list):
        if not data_list:
            return 0
        
        sql = text("""
            INSERT INTO ths_industry_and_block 
            (ts_code, name, count, exchange, list_date, type)
            VALUES (:ts_code, :name, :count, :exchange, :list_date, :type)
            ON DUPLICATE KEY UPDATE
            name=VALUES(name), count=VALUES(count), exchange=VALUES(exchange),
            list_date=VALUES(list_date), type=VALUES(type)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
