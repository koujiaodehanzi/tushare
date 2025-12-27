from flask import Blueprint, jsonify, request
from utils.db import SessionLocal
from utils.logger import get_logger
from models import StockList, StockDaily, StockLimitStatus
from sqlalchemy import and_

logger = get_logger(__name__)

backtest_bp = Blueprint('backtest', __name__)

@backtest_bp.route('/api/backtest/strategy1', methods=['POST'])
def backtest_strategy1():
    """策略一：连续n天下跌后第n+1天的表现"""
    try:
        data = request.get_json() or {}
        n = data.get('n', 3)  # 默认3天
        
        if not isinstance(n, int) or n < 1:
            return jsonify({'error': 'n必须是大于0的整数'}), 400
        
        logger.info(f"开始执行策略一回测，参数n={n}")
        
        db = SessionLocal()
        try:
            # 1. 查询主板股票列表
            stocks = db.query(StockList).filter(StockList.market == '主板').all()
            logger.info(f"找到{len(stocks)}只主板股票")
            
            A = 0  # 涨幅>=0.2的次数
            B = 0  # 涨幅<0.2的次数
            
            # 2. 遍历股票列表
            for stock in stocks:
                ts_code = stock.ts_code
                
                # 3. 查询该股票所有日线数据，按日期升序
                daily_records = db.query(StockDaily).filter(
                    StockDaily.ts_code == ts_code
                ).order_by(StockDaily.trade_date).all()
                
                if len(daily_records) < n + 2:
                    continue
                
                # 4. 滑动窗口处理
                i = 0
                while i <= len(daily_records) - (n + 2):
                    # 窗口大小为n+2
                    window = daily_records[i:i + n + 2]
                    
                    # 检查是否符合条件
                    # a. 窗口最左侧：空记录或开盘价<收盘价
                    left_record = daily_records[i] if i > 0 else None
                    if left_record and left_record.open >= left_record.close:
                        i += 1
                        continue
                    
                    # b. 窗口最左侧后面连续n+1条都有记录
                    if len(window) < n + 2:
                        break
                    
                    # c. 窗口最左侧后面连续n条记录的开盘价都大于收盘价
                    valid = True
                    for j in range(1, n + 1):
                        if window[j].open <= window[j].close:
                            valid = False
                            break
                    
                    if not valid:
                        i += 1
                        continue
                    
                    # 符合条件，计算窗口最右侧记录的涨幅
                    right_record = window[n + 1]
                    if right_record.open and right_record.open > 0:
                        pct_change = (right_record.close - right_record.open) / right_record.open
                        
                        if pct_change >= 2:  # 2%
                            A += 1
                        else:
                            B += 1
                    
                    # 移动窗口
                    i += n + 2
            
            logger.info(f"策略一回测完成，A={A}, B={B}")
            
            return jsonify({
                'strategy': 'strategy1',
                'params': {'n': n},
                'result': {
                    'A': A,
                    'B': B,
                    'total': A + B,
                    'success_rate': round(A / (A + B) * 100, 2) if (A + B) > 0 else 0
                }
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略一回测失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@backtest_bp.route('/api/backtest/strategy2', methods=['POST'])
def backtest_strategy2():
    """策略二：首板后第二天的表现"""
    try:
        data = request.get_json() or {}
        m = data.get('m', 5)
        n = data.get('n', 2)
        
        if not isinstance(m, int) or m < 1:
            return jsonify({'error': 'm必须是大于0的整数'}), 400
        if not isinstance(n, (int, float)) or n < 0:
            return jsonify({'error': 'n必须是大于等于0的数字'}), 400
        
        logger.info(f"开始执行策略二回测，参数m={m}, n={n}")
        
        db = SessionLocal()
        try:
            stocks = db.query(StockList).filter(StockList.market == '主板').all()
            logger.info(f"找到{len(stocks)}只主板股票")
            
            A = 0
            B = 0
            details = []  # 存储满足条件的详细信息
            
            for stock in stocks:
                ts_code = stock.ts_code
                stock_name = stock.name
                
                daily_records = db.query(StockDaily).filter(
                    StockDaily.ts_code == ts_code
                ).order_by(StockDaily.trade_date).all()
                
                if len(daily_records) < m + 2:
                    continue
                
                limit_records = db.query(StockLimitStatus).filter(
                    StockLimitStatus.ts_code == ts_code
                ).all()
                
                limit_dict = {r.trade_date: r for r in limit_records}
                
                i = 0
                while i <= len(daily_records) - (m + 2):
                    window = daily_records[i:i + m + 2]
                    
                    if len(window) < m + 2:
                        break
                    
                    has_limit = False
                    for j in range(m):
                        trade_date = window[j].trade_date
                        if trade_date in limit_dict:
                            limit_status = limit_dict[trade_date].limit
                            if limit_status in ['U', 'Z']:
                                has_limit = True
                                break
                    
                    if has_limit:
                        i += 1
                        continue
                    
                    m_plus_1_date = window[m].trade_date
                    if m_plus_1_date not in limit_dict:
                        i += 1
                        continue
                    
                    limit_status = limit_dict[m_plus_1_date].limit
                    if limit_status not in ['U', 'Z']:
                        i += 1
                        continue
                    
                    right_record = window[m + 1]
                    m_plus_1_record = window[m]
                    
                    if right_record.close >= right_record.open and m_plus_1_record.close and m_plus_1_record.close > 0:
                        pct_change = (right_record.close - m_plus_1_record.close) / m_plus_1_record.close * 100
                        
                        if pct_change >= n:
                            A += 1
                            # 记录详细信息
                            details.append({
                                'ts_code': ts_code,
                                'stock_name': stock_name,
                                'limit_date': m_plus_1_date,
                                'next_date': right_record.trade_date,
                                'pct_change': round(pct_change, 2)
                            })
                        else:
                            B += 1
                    else:
                        B += 1
                    
                    i += m + 2
            
            logger.info(f"策略二回测完成，A={A}, B={B}")
            
            return jsonify({
                'strategy': 'strategy2',
                'params': {'m': m, 'n': n},
                'result': {
                    'A': A,
                    'B': B,
                    'total': A + B,
                    'success_rate': round(A / (A + B) * 100, 2) if (A + B) > 0 else 0,
                    'details': details
                }
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略二回测失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@backtest_bp.route('/api/backtest/strategy3', methods=['POST'])
def backtest_strategy3():
    """策略三：m连板后k日涨幅统计"""
    try:
        data = request.get_json() or {}
        m = data.get('m', 2)  # 连板天数
        k = data.get('k', 1)  # 后续观察天数
        n = data.get('n', 2)  # 涨幅阈值(%)
        
        if not isinstance(m, int) or m < 1:
            return jsonify({'error': 'm必须是大于0的整数'}), 400
        if not isinstance(k, int) or k < 1:
            return jsonify({'error': 'k必须是大于0的整数'}), 400
        if not isinstance(n, (int, float)) or n < 0:
            return jsonify({'error': 'n必须是大于等于0的数字'}), 400
        
        logger.info(f"开始执行策略三回测，参数m={m}, k={k}, n={n}")
        
        db = SessionLocal()
        try:
            # 1. 查询主板股票列表
            stocks = db.query(StockList).filter(StockList.market == '主板').all()
            logger.info(f"找到{len(stocks)}只主板股票")
            
            A = 0  # 涨幅>=n的次数
            B = 0  # 涨幅<n的次数
            details = []  # 存储所有命中窗口的详细信息
            
            # 2. 遍历股票列表
            for stock in stocks:
                ts_code = stock.ts_code
                stock_name = stock.name
                
                # 3. 查询该股票所有日线数据和涨停数据，按日期升序
                daily_records = db.query(StockDaily).filter(
                    StockDaily.ts_code == ts_code
                ).order_by(StockDaily.trade_date).all()
                
                if len(daily_records) < m + k:
                    continue
                
                limit_records = db.query(StockLimitStatus).filter(
                    StockLimitStatus.ts_code == ts_code
                ).all()
                
                # 构建涨停数据字典，key为trade_date
                limit_dict = {r.trade_date: r for r in limit_records}
                
                # 4. 滑动窗口处理，窗口大小为m+k
                i = 0
                while i <= len(daily_records) - (m + k):
                    window = daily_records[i:i + m + k]
                    
                    if len(window) < m + k:
                        break
                    
                    # a. 检查窗口最左侧的m条数据是否都涨停
                    all_limit = True
                    for j in range(m):
                        trade_date = window[j].trade_date
                        if trade_date not in limit_dict:
                            all_limit = False
                            break
                        
                        limit_status = limit_dict[trade_date].limit
                        if limit_status != 'U':  # U表示涨停
                            all_limit = False
                            break
                    
                    if not all_limit:
                        i += 1
                        continue
                    
                    # b. 符合条件，计算窗口第m+k天相对第m天的涨幅
                    k_day_record = window[m + k - 1]  # 第m+k天记录
                    m_record = window[m - 1]  # 第m天记录
                    left_date = window[0].trade_date  # 窗口最左侧日期
                    
                    # 检查第m+k天开盘价大于收盘价（即下跌）
                    if k_day_record.open and k_day_record.close and k_day_record.open > k_day_record.close:
                        # 计算第m+k天收盘价相比于第m天收盘价的涨幅
                        if m_record.close and m_record.close > 0:
                            pct_change = (k_day_record.close - m_record.close) / m_record.close * 100
                            
                            match_condition = pct_change >= n
                            if match_condition:
                                A += 1
                            else:
                                B += 1
                            
                            # 记录详细信息
                            details.append({
                                'ts_code': ts_code,
                                'stock_name': stock_name,
                                'match_condition': '是' if match_condition else '否',
                                'left_date': str(left_date),
                                'pct_change': round(pct_change, 2)
                            })
                    
                    # c. 移动窗口到下一个可能的位置
                    i += 1
            
            logger.info(f"策略三回测完成，A={A}, B={B}, 详细记录={len(details)}条")
            
            return jsonify({
                'strategy': 'strategy3',
                'params': {'m': m, 'k': k, 'n': n},
                'result': {
                    'A': A,
                    'B': B,
                    'total': A + B,
                    'success_rate': round(A / (A + B) * 100, 2) if (A + B) > 0 else 0,
                    'details': details
                }
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"策略三回测失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
