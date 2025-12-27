from repositories.base_repository import BaseRepository
from models.stock_money_flow_ths import StockMoneyFlowThs
from sqlalchemy import text, and_

class StockMoneyFlowThsRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(StockMoneyFlowThs, session)
    
    def batch_upsert(self, data_list):
        if not data_list:
            return 0
        
        # Ensure all fields exist
        for item in data_list:
            item.setdefault('name', None)
            item.setdefault('pct_change', None)
            item.setdefault('latest', None)
            item.setdefault('net_amount', None)
            item.setdefault('net_d5_amount', None)
            item.setdefault('buy_lg_amount', None)
            item.setdefault('buy_lg_amount_rate', None)
            item.setdefault('buy_md_amount', None)
            item.setdefault('buy_md_amount_rate', None)
            item.setdefault('buy_sm_amount', None)
            item.setdefault('buy_sm_amount_rate', None)
        
        sql = text("""
            INSERT INTO stock_money_flow_ths 
            (ts_code, trade_date, name, pct_change, latest, net_amount, net_d5_amount,
             buy_lg_amount, buy_lg_amount_rate, buy_md_amount, buy_md_amount_rate,
             buy_sm_amount, buy_sm_amount_rate)
            VALUES (:ts_code, :trade_date, :name, :pct_change, :latest, :net_amount, :net_d5_amount,
                    :buy_lg_amount, :buy_lg_amount_rate, :buy_md_amount, :buy_md_amount_rate,
                    :buy_sm_amount, :buy_sm_amount_rate)
            ON DUPLICATE KEY UPDATE
            name=VALUES(name), pct_change=VALUES(pct_change), latest=VALUES(latest),
            net_amount=VALUES(net_amount), net_d5_amount=VALUES(net_d5_amount),
            buy_lg_amount=VALUES(buy_lg_amount), buy_lg_amount_rate=VALUES(buy_lg_amount_rate),
            buy_md_amount=VALUES(buy_md_amount), buy_md_amount_rate=VALUES(buy_md_amount_rate),
            buy_sm_amount=VALUES(buy_sm_amount), buy_sm_amount_rate=VALUES(buy_sm_amount_rate)
        """)
        self.db.execute(sql, data_list)
        self.db.commit()
        return len(data_list)
    
    def get_by_ts_code_and_date(self, ts_code: str, trade_date: str):
        """根据TS代码和交易日期查询单条数据"""
        return self.db.query(StockMoneyFlowThs).filter(
            and_(
                StockMoneyFlowThs.ts_code == ts_code,
                StockMoneyFlowThs.trade_date == trade_date
            )
        ).first()
    
    def get_by_ts_code_and_date_range(self, ts_code: str, start_date: str, end_date: str):
        """根据TS代码和日期范围查询数据列表"""
        return self.db.query(StockMoneyFlowThs).filter(
            and_(
                StockMoneyFlowThs.ts_code == ts_code,
                StockMoneyFlowThs.trade_date >= start_date,
                StockMoneyFlowThs.trade_date <= end_date
            )
        ).order_by(StockMoneyFlowThs.trade_date.desc()).all()
