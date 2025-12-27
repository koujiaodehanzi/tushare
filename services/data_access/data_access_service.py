from services.tushare_client import TushareClient
from utils.logger import get_logger

logger = get_logger(__name__)

class DataAccessService:
    def __init__(self):
        self.client = TushareClient()
    
    def get_stock_list(self, **kwargs):
        """获取股票列表"""
        return self.client.get_stock_basic(**kwargs)
    
    def get_stock_holder(self, ts_code: str, **kwargs):
        """获取股东持股"""
        return self.client.get_top10_holders(ts_code=ts_code, **kwargs)
    
    def get_stock_daily(self, ts_code: str = None, trade_date: str = None, 
                       start_date: str = None, end_date: str = None):
        """获取日线行情"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_daily(**params)
    
    def get_stock_chip(self, ts_code: str, trade_date: str = None, 
                      start_date: str = None, end_date: str = None):
        """获取股票每日筹码"""
        params = {'ts_code': ts_code}
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_cyq_perf(**params)
    
    def get_stock_tech_factor(self, ts_code: str = None, trade_date: str = None,
                             start_date: str = None, end_date: str = None):
        """获取股票技术面因子"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_stk_factor(**params)
    
    def get_stock_tech_factor_pro(self, ts_code: str = None, trade_date: str = None,
                                  start_date: str = None, end_date: str = None):
        """获取股票技术面因子专业版"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_stk_factor_pro(**params)
    
    def get_stock_money_flow(self, ts_code: str = None, trade_date: str = None,
                            start_date: str = None, end_date: str = None):
        """获取个股资金流向"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_moneyflow(**params)
    
    def get_block_ths_money_flow(self, trade_date: str):
        """获取同花顺板块资金流向"""
        return self.client.get_moneyflow_cnt_ths(trade_date=trade_date)
    
    def get_industry_ths_money_flow(self, trade_date: str):
        """获取同花顺行业资金流向"""
        return self.client.get_ths_industry(trade_date=trade_date)
    
    def get_stock_lhb_daily(self, trade_date: str = None, ts_code: str = None):
        """获取龙虎榜每日统计"""
        params = {}
        if trade_date:
            params['trade_date'] = trade_date
        if ts_code:
            params['ts_code'] = ts_code
        return self.client.get_top_list(**params)
    
    def get_stock_lhb_inst(self, trade_date: str = None, ts_code: str = None):
        """获取龙虎榜机构交易"""
        params = {}
        if trade_date:
            params['trade_date'] = trade_date
        if ts_code:
            params['ts_code'] = ts_code
        return self.client.get_top_inst(**params)
    
    def get_stock_limit_status(self, trade_date: str):
        """获取涨跌停和炸板数据"""
        return self.client.get_limit_list_d(trade_date=trade_date)
    
    def get_stock_limit_ladder(self, trade_date: str):
        """获取涨停股票连板天梯"""
        return self.client.get_limit_list(trade_date=trade_date)
    
    def get_block_limit_strong(self, trade_date: str):
        """获取涨停板块最强统计"""
        return self.client.get_ths_hot_rank(trade_date=trade_date)
    
    def get_stock_hot_money(self):
        """获取股票游资名录"""
        return self.client.get_hot_inst_cons()
    
    def get_stock_hot_money_daily(self, trade_date: str, ts_code: str = None, hm_name: str = None):
        """获取游资每日明细"""
        params = {'trade_date': trade_date}
        if ts_code:
            params['ts_code'] = ts_code
        if hm_name:
            params['hm_name'] = hm_name
        return self.client.get_hm_detail(**params)
    
    def get_trade_cal(self, start_date: str, end_date: str):
        """获取交易日历"""
        return self.client.get_trade_cal(start_date=start_date, end_date=end_date, exchange='SSE')

    def get_ths_index(self, ts_code: str = None, exchange: str = None, type: str = None):
        """获取同花顺行业和概念板块"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if exchange:
            params['exchange'] = exchange
        if type:
            params['type'] = type
        return self.client.get_ths_index(**params)
    
    def get_ths_member(self, ts_code: str = None, con_code: str = None):
        """获取同花顺板块成分"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if con_code:
            params['con_code'] = con_code
        return self.client.get_ths_member(**params)
    
    def get_ths_daily(self, ts_code: str = None, trade_date: str = None, 
                      start_date: str = None, end_date: str = None):
        """获取同花顺板块每日行情"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_ths_daily(**params)
    
    def get_moneyflow_ths(self, ts_code: str = None, trade_date: str = None,
                          start_date: str = None, end_date: str = None):
        """获取同花顺个股资金流向"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_moneyflow_ths(**params)
    
    def get_moneyflow_dc(self, ts_code: str = None, trade_date: str = None,
                         start_date: str = None, end_date: str = None):
        """获取东方财富个股资金流向"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_moneyflow_dc(**params)
    
    def get_moneyflow_dc_cnt(self, ts_code: str = None, trade_date: str = None,
                             start_date: str = None, end_date: str = None):
        """获取东方财富板块资金流向"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_moneyflow_dc_cnt(**params)
    
    def get_moneyflow_dc_industry(self, ts_code: str = None, trade_date: str = None,
                                   start_date: str = None, end_date: str = None):
        """获取东方财富行业资金流向"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_moneyflow_dc_industry(**params)
    
    def get_dc_index(self, ts_code: str = None, name: str = None, trade_date: str = None,
                     start_date: str = None, end_date: str = None):
        """获取东方财富概念板块"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if name:
            params['name'] = name
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self.client.get_dc_index(**params)
    
    def get_dc_member(self, ts_code: str = None, con_code: str = None, trade_date: str = None):
        """获取东方财富板块成分"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if con_code:
            params['con_code'] = con_code
        if trade_date:
            params['trade_date'] = trade_date
        return self.client.get_dc_member(**params)
    
    def get_dc_daily(self, ts_code: str = None, trade_date: str = None,
                     start_date: str = None, end_date: str = None, idx_type: str = None):
        """获取东方财富板块每日行情"""
        params = {}
        if ts_code:
            params['ts_code'] = ts_code
        if trade_date:
            params['trade_date'] = trade_date
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if idx_type:
            params['idx_type'] = idx_type
        return self.client.get_dc_daily(**params)
