from repositories.base_repository import BaseRepository
from models.block_dc_money_flow import BlockDcMoneyFlow
from sqlalchemy import text

class BlockDcMoneyFlowRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(BlockDcMoneyFlow, session)
    
    def batch_upsert(self, data_list):
        if not data_list:
            return 0
        
        for item in data_list:
            item.setdefault('buy_elg_amount', None)
            item.setdefault('buy_elg_amount_rate', None)
            item.setdefault('sell_elg_amount', None)
            item.setdefault('sell_elg_amount_rate', None)
            item.setdefault('buy_lg_amount', None)
            item.setdefault('buy_lg_amount_rate', None)
            item.setdefault('sell_lg_amount', None)
            item.setdefault('sell_lg_amount_rate', None)
            item.setdefault('buy_md_amount', None)
            item.setdefault('sell_md_amount', None)
            item.setdefault('buy_sm_amount', None)
            item.setdefault('sell_sm_amount', None)
            item.setdefault('net_mf_amount', None)
        
        sql = text("""
            INSERT INTO block_dc_money_flow 
            (ts_code, trade_date, buy_elg_amount, buy_elg_amount_rate, sell_elg_amount, sell_elg_amount_rate,
             buy_lg_amount, buy_lg_amount_rate, sell_lg_amount, sell_lg_amount_rate,
             buy_md_amount, sell_md_amount, buy_sm_amount, sell_sm_amount, net_mf_amount)
            VALUES (:ts_code, :trade_date, :buy_elg_amount, :buy_elg_amount_rate, :sell_elg_amount, :sell_elg_amount_rate,
                    :buy_lg_amount, :buy_lg_amount_rate, :sell_lg_amount, :sell_lg_amount_rate,
                    :buy_md_amount, :sell_md_amount, :buy_sm_amount, :sell_sm_amount, :net_mf_amount)
            ON DUPLICATE KEY UPDATE
            buy_elg_amount=VALUES(buy_elg_amount), buy_elg_amount_rate=VALUES(buy_elg_amount_rate),
            sell_elg_amount=VALUES(sell_elg_amount), sell_elg_amount_rate=VALUES(sell_elg_amount_rate),
            buy_lg_amount=VALUES(buy_lg_amount), buy_lg_amount_rate=VALUES(buy_lg_amount_rate),
            sell_lg_amount=VALUES(sell_lg_amount), sell_lg_amount_rate=VALUES(sell_lg_amount_rate),
            buy_md_amount=VALUES(buy_md_amount), sell_md_amount=VALUES(sell_md_amount),
            buy_sm_amount=VALUES(buy_sm_amount), sell_sm_amount=VALUES(sell_sm_amount),
            net_mf_amount=VALUES(net_mf_amount)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
