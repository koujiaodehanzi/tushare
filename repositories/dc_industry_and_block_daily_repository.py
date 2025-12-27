from repositories.base_repository import BaseRepository
from models.dc_industry_and_block_daily import DcIndustryAndBlockDaily
from sqlalchemy import text

class DcIndustryAndBlockDailyRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(DcIndustryAndBlockDaily, session)
    
    def batch_upsert(self, data_list):
        if not data_list:
            return 0
        
        for item in data_list:
            item.setdefault('close', None)
            item.setdefault('open', None)
            item.setdefault('high', None)
            item.setdefault('low', None)
            item.setdefault('change', None)
            item.setdefault('pct_change', None)
            item.setdefault('vol', None)
            item.setdefault('amount', None)
            item.setdefault('swing', None)
            item.setdefault('turnover_rate', None)
        
        sql = text("""
            INSERT INTO dc_industry_and_block_daily 
            (ts_code, trade_date, close, open, high, low, `change`, pct_change, vol, amount, swing, turnover_rate)
            VALUES (:ts_code, :trade_date, :close, :open, :high, :low, :change, :pct_change, :vol, :amount, :swing, :turnover_rate)
            ON DUPLICATE KEY UPDATE
            close=VALUES(close), open=VALUES(open), high=VALUES(high), low=VALUES(low),
            `change`=VALUES(`change`), pct_change=VALUES(pct_change), vol=VALUES(vol), amount=VALUES(amount),
            swing=VALUES(swing), turnover_rate=VALUES(turnover_rate)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
