from flask import Blueprint, jsonify, request
from utils.db import SessionLocal
from utils.logger import get_logger
from sqlalchemy import and_, or_, func
from models import StockList, StockDaily, StockTechFactorPro, StockLimitStatus, StockHolder, StockChip, StockMoneyFlow
from repositories import StockListRepository

logger = get_logger(__name__)

stock_query_bp = Blueprint('stock_query', __name__)

@stock_query_bp.route('/api/stocks/list', methods=['POST'])
def get_stock_list():
    """获取股票列表（带搜索和分页）"""
    try:
        data = request.get_json() or {}
        trade_date = data.get('trade_date')
        ts_code = data.get('ts_code', '').strip()
        name = data.get('name', '').strip()
        industry = data.get('industry', '').strip()
        area = data.get('area', '').strip()
        market = data.get('market', '').strip()
        pct_chg_min = data.get('pct_chg_min')
        pct_chg_max = data.get('pct_chg_max')
        close_min = data.get('close_min')
        close_max = data.get('close_max')
        limit_status = data.get('limit_status', '').strip()
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        if not trade_date:
            return jsonify({'error': '交易日期为必填项'}), 400
        
        db = SessionLocal()
        try:
            # 基础查询
            query = db.query(
                StockList.ts_code,
                StockList.name,
                StockList.list_date,
                StockList.industry,
                StockList.area,
                StockList.market,
                StockDaily.trade_date,
                StockDaily.open,
                StockDaily.close,
                StockDaily.pct_chg,
                StockDaily.vol,
                StockDaily.amount,
                StockTechFactorPro.turnover_rate,
                StockTechFactorPro.turnover_rate_f
            ).join(
                StockDaily, and_(
                    StockList.ts_code == StockDaily.ts_code,
                    StockDaily.trade_date == trade_date
                )
            ).outerjoin(
                StockTechFactorPro, and_(
                    StockList.ts_code == StockTechFactorPro.ts_code,
                    StockTechFactorPro.trade_date == trade_date
                )
            )
            
            # 涨跌停筛选
            if limit_status and limit_status != '正常':
                limit_query = db.query(StockLimitStatus.ts_code).filter(
                    StockLimitStatus.trade_date == trade_date,
                    StockLimitStatus.limit == limit_status
                )
                limit_ts_codes = [row[0] for row in limit_query.all()]
                if limit_ts_codes:
                    query = query.filter(StockList.ts_code.in_(limit_ts_codes))
                else:
                    return jsonify({'total': 0, 'data': [], 'page': page, 'page_size': page_size})
            
            # 其他筛选条件
            if ts_code:
                query = query.filter(StockList.ts_code.like(f'%{ts_code}%'))
            if name:
                query = query.filter(StockList.name.like(f'%{name}%'))
            if industry:
                query = query.filter(StockList.industry == industry)
            if area:
                query = query.filter(StockList.area == area)
            if market:
                query = query.filter(StockList.market == market)
            if pct_chg_min is not None:
                query = query.filter(StockDaily.pct_chg >= pct_chg_min)
            if pct_chg_max is not None:
                query = query.filter(StockDaily.pct_chg <= pct_chg_max)
            if close_min is not None:
                query = query.filter(StockDaily.close >= close_min)
            if close_max is not None:
                query = query.filter(StockDaily.close <= close_max)
            
            # 总数
            total = query.count()
            
            # 分页
            offset = (page - 1) * page_size
            results = query.offset(offset).limit(page_size).all()
            
            # 格式化数据
            data_list = []
            for row in results:
                data_list.append({
                    'ts_code': row.ts_code,
                    'name': row.name,
                    'list_date': row.list_date,
                    'industry': row.industry,
                    'area': row.area,
                    'market': row.market,
                    'trade_date': row.trade_date,
                    'open': float(row.open) if row.open else None,
                    'close': float(row.close) if row.close else None,
                    'pct_chg': float(row.pct_chg) if row.pct_chg else None,
                    'vol': float(row.vol) if row.vol else None,
                    'amount': float(row.amount) if row.amount else None,
                    'turnover_rate': float(row.turnover_rate) if row.turnover_rate else None,
                    'turnover_rate_f': float(row.turnover_rate_f) if row.turnover_rate_f else None
                })
            
            return jsonify({
                'total': total,
                'data': data_list,
                'page': page,
                'page_size': page_size
            })
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@stock_query_bp.route('/api/stocks/detail/<ts_code>', methods=['GET'])
def get_stock_detail(ts_code):
    """获取股票详情"""
    try:
        db = SessionLocal()
        try:
            # 基本信息
            stock_info = db.query(StockList).filter(StockList.ts_code == ts_code).first()
            if not stock_info:
                return jsonify({'error': '股票不存在'}), 404
            
            # 股东信息（最新）
            holder_info = db.query(StockHolder).filter(
                StockHolder.ts_code == ts_code
            ).order_by(StockHolder.ann_date.desc()).first()
            
            # 最新交易日
            latest_daily = db.query(StockDaily).filter(
                StockDaily.ts_code == ts_code
            ).order_by(StockDaily.trade_date.desc()).first()
            
            latest_trade_date = latest_daily.trade_date if latest_daily else None
            
            # 最新交易日的技术指标
            latest_tech = None
            if latest_trade_date:
                latest_tech = db.query(StockTechFactorPro).filter(
                    StockTechFactorPro.ts_code == ts_code,
                    StockTechFactorPro.trade_date == latest_trade_date
                ).first()
            
            # 最新交易日的资金流向
            latest_money_flow = None
            if latest_trade_date:
                latest_money_flow = db.query(StockMoneyFlow).filter(
                    StockMoneyFlow.ts_code == ts_code,
                    StockMoneyFlow.trade_date == latest_trade_date
                ).first()
            
            result = {
                'basic_info': {
                    'ts_code': stock_info.ts_code,
                    'name': stock_info.name,
                    'list_date': stock_info.list_date,
                    'industry': stock_info.industry,
                    'area': stock_info.area,
                    'market': stock_info.market
                },
                'holder_info': {
                    'ann_date': holder_info.ann_date,
                    'end_date': holder_info.end_date,
                    'holder_num': holder_info.holder_num,
                    'holder_ratio': float(holder_info.holder_ratio) if holder_info.holder_ratio else None
                } if holder_info else None,
                'latest_daily': {
                    'trade_date': latest_daily.trade_date,
                    'open': float(latest_daily.open) if latest_daily.open else None,
                    'high': float(latest_daily.high) if latest_daily.high else None,
                    'low': float(latest_daily.low) if latest_daily.low else None,
                    'close': float(latest_daily.close) if latest_daily.close else None,
                    'pre_close': float(latest_daily.pre_close) if latest_daily.pre_close else None,
                    'change': float(latest_daily.change) if latest_daily.change else None,
                    'pct_chg': float(latest_daily.pct_chg) if latest_daily.pct_chg else None,
                    'vol': float(latest_daily.vol) if latest_daily.vol else None,
                    'amount': float(latest_daily.amount) if latest_daily.amount else None
                } if latest_daily else None,
                'latest_tech': _format_tech_factor(latest_tech) if latest_tech else None,
                'latest_money_flow': {
                    'buy_sm_amount': float(latest_money_flow.buy_sm_amount) if latest_money_flow.buy_sm_amount else None,
                    'buy_md_amount': float(latest_money_flow.buy_md_amount) if latest_money_flow.buy_md_amount else None,
                    'buy_lg_amount': float(latest_money_flow.buy_lg_amount) if latest_money_flow.buy_lg_amount else None,
                    'buy_elg_amount': float(latest_money_flow.buy_elg_amount) if latest_money_flow.buy_elg_amount else None,
                    'sell_sm_amount': float(latest_money_flow.sell_sm_amount) if latest_money_flow.sell_sm_amount else None,
                    'sell_md_amount': float(latest_money_flow.sell_md_amount) if latest_money_flow.sell_md_amount else None,
                    'sell_lg_amount': float(latest_money_flow.sell_lg_amount) if latest_money_flow.sell_lg_amount else None,
                    'sell_elg_amount': float(latest_money_flow.sell_elg_amount) if latest_money_flow.sell_elg_amount else None,
                    'net_mf_amount': float(latest_money_flow.net_mf_amount) if latest_money_flow.net_mf_amount else None
                } if latest_money_flow else None
            }
            
            return jsonify(result)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取股票详情失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@stock_query_bp.route('/api/stocks/kline/<ts_code>', methods=['GET'])
