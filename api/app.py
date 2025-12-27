from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from services.data_sync import DataSyncService
from utils.logger import get_logger
from utils.db import SessionLocal
from repositories import StockListRepository
from datetime import datetime
import os

app = Flask(__name__, static_folder='../static')
CORS(app)
logger = get_logger(__name__)

sync_service = DataSyncService()

# 注册股票查询蓝图
from api.stock_query_api import stock_query_bp
app.register_blueprint(stock_query_bp)

# 注册回测蓝图
from api.backtest_api import backtest_bp
app.register_blueprint(backtest_bp)

# 注册概念筛选蓝图
from api.concept_api import concept_bp
app.register_blueprint(concept_bp)

def symbol_to_ts_code(symbol):
    """将symbol转换为ts_code，如果已经是ts_code则直接返回"""
    if not symbol:
        return None
    
    # 如果已经包含.SZ或.SH，直接返回
    if '.SZ' in symbol or '.SH' in symbol or '.BJ' in symbol:
        return symbol
    
    # 查询数据库获取完整ts_code
    db = SessionLocal()
    try:
        repo = StockListRepository(db)
        stock = repo.get_by_symbol(symbol)
        if stock:
            return stock.ts_code
        else:
            logger.warning(f"未找到股票代码: {symbol}")
            return None
    finally:
        db.close()

def symbols_to_ts_codes(symbols_str):
    """将逗号分隔的symbols转换为ts_codes"""
    if not symbols_str:
        return None
    
    symbols = [s.strip() for s in symbols_str.split(',') if s.strip()]
    ts_codes = []
    for symbol in symbols:
        ts_code = symbol_to_ts_code(symbol)
        if ts_code:
            ts_codes.append(ts_code)
    
    return ','.join(ts_codes) if ts_codes else None

