from repositories.base_repository import BaseRepository
from models.ths_industry_and_block_detail import ThsIndustryAndBlockDetail
from sqlalchemy import text

class ThsIndustryAndBlockDetailRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(ThsIndustryAndBlockDetail, session)
    
    def delete_by_ts_code(self, ts_code):
        self.db.query(ThsIndustryAndBlockDetail).filter(
            ThsIndustryAndBlockDetail.ts_code == ts_code
        ).delete()
        self.db.commit()
    
    def batch_insert(self, data_list):
        if not data_list:
            return 0
        
        # Ensure all required fields exist with None as default
        for item in data_list:
            item.setdefault('weight', None)
            item.setdefault('in_date', None)
            item.setdefault('out_date', None)
            item.setdefault('is_new', None)
        
        sql = text("""
            INSERT INTO ths_industry_and_block_detail 
            (ts_code, con_code, con_name, weight, in_date, out_date, is_new)
            VALUES (:ts_code, :con_code, :con_name, :weight, :in_date, :out_date, :is_new)
            ON DUPLICATE KEY UPDATE
            con_name=VALUES(con_name), weight=VALUES(weight), in_date=VALUES(in_date),
            out_date=VALUES(out_date), is_new=VALUES(is_new)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