def get_stock_kline(ts_code):
    """获取K线数据"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        db = SessionLocal()
        try:
            query = db.query(StockDaily).filter(StockDaily.ts_code == ts_code)
            
            if start_date:
                query = query.filter(StockDaily.trade_date >= start_date)
            if end_date:
                query = query.filter(StockDaily.trade_date <= end_date)
            
            results = query.order_by(StockDaily.trade_date).all()
            
            data_list = []
            for row in results:
                data_list.append({
                    'trade_date': row.trade_date,
                    'open': float(row.open) if row.open else None,
                    'high': float(row.high) if row.high else None,
                    'low': float(row.low) if row.low else None,
                    'close': float(row.close) if row.close else None,
                    'vol': float(row.vol) if row.vol else None,
                    'amount': float(row.amount) if row.amount else None
                })
            
            return jsonify({'data': data_list})
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@stock_query_bp.route('/api/stocks/day_info/<ts_code>/<trade_date>', methods=['GET'])
def get_stock_day_info(ts_code, trade_date):
    """获取指定交易日信息"""
    try:
        db = SessionLocal()
        try:
            # 交易数据
            daily = db.query(StockDaily).filter(
                StockDaily.ts_code == ts_code,
                StockDaily.trade_date == trade_date
            ).first()
            
            # 技术指标
            tech = db.query(StockTechFactorPro).filter(
                StockTechFactorPro.ts_code == ts_code,
                StockTechFactorPro.trade_date == trade_date
            ).first()
            
            # 资金流向
            money_flow = db.query(StockMoneyFlow).filter(
                StockMoneyFlow.ts_code == ts_code,
                StockMoneyFlow.trade_date == trade_date
            ).first()
            
            # 筹码分布
            chips = db.query(StockChip).filter(
                StockChip.ts_code == ts_code,
                StockChip.trade_date == trade_date
            ).order_by(StockChip.price).all()
            
            chip_data = None
            if chips:
                chip_data = {
                    'prices': [float(c.price) for c in chips],
                    'percents': [float(c.percent) if c.percent else 0 for c in chips]
                }
            
            result = {
                'daily': {
                    'trade_date': daily.trade_date,
                    'open': float(daily.open) if daily.open else None,
                    'high': float(daily.high) if daily.high else None,
                    'low': float(daily.low) if daily.low else None,
                    'close': float(daily.close) if daily.close else None,
                    'pre_close': float(daily.pre_close) if daily.pre_close else None,
                    'change': float(daily.change) if daily.change else None,
                    'pct_chg': float(daily.pct_chg) if daily.pct_chg else None,
                    'vol': float(daily.vol) if daily.vol else None,
                    'amount': float(daily.amount) if daily.amount else None
                } if daily else None,
                'tech': _format_tech_factor(tech) if tech else None,
                'money_flow': {
                    'buy_sm_amount': float(money_flow.buy_sm_amount) if money_flow.buy_sm_amount else None,
                    'buy_md_amount': float(money_flow.buy_md_amount) if money_flow.buy_md_amount else None,
                    'buy_lg_amount': float(money_flow.buy_lg_amount) if money_flow.buy_lg_amount else None,
                    'buy_elg_amount': float(money_flow.buy_elg_amount) if money_flow.buy_elg_amount else None,
                    'sell_sm_amount': float(money_flow.sell_sm_amount) if money_flow.sell_sm_amount else None,
                    'sell_md_amount': float(money_flow.sell_md_amount) if money_flow.sell_md_amount else None,
                    'sell_lg_amount': float(money_flow.sell_lg_amount) if money_flow.sell_lg_amount else None,
                    'sell_elg_amount': float(money_flow.sell_elg_amount) if money_flow.sell_elg_amount else None,
                    'net_mf_amount': float(money_flow.net_mf_amount) if money_flow.net_mf_amount else None
                } if money_flow else None,
                'chip': chip_data
            }
            
            return jsonify(result)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"获取指定交易日信息失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def _format_tech_factor(tech):
    """格式化技术指标数据（只返回主要指标）"""
    if not tech:
        return None
    return {
        'turnover_rate': float(tech.turnover_rate) if tech.turnover_rate else None,
        'turnover_rate_f': float(tech.turnover_rate_f) if tech.turnover_rate_f else None,
        'volume_ratio': float(tech.volume_ratio) if tech.volume_ratio else None,
        'pe': float(tech.pe) if tech.pe else None,
        'pe_ttm': float(tech.pe_ttm) if tech.pe_ttm else None,
        'pb': float(tech.pb) if tech.pb else None,
        'ps': float(tech.ps) if tech.ps else None,
        'ps_ttm': float(tech.ps_ttm) if tech.ps_ttm else None,
        'total_share': float(tech.total_share) if tech.total_share else None,
        'float_share': float(tech.float_share) if tech.float_share else None,
        'total_mv': float(tech.total_mv) if tech.total_mv else None,
        'circ_mv': float(tech.circ_mv) if tech.circ_mv else None
    }
