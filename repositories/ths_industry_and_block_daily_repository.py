from repositories.base_repository import BaseRepository
from models.ths_industry_and_block_daily import ThsIndustryAndBlockDaily
from sqlalchemy import text

class ThsIndustryAndBlockDailyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(ThsIndustryAndBlockDaily, session)
    
    def batch_upsert(self, data_list):
        if not data_list:
            return 0
        
        # Ensure all fields exist with None as default
        for item in data_list:
            item.setdefault('close', None)
            item.setdefault('open', None)
            item.setdefault('high', None)
            item.setdefault('low', None)
            item.setdefault('pre_close', None)
            item.setdefault('avg_price', None)
            item.setdefault('change', None)
            item.setdefault('pct_change', None)
            item.setdefault('vol', None)
            item.setdefault('turnover_rate', None)
            item.setdefault('total_mv', None)
            item.setdefault('float_mv', None)
        
        sql = text("""
            INSERT INTO ths_industry_and_block_daily 
            (ts_code, trade_date, close, open, high, low, pre_close, avg_price, 
             `change`, pct_change, vol, turnover_rate, total_mv, float_mv)
            VALUES (:ts_code, :trade_date, :close, :open, :high, :low, :pre_close, :avg_price,
                    :change, :pct_change, :vol, :turnover_rate, :total_mv, :float_mv)
            ON DUPLICATE KEY UPDATE
            close=VALUES(close), open=VALUES(open), high=VALUES(high), low=VALUES(low),
            pre_close=VALUES(pre_close), avg_price=VALUES(avg_price), `change`=VALUES(`change`),
            pct_change=VALUES(pct_change), vol=VALUES(vol), turnover_rate=VALUES(turnover_rate),
            total_mv=VALUES(total_mv), float_mv=VALUES(float_mv)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
