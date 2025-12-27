import tushare as ts
from config import config
from utils.logger import get_logger
from utils.rate_limiter import RateLimiter
from utils.retry import retry

logger = get_logger(__name__)

class TushareClient:
    def __init__(self):
        self.token = config['tushare']['token']
        self.api_limit = config['tushare']['api_limit']
        self.retry_times = config['tushare']['retry_times']
        self.retry_delay = config['tushare']['retry_delay']
        
        # 初始化tushare
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        
        # 初始化限流器
        self.rate_limiter = RateLimiter(self.api_limit, period=60)
    
    @retry(max_attempts=3, delay=1)
    def query(self, api_name: str, **kwargs):
        """统一查询接口"""
        # 按接口名称进行限流
        self.rate_limiter.acquire(api_name)
        
        try:
            logger.info(f"调用Tushare API: {api_name}, 参数: {kwargs}")
            df = self.pro.query(api_name, **kwargs)
            logger.info(f"API调用成功，返回{len(df)}条数据")
            return df
        except Exception as e:
            logger.error(f"API调用失败: {api_name}, 错误: {e}")
            raise
    
    def get_stock_basic(self, **kwargs):
        """获取股票列表"""
        return self.query('stock_basic', **kwargs)
    
    def get_top10_holders(self, **kwargs):
        """获取前十大股东"""
        return self.query('top10_holders', **kwargs)
    
    def get_daily(self, **kwargs):
        """获取日线行情"""
        return self.query('daily', **kwargs)
    
    def get_cyq_perf(self, **kwargs):
        """获取每日筹码及胜率"""
        return self.query('cyq_chips', **kwargs)
    
    def get_stk_factor(self, **kwargs):
        """获取股票技术面因子"""
        return self.query('stk_factor', **kwargs)
    
    def get_stk_factor_pro(self, **kwargs):
        """获取股票技术面因子专业版"""
        return self.query('stk_factor_pro', **kwargs)
    
    def get_moneyflow(self, **kwargs):
        """获取个股资金流向"""
        return self.query('moneyflow', **kwargs)
    
    def get_moneyflow_cnt_ths(self, **kwargs):
        """获取同花顺板块资金流向"""
        return self.query('moneyflow_cnt_ths', **kwargs)
    
    def get_ths_industry(self, **kwargs):
        """获取同花顺行业资金流向"""
        return self.query('moneyflow_ind_ths', **kwargs)
    
    def get_top_list(self, **kwargs):
        """获取龙虎榜每日统计"""
        return self.query('top_list', **kwargs)
    
    def get_top_inst(self, **kwargs):
        """获取龙虎榜机构交易"""
        return self.query('top_inst', **kwargs)
    
    def get_limit_list_d(self, **kwargs):
        """获取涨跌停和炸板数据"""
        return self.query('limit_list_d', **kwargs)
    
    def get_limit_list(self, **kwargs):
        """获取涨停股票连板天梯"""
        return self.query('limit_step', **kwargs)
    
    def get_ths_hot_rank(self, **kwargs):
        """获取涨停板块最强统计"""
        return self.query('limit_cpt_list', **kwargs)
    
    def get_hot_inst_cons(self, **kwargs):
        """获取股票游资名录"""
        return self.query('hm_list', **kwargs)
    
    def get_hm_detail(self, **kwargs):
        """获取游资每日明细"""
        return self.query('hm_detail', **kwargs)
    
    def get_trade_cal(self, **kwargs):
        """获取交易日历"""
        return self.query('trade_cal', **kwargs)
    
    def get_ths_index(self, **kwargs):
        """获取同花顺行业和概念板块"""
        return self.query('ths_index', **kwargs)
    
    def get_ths_member(self, **kwargs):
        """获取同花顺板块成分"""
        return self.query('ths_member', **kwargs)
    
    def get_ths_daily(self, **kwargs):
        """获取同花顺板块每日行情"""
        return self.query('ths_daily', **kwargs)
    
    def get_moneyflow_ths(self, **kwargs):
        """获取同花顺个股资金流向"""
        return self.query('moneyflow_ths', **kwargs)
    
    def get_moneyflow_dc(self, **kwargs):
        """获取东方财富个股资金流向"""
        return self.query('moneyflow_dc', **kwargs)
    
    def get_moneyflow_dc_cnt(self, **kwargs):
        """获取东方财富板块资金流向"""
        return self.query('moneyflow_dc_cnt', **kwargs)
    
    def get_moneyflow_dc_industry(self, **kwargs):
        """获取东方财富行业资金流向"""
        return self.query('moneyflow_dc_industry', **kwargs)
    
    def get_dc_index(self, **kwargs):
        """获取东方财富概念板块"""
        return self.query('dc_index', **kwargs)
    
    def get_dc_member(self, **kwargs):
        """获取东方财富板块成分"""
        return self.query('dc_member', **kwargs)
    
    def get_dc_daily(self, **kwargs):
        """获取东方财富板块每日行情"""
        return self.query('dc_daily', **kwargs)
    
    def get_rate_limit_stats(self, interface_name: str = None):
        """获取限流统计信息"""
        return self.rate_limiter.get_stats(interface_name)

