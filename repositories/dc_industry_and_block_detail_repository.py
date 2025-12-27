from repositories.base_repository import BaseRepository
from models.dc_industry_and_block_detail import DcIndustryAndBlockDetail
from sqlalchemy import text

class DcIndustryAndBlockDetailRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(DcIndustryAndBlockDetail, session)
    
    def delete_by_ts_code(self, ts_code):
        sql = text("DELETE FROM dc_industry_and_block_detail WHERE ts_code = :ts_code")
        self.db.execute(sql, {'ts_code': ts_code})
        self.db.commit()
    
    def batch_insert(self, data_list):
        if not data_list:
            return 0
        
        for item in data_list:
            item.setdefault('name', None)
        
        sql = text("""
            INSERT INTO dc_industry_and_block_detail 
            (trade_date, ts_code, con_code, name)
            VALUES (:trade_date, :ts_code, :con_code, :name)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