@app.route('/')
def index():
    """首页"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/stock_list.html')
def stock_list():
    """股票列表页"""
    return send_from_directory(app.static_folder, 'stock_list.html')

@app.route('/stock_detail.html')
def stock_detail():
    """股票详情页"""
    return send_from_directory(app.static_folder, 'stock_detail.html')

@app.route('/backtest.html')
def backtest():
    """策略回测页"""
    return send_from_directory(app.static_folder, 'backtest.html')

@app.route('/concept.html')
def concept():
    """概念筛选页"""
    return send_from_directory(app.static_folder, 'concept.html')

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/sync/base', methods=['POST'])
def sync_base_data():
    """基础数据全量同步接口"""
    try:
        logger.info("收到基础数据全量同步请求")
        result = sync_service.sync_base_data()
        return jsonify({
            'stock_list': result.get('stock_list', 0),
            'stock_holder': result.get('stock_holder', 0),
            'stock_hot_money': result.get('stock_hot_money', 0),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"基础数据全量同步失败: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync/daily', methods=['POST'])
def sync_daily_data():
    """每日数据同步接口"""
    try:
        data = request.get_json() or {}
        trade_date = data.get('trade_date')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        symbols_str = data.get('ts_codes', '').strip()  # 前端传的是symbol
        
        # 将symbols转换为ts_codes
        ts_codes_str = symbols_to_ts_codes(symbols_str) if symbols_str else None
        ts_codes = [code.strip() for code in ts_codes_str.split(',') if code.strip()] if ts_codes_str else None
        
        if trade_date:
            logger.info(f"收到每日数据同步请求: {trade_date}, symbols={symbols_str}, ts_codes={ts_codes}")
            result = sync_service.sync_daily_data_by_date(trade_date, ts_codes)
            return jsonify({
                'total_count': result.get('total_count', 0),
                'details': result.get('details', {}),
                'skipped': result.get('skipped', False),
                'timestamp': datetime.now().isoformat()
            })
        elif start_date and end_date:
            logger.info(f"收到日期范围数据同步请求: {start_date} - {end_date}, ts_codes={ts_codes}")
            result = sync_service.sync_daily_data_by_range(start_date, end_date, ts_codes)
            return jsonify({
                'total_count': result.get('total_count', 0),
                'details': result.get('details', {}),
                'synced_dates': result.get('synced_dates', 0),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'error': '请提供trade_date或start_date和end_date',
                'timestamp': datetime.now().isoformat()
            }), 400
    except Exception as e:
        logger.error(f"每日数据同步失败: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync/stock_list', methods=['POST'])
def sync_stock_list():
    """股票列表同步接口"""
    try:
        logger.info("收到股票列表同步请求")
        count = sync_service.sync_stock_list()
        return jsonify({
            'count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"股票列表同步失败: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync/stock_holder', methods=['POST'])
def sync_stock_holder():
    """股东持股同步接口"""
    try:
        logger.info("收到股东持股同步请求")
        count = sync_service.sync_stock_holder()
        return jsonify({
            'count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"股东持股同步失败: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync/stock_hot_money', methods=['POST'])
def sync_stock_hot_money():
    """股票游资名录同步接口"""
    try:
        logger.info("收到股票游资名录同步请求")
        count = sync_service.sync_stock_hot_money()
        return jsonify({
            'count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"股票游资名录同步失败: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/sync/stock_daily', methods=['POST'])
def sync_stock_daily_single():
    """日线行情同步接口"""
    try:
        data = request.get_json() or {}
        symbol = data.get('ts_code')  # 前端传的是symbol
        trade_date = data.get('trade_date')
        if not symbol or not trade_date:
            return jsonify({'error': '请提供股票代码和trade_date'}), 400
        
        ts_code = symbol_to_ts_code(symbol)
        if not ts_code:
            return jsonify({'error': f'未找到股票代码: {symbol}'}), 400
            
        logger.info(f"收到日线行情同步请求: symbol={symbol}, ts_code={ts_code}, {trade_date}")
        count = sync_service._sync_stock_daily(ts_code, trade_date=trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"日线行情同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_chip', methods=['POST'])
def sync_stock_chip_single():
    """筹码分布同步接口"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code', '').strip() or None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到筹码分布同步请求: ts_code={ts_code}, {start_date}-{end_date}")
        
        # 获取交易日历
        from services.data_access import DataAccessService
        data_access = DataAccessService()
        trade_cal_df = data_access.get_trade_cal(start_date, end_date)
        
        if trade_cal_df.empty:
            return jsonify({'count': 0, 'message': '未获取到交易日历数据'}), 200
        
        trade_dates = trade_cal_df[trade_cal_df['is_open'] == 1]['cal_date'].tolist()
        
        if not trade_dates:
            return jsonify({'count': 0, 'message': '日期范围内无交易日'}), 200
        
        total_count = 0
        
        if ts_code:
            # 同步指定股票
            for trade_date in trade_dates:
                try:
                    total_count += sync_service._sync_stock_chip(ts_code, trade_date=trade_date)
                except Exception as e:
                    logger.error(f"同步筹码失败 {ts_code} {trade_date}: {e}")
        else:
            # 同步所有股票
            from repositories import StockListRepository
            from utils.db import SessionLocal
            db = SessionLocal()
            try:
                stock_repo = StockListRepository(db)
                stocks = stock_repo.get_all_stocks()
                logger.info(f"开始同步所有股票筹码数据: {len(stocks)}只 × {len(trade_dates)}天")
                
                for stock in stocks:
                    for trade_date in trade_dates:
                        try:
                            total_count += sync_service._sync_stock_chip(stock.ts_code, trade_date=trade_date)
                        except Exception as e:
                            logger.error(f"同步筹码失败 {stock.ts_code} {trade_date}: {e}")
            finally:
                db.close()
        
        return jsonify({'count': total_count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"筹码分布同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_tech_factor', methods=['POST'])
def sync_stock_tech_factor_single():
    """技术因子同步接口"""
    try:
        data = request.get_json() or {}
        symbol = data.get('ts_code')  # 前端传symbol
        ts_code = symbol_to_ts_code(symbol) if symbol else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到技术因子同步请求: symbol={symbol}, ts_code={ts_code}, {start_date}-{end_date}")
        
        total_count = 0
        
        if ts_code:
            # 同步指定股票
            total_count = sync_service._sync_stock_tech_factor(ts_code, start_date=start_date, end_date=end_date)
        else:
            # 同步所有股票，遍历日期范围
            from services.tushare_client import TushareClient
            client = TushareClient()
            trade_cal_df = client.get_trade_cal(start_date=start_date, end_date=end_date, is_open='1')
            trade_dates = trade_cal_df['cal_date'].tolist()
            logger.info(f"开始同步所有股票技术因子: {len(trade_dates)}个交易日")
            
            for trade_date in trade_dates:
                try:
                    total_count += sync_service._sync_stock_tech_factor(None, trade_date=trade_date)
                except Exception as e:
                    logger.error(f"同步技术因子失败 {trade_date}: {e}")
        
        return jsonify({'count': total_count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"技术因子同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_tech_factor_pro', methods=['POST'])
def sync_stock_tech_factor_pro_single():
    """技术因子专业版同步接口"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code', '').strip() or None
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到技术因子专业版同步请求: ts_code={ts_code}, {start_date}-{end_date}")
        
        total_count = 0
        
        if ts_code:
            # 同步指定股票
            total_count = sync_service._sync_stock_tech_factor_pro(ts_code, start_date=start_date, end_date=end_date)
        else:
            # 同步所有股票，遍历日期范围
            from services.tushare_client import TushareClient
            client = TushareClient()
            trade_cal_df = client.get_trade_cal(start_date=start_date, end_date=end_date, is_open='1')
            trade_dates = trade_cal_df['cal_date'].tolist()
            logger.info(f"开始同步所有股票技术因子专业版: {len(trade_dates)}个交易日")
            
            for trade_date in trade_dates:
                try:
                    total_count += sync_service._sync_stock_tech_factor_pro(None, trade_date=trade_date)
                except Exception as e:
                    logger.error(f"同步技术因子专业版失败 {trade_date}: {e}")
        
        return jsonify({'count': total_count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"技术因子专业版同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_money_flow', methods=['POST'])
def sync_stock_money_flow_single():
    """个股资金流同步接口（支持日期范围）"""
    try:
        data = request.get_json() or {}
        symbol = data.get('ts_code')  # 前端传symbol
        ts_code = symbol_to_ts_code(symbol) if symbol else None
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到个股资金流同步请求: {ts_code or '全部'}, {start_date} - {end_date}")
        count = sync_service._sync_stock_money_flow(ts_code, start_date=start_date, end_date=end_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"个股资金流同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_money_flow_ths', methods=['POST'])
def sync_stock_money_flow_ths():
    """同花顺个股资金流向同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        logger.info(f"收到同花顺个股资金流向同步请求: {start_date} - {end_date}")
        result = sync_service.sync_stock_money_flow_ths(start_date, end_date)
        return jsonify({**result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"同花顺个股资金流向同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_money_flow_dc', methods=['POST'])
def sync_stock_money_flow_dc():
    """东方财富个股资金流向同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        logger.info(f"收到东方财富个股资金流向同步请求: {start_date} - {end_date}")
        result = sync_service.sync_stock_money_flow_dc(start_date, end_date)
        return jsonify({**result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"东方财富个股资金流向同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/block_dc_money_flow', methods=['POST'])
def sync_block_dc_money_flow():
    """东方财富板块资金流向同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        logger.info(f"收到东方财富板块资金流向同步请求: {start_date} - {end_date}")
        result = sync_service.sync_block_dc_money_flow(start_date, end_date)
        return jsonify({**result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"东方财富板块资金流向同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/industry_dc_money_flow', methods=['POST'])
def sync_industry_dc_money_flow():
    """东方财富行业资金流向同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        logger.info(f"收到东方财富行业资金流向同步请求: {start_date} - {end_date}")
        result = sync_service.sync_industry_dc_money_flow(start_date, end_date)
        return jsonify({**result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"东方财富行业资金流向同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

@app.route('/api/sync/block_ths_money_flow', methods=['POST'])
def sync_block_ths_money_flow_single():
    """板块资金流同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到板块资金流同步请求: {start_date} - {end_date}")
        
        # 获取交易日历
        from services.tushare_client import TushareClient
        client = TushareClient()
        trade_cal_df = client.get_trade_cal(start_date=start_date, end_date=end_date, is_open='1')
        trade_dates = trade_cal_df['cal_date'].tolist()
        
        total_count = 0
        for trade_date in trade_dates:
            try:
                count = sync_service._sync_block_ths_money_flow(trade_date)
                total_count += count
                logger.info(f"板块资金流同步成功: {trade_date}, {count}条")
            except Exception as e:
                logger.error(f"板块资金流同步失败 {trade_date}: {e}")
                continue
        
        return jsonify({'count': total_count, 'dates': len(trade_dates), 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"板块资金流同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/industry_ths_money_flow', methods=['POST'])
def sync_industry_ths_money_flow_single():
    """行业资金流同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到行业资金流同步请求: {start_date} - {end_date}")
        
        # 获取交易日历
        from services.tushare_client import TushareClient
        client = TushareClient()
        trade_cal_df = client.get_trade_cal(start_date=start_date, end_date=end_date, is_open='1')
        trade_dates = trade_cal_df['cal_date'].tolist()
        
        total_count = 0
        for trade_date in trade_dates:
            try:
                count = sync_service._sync_industry_ths_money_flow(trade_date)
                total_count += count
                logger.info(f"行业资金流同步成功: {trade_date}, {count}条")
            except Exception as e:
                logger.error(f"行业资金流同步失败 {trade_date}: {e}")
                continue
        
        return jsonify({'count': total_count, 'dates': len(trade_dates), 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"行业资金流同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_lhb_daily', methods=['POST'])
def sync_stock_lhb_daily_single():
    """龙虎榜每日统计同步接口"""
    try:
        data = request.get_json() or {}
        symbol = data.get('ts_code')  # 前端传symbol
        ts_code = symbol_to_ts_code(symbol) if symbol else None
        trade_date = data.get('trade_date')
        if not trade_date:
            return jsonify({'error': '请提供trade_date'}), 400
        logger.info(f"收到龙虎榜每日同步请求: {ts_code or '全部'}, {trade_date}")
        count = sync_service._sync_stock_lhb_daily(ts_code, trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"龙虎榜每日同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_lhb_inst', methods=['POST'])
def sync_stock_lhb_inst_single():
    """龙虎榜机构交易同步接口"""
    try:
        data = request.get_json() or {}
        symbol = data.get('ts_code')  # 前端传symbol
        ts_code = symbol_to_ts_code(symbol) if symbol else None
        trade_date = data.get('trade_date')
        if not trade_date:
            return jsonify({'error': '请提供trade_date'}), 400
        logger.info(f"收到龙虎榜机构同步请求: {ts_code or '全部'}, {trade_date}")
        count = sync_service._sync_stock_lhb_inst(ts_code, trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"龙虎榜机构同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/sync/stock_limit_status', methods=['POST'])
def sync_stock_limit_status_single():
    """涨跌停数据同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        
        logger.info(f"收到涨跌停数据同步请求: {start_date} - {end_date}")
        
        # 获取交易日历
        from services.tushare_client import TushareClient
        client = TushareClient()
        trade_cal_df = client.get_trade_cal(start_date=start_date, end_date=end_date, is_open='1')
        trade_dates = trade_cal_df['cal_date'].tolist()
        
        total_count = 0
        for trade_date in trade_dates:
            try:
                count = sync_service._sync_stock_limit_status(trade_date)
                total_count += count
                logger.info(f"涨跌停数据同步成功: {trade_date}, {count}条")
            except Exception as e:
                logger.error(f"涨跌停数据同步失败 {trade_date}: {e}")
                continue
        
        return jsonify({'count': total_count, 'dates': len(trade_dates), 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"涨跌停数据同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_limit_ladder', methods=['POST'])
def sync_stock_limit_ladder_single():
    """连板天梯同步接口"""
    try:
        data = request.get_json() or {}
        trade_date = data.get('trade_date')
        if not trade_date:
            return jsonify({'error': '请提供trade_date'}), 400
        logger.info(f"收到连板天梯同步请求: {trade_date}")
        count = sync_service._sync_stock_limit_ladder(trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"连板天梯同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/block_limit_strong', methods=['POST'])
def sync_block_limit_strong_single():
    """强势板块同步接口"""
    try:
        data = request.get_json() or {}
        trade_date = data.get('trade_date')
        if not trade_date:
            return jsonify({'error': '请提供trade_date'}), 400
        logger.info(f"收到强势板块同步请求: {trade_date}")
        count = sync_service._sync_block_limit_strong(trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"强势板块同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/stock_hot_money_daily', methods=['POST'])
def sync_stock_hot_money_daily_single():
    """游资每日明细同步接口"""
    try:
        data = request.get_json() or {}
        trade_date = data.get('trade_date')
        ts_code = data.get('ts_code', '').strip() or None
        if not trade_date:
            return jsonify({'error': '请提供trade_date'}), 400
        logger.info(f"收到游资每日明细同步请求: {trade_date}, ts_code={ts_code}")
        count = sync_service._sync_stock_hot_money_daily(trade_date, ts_code)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"游资每日明细同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/ths_index', methods=['POST'])
def sync_ths_index():
    """同花顺行业和概念板块同步接口"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code', '').strip() or None
        exchange = data.get('exchange', '').strip() or None
        type = data.get('type', '').strip() or None
        logger.info(f"收到同花顺板块同步请求: ts_code={ts_code}, exchange={exchange}, type={type}")
        count = sync_service.sync_ths_index(ts_code=ts_code, exchange=exchange, type=type)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"同花顺板块同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/ths_member', methods=['POST'])
def sync_ths_member():
    """同花顺板块成分同步接口"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code', '').strip() or None
        logger.info(f"收到同花顺板块成分同步请求: {ts_code or '全部'}")
        count = sync_service.sync_ths_member(ts_code)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"同花顺板块成分同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/ths_daily', methods=['POST'])
def sync_ths_daily():
    """同花顺板块每日行情同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        logger.info(f"收到同花顺板块行情同步请求: {start_date} - {end_date}")
        result = sync_service.sync_ths_daily(start_date, end_date)
        return jsonify({**result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"同花顺板块行情同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/dc_index', methods=['POST'])
def sync_dc_index():
    """东方财富概念板块同步接口"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code', '').strip() or None
        name = data.get('name', '').strip() or None
        trade_date = data.get('trade_date', '').strip() or None
        logger.info(f"收到东方财富板块同步请求: ts_code={ts_code}, name={name}, trade_date={trade_date}")
        count = sync_service.sync_dc_index(ts_code=ts_code, name=name, trade_date=trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"东方财富板块同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/dc_member', methods=['POST'])
def sync_dc_member():
    """东方财富板块成分同步接口"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code', '').strip() or None
        trade_date = data.get('trade_date', '').strip() or None
        logger.info(f"收到东方财富板块成分同步请求: ts_code={ts_code}, trade_date={trade_date}")
        count = sync_service.sync_dc_member(ts_code=ts_code, trade_date=trade_date)
        return jsonify({'count': count, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"东方财富板块成分同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/dc_daily', methods=['POST'])
def sync_dc_daily():
    """东方财富板块每日行情同步接口"""
    try:
        data = request.get_json() or {}
        start_date = data.get('start_date', '').strip()
        end_date = data.get('end_date', '').strip()
        idx_type = data.get('idx_type', '').strip() or None
        if not start_date or not end_date:
            return jsonify({'error': '请提供start_date和end_date'}), 400
        logger.info(f"收到东方财富板块行情同步请求: {start_date} - {end_date}, type={idx_type}")
        result = sync_service.sync_dc_daily(start_date, end_date, idx_type=idx_type)
        return jsonify({**result, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"东方财富板块行情同步失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


