from repositories.base_repository import BaseRepository
from models.dc_industry_and_block import DcIndustryAndBlock
from sqlalchemy import text

class DcIndustryAndBlockRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(DcIndustryAndBlock, session)
    
    def batch_upsert(self, data_list):
        if not data_list:
            return 0
        
        for item in data_list:
            item.setdefault('name', None)
            item.setdefault('leading', None)
            item.setdefault('leading_code', None)
            item.setdefault('pct_change', None)
            item.setdefault('leading_pct', None)
            item.setdefault('total_mv', None)
            item.setdefault('turnover_rate', None)
            item.setdefault('up_num', None)
            item.setdefault('down_num', None)
        
        sql = text("""
            INSERT INTO dc_industry_and_block 
            (ts_code, trade_date, name, `leading`, leading_code, pct_change, leading_pct, 
             total_mv, turnover_rate, up_num, down_num)
            VALUES (:ts_code, :trade_date, :name, :leading, :leading_code, :pct_change, :leading_pct,
                    :total_mv, :turnover_rate, :up_num, :down_num)
            ON DUPLICATE KEY UPDATE
            name=VALUES(name), `leading`=VALUES(`leading`), leading_code=VALUES(leading_code),
            pct_change=VALUES(pct_change), leading_pct=VALUES(leading_pct), total_mv=VALUES(total_mv),
            turnover_rate=VALUES(turnover_rate), up_num=VALUES(up_num), down_num=VALUES(down_num)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
