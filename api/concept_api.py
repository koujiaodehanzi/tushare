from flask import Blueprint, jsonify, request
from utils.db import SessionLocal
from utils.logger import get_logger
from models import ThsIndustryAndBlock, ThsIndustryAndBlockDetail, StockDaily, StockList
from sqlalchemy import and_, or_

logger = get_logger(__name__)

concept_bp = Blueprint('concept', __name__)

@concept_bp.route('/api/concept/filter', methods=['POST'])
def filter_stocks_by_concept():
    """根据概念筛选股票"""
    try:
        data = request.get_json() or {}
        base_concepts = data.get('base_concepts', [])  # 基础概念列表
        filter_concepts = data.get('filter_concepts', [])  # 必须包含的概念列表
        stock_names = data.get('stock_names', [])  # 股票名称关键词列表
        
        if not base_concepts and not stock_names:
            return jsonify({'error': '请至少提供一个基础概念或股票名称'}), 400
        
        logger.info(f"概念筛选: base={base_concepts}, filter={filter_concepts}, names={stock_names}")
        
        db = SessionLocal()
        try:
            # 1. 获取基础概念下的所有股票（模糊匹配）
            if base_concepts:
                # 构建模糊匹配条件
                concept_filters = []
                for concept in base_concepts:
                    concept_filters.append(ThsIndustryAndBlock.name.like(f'%{concept}%'))
                
                base_stock_codes = db.query(ThsIndustryAndBlockDetail.con_code).distinct().join(
                    ThsIndustryAndBlock,
                    ThsIndustryAndBlockDetail.ts_code == ThsIndustryAndBlock.ts_code
                ).filter(
                    or_(*concept_filters)
                ).all()
                
                stock_codes = [code[0] for code in base_stock_codes]
            else:
                # 如果没有基础概念，获取所有股票
                all_stock_codes = db.query(ThsIndustryAndBlockDetail.con_code).distinct().all()
                stock_codes = [code[0] for code in all_stock_codes]
            
            if not stock_codes:
                return jsonify({
                    'stocks': [],
                    'total': 0,
                    'message': '未找到符合基础概念的股票'
                })
            
            # 2. 获取这些股票的所有概念
            stock_concepts = db.query(
                ThsIndustryAndBlockDetail.con_code,
                ThsIndustryAndBlockDetail.con_name,
                ThsIndustryAndBlock.name.label('concept_name')
            ).join(
                ThsIndustryAndBlock,
                ThsIndustryAndBlockDetail.ts_code == ThsIndustryAndBlock.ts_code
            ).filter(
                ThsIndustryAndBlockDetail.con_code.in_(stock_codes),
                ~ThsIndustryAndBlock.name.like('%上证%'),
                ~ThsIndustryAndBlock.name.like('%中证%'),
                ~ThsIndustryAndBlock.name.like('%同花顺%'),
                ~ThsIndustryAndBlock.name.like('%昨日%'),
                ~ThsIndustryAndBlock.name.like('%深股通%'),
                ~ThsIndustryAndBlock.name.like('%深市新主板%'),
                ~ThsIndustryAndBlock.name.like('%最近多板%'),
                ~ThsIndustryAndBlock.name.like('%新高%'),
                ~ThsIndustryAndBlock.name.like('%指数%'),
                ~ThsIndustryAndBlock.name.like('%高市盈率%'),
                ~ThsIndustryAndBlock.name.like('%高市净率%'),
                ~ThsIndustryAndBlock.name.like('%高贝塔值%')
            ).all()
            
            # 3. 按股票分组概念
            stock_dict = {}
            for con_code, con_name, concept_name in stock_concepts:
                if con_code not in stock_dict:
                    stock_dict[con_code] = {
                        'ts_code': con_code,
                        'name': con_name,
                        'concepts': []
                    }
                stock_dict[con_code]['concepts'].append(concept_name)
            
            # 4. 筛选包含所有必须概念的股票
            result_stocks = []
            filtered_stock_codes = []
            
            for stock_code, stock_info in stock_dict.items():
                concepts_set = set(stock_info['concepts'])
                stock_name = stock_info['name']
                
                # 检查股票名称是否匹配（模糊匹配）
                if stock_names:
                    if not any(sn in stock_name for sn in stock_names):
                        continue
                
                # 检查是否包含所有必须的概念（模糊匹配）
                if filter_concepts:
                    match_all = True
                    for fc in filter_concepts:
                        # 检查是否有任何概念包含该关键词
                        if not any(fc in concept for concept in concepts_set):
                            match_all = False
                            break
                    
                    if match_all:
                        result_stocks.append({
                            'ts_code': stock_info['ts_code'],
                            'name': stock_info['name'],
                            'concepts': ', '.join(sorted(stock_info['concepts']))
                        })
                        filtered_stock_codes.append(stock_code)
                else:
                    result_stocks.append({
                        'ts_code': stock_info['ts_code'],
                        'name': stock_info['name'],
                        'concepts': ', '.join(sorted(stock_info['concepts']))
                    })
                    filtered_stock_codes.append(stock_code)
            
            # 5. 批量获取所有股票的日线数据和市场信息
            if filtered_stock_codes:
                # 获取股票市场信息
                stock_list_data = db.query(StockList).filter(
                    StockList.ts_code.in_(filtered_stock_codes)
                ).all()
                
                market_dict = {s.ts_code: s.market for s in stock_list_data}
                
                all_daily_data = db.query(StockDaily).filter(
                    StockDaily.ts_code.in_(filtered_stock_codes)
                ).order_by(StockDaily.ts_code, StockDaily.trade_date.desc()).all()
                
                # 按股票分组
                daily_dict = {}
                for record in all_daily_data:
                    if record.ts_code not in daily_dict:
                        daily_dict[record.ts_code] = []
                    daily_dict[record.ts_code].append(record)
                
                # 计算每只股票的涨幅
                for stock in result_stocks:
                    ts_code = stock['ts_code']
                    daily_list = daily_dict.get(ts_code, [])
                    market = market_dict.get(ts_code)
                    
                    stock['market'] = market
                    
                    # 获取最新股价
                    if len(daily_list) >= 1:
                        stock['latest_price'] = daily_list[0].close
                    else:
                        stock['latest_price'] = None
                    
                    # 计算单日涨幅（最近交易日）
                    if len(daily_list) >= 1:
                        stock['pct_1d'] = daily_list[0].pct_chg if daily_list[0].pct_chg else None
                    else:
                        stock['pct_1d'] = None
                    
                    # 计算9日涨幅
                    if len(daily_list) >= 10:
                        close_today = daily_list[0].close
                        close_9d = daily_list[9].close
                        if close_today and close_9d and close_9d > 0:
                            stock['pct_9d'] = round((close_today - close_9d) / close_9d * 100, 2)
                        else:
                            stock['pct_9d'] = None
                    else:
                        stock['pct_9d'] = None
                    
                    # 计算10日涨幅
                    if len(daily_list) >= 11:
                        close_today = daily_list[0].close
                        close_10d = daily_list[10].close
                        if close_today and close_10d and close_10d > 0:
                            stock['pct_10d'] = round((close_today - close_10d) / close_10d * 100, 2)
                        else:
                            stock['pct_10d'] = None
                    else:
                        stock['pct_10d'] = None
                    
                    # 计算20日涨幅
                    if len(daily_list) >= 21:
                        close_today = daily_list[0].close
                        close_20d = daily_list[20].close
                        if close_today and close_20d and close_20d > 0:
                            stock['pct_20d'] = round((close_today - close_20d) / close_20d * 100, 2)
                        else:
                            stock['pct_20d'] = None
                    else:
                        stock['pct_20d'] = None
                    
                    # 计算29日涨幅
                    if len(daily_list) >= 30:
                        close_today = daily_list[0].close
                        close_29d = daily_list[29].close
                        if close_today and close_29d and close_29d > 0:
                            stock['pct_29d'] = round((close_today - close_29d) / close_29d * 100, 2)
                        else:
                            stock['pct_29d'] = None
                    else:
                        stock['pct_29d'] = None
                    
                    # 计算30日涨幅
                    if len(daily_list) >= 31:
                        close_today = daily_list[0].close
                        close_30d = daily_list[30].close
                        if close_today and close_30d and close_30d > 0:
                            stock['pct_30d'] = round((close_today - close_30d) / close_30d * 100, 2)
                        else:
                            stock['pct_30d'] = None
                    else:
                        stock['pct_30d'] = None
                    
                    # 计算异动阈值（主板、科创板、创业板）
                    if market in ['主板', '科创板', '创业板']:
                        # 10日异动阈值
                        if stock['pct_9d'] is not None:
                            if stock['pct_9d'] >= 100:
                                stock['alert_10d'] = 'triggered'
                            else:
                                threshold = ((2 / (1 + stock['pct_9d']/100)) - 1) * 100
                                stock['alert_10d'] = round(threshold, 2)
                        else:
                            stock['alert_10d'] = None
                        
                        # 30日异动阈值
                        if stock['pct_29d'] is not None:
                            if stock['pct_29d'] >= 200:
                                stock['alert_30d'] = 'triggered'
                            else:
                                threshold = ((3 / (1 + stock['pct_29d']/100)) - 1) * 100
                                stock['alert_30d'] = round(threshold, 2)
                        else:
                            stock['alert_30d'] = None
                    else:
                        stock['alert_10d'] = None
                        stock['alert_30d'] = None
            
            logger.info(f"筛选完成，共{len(result_stocks)}只股票")
            
            # 如果有基础概念，查询基础概念的关联度
            base_concept_scores = {}
            if base_concepts and filtered_stock_codes:
                from models import StockConceptAnalysis
                
                # 查询所有股票对基础概念的关联度
                concept_analysis = db.query(
                    StockConceptAnalysis.ts_code,
                    StockConceptAnalysis.concept_name,
                    StockConceptAnalysis.relevance_score
                ).filter(
                    StockConceptAnalysis.ts_code.in_(filtered_stock_codes),
                    StockConceptAnalysis.concept_name.in_(base_concepts)
                ).all()
                
                # 按股票代码分组，计算平均关联度
                for ts_code, concept_name, score in concept_analysis:
                    if ts_code not in base_concept_scores:
                        base_concept_scores[ts_code] = []
                    base_concept_scores[ts_code].append(score)
                
                # 计算每只股票的平均关联度
                for ts_code in base_concept_scores:
                    scores = base_concept_scores[ts_code]
                    base_concept_scores[ts_code] = round(sum(scores) / len(scores), 1) if scores else None
            
            # 添加基础概念关联度到结果
            for stock in result_stocks:
                stock['base_concept_score'] = base_concept_scores.get(stock['ts_code'])
            
            return jsonify({
                'stocks': result_stocks,
                'total': len(result_stocks),
                'params': {
                    'base_concepts': base_concepts,
                    'filter_concepts': filter_concepts,
                    'stock_names': stock_names
                }
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"概念筛选失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/api/concept/list', methods=['GET'])
def get_concept_list():
    """获取所有概念列表"""
    try:
        db = SessionLocal()
        try:
            concepts = db.query(
                ThsIndustryAndBlock.name
            ).filter(
                ~ThsIndustryAndBlock.name.like('%上证%'),
                ~ThsIndustryAndBlock.name.like('%中证%'),
                ~ThsIndustryAndBlock.name.like('%同花顺%'),
                ~ThsIndustryAndBlock.name.like('%昨日%')
            ).distinct().order_by(ThsIndustryAndBlock.name).all()
            
            concept_list = [c[0] for c in concepts]
            
            return jsonify({
                'concepts': concept_list,
                'total': len(concept_list)
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"获取概念列表失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/api/concept/analysis', methods=['GET'])
def get_concept_analysis():
    """获取股票概念分析数据"""
    try:
        ts_code = request.args.get('ts_code')
        if not ts_code:
            return jsonify({'error': '缺少ts_code参数'}), 400
        
        from services.concept_analysis_service import ConceptAnalysisService
        service = ConceptAnalysisService()
        result = service.get_analysis(ts_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取概念分析失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/api/concept/analysis', methods=['POST'])
def generate_concept_analysis():
    """生成股票概念分析"""
    try:
        data = request.get_json() or {}
        ts_code = data.get('ts_code')
        stock_name = data.get('stock_name')
        concepts = data.get('concepts', [])
        
        if not ts_code or not stock_name or not concepts:
            return jsonify({'error': '缺少必需参数: ts_code, stock_name, concepts'}), 400
        
        from services.concept_analysis_service import ConceptAnalysisService
        service = ConceptAnalysisService()
        
        # 生成分析
        analysis_data = service.generate_analysis(ts_code, stock_name, concepts)
        
        return jsonify({
            'success': True,
            'data': analysis_data,
            'total': len(analysis_data)
        })
        
    except Exception as e:
        logger.error(f"生成概念分析失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/api/config/prompt', methods=['GET'])
def get_prompt_config():
    """获取prompt配置"""
    try:
        from services.concept_analysis_service import ConceptAnalysisService
        service = ConceptAnalysisService()
        config = service.get_prompt_config()
        
        return jsonify(config)
        
    except Exception as e:
        logger.error(f"获取prompt配置失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/api/config/prompt', methods=['PUT'])
def update_prompt_config():
    """更新prompt配置"""
    try:
        data = request.get_json() or {}
        system_prompt = data.get('system_prompt')
        user_prompt_template = data.get('user_prompt_template')
        
        if not system_prompt or not user_prompt_template:
            return jsonify({'error': '缺少必需参数'}), 400
        
        from services.concept_analysis_service import ConceptAnalysisService
        service = ConceptAnalysisService()
        service.update_prompt_config(system_prompt, user_prompt_template)
        
        return jsonify({'success': True, 'message': 'Prompt配置已更新'})
        
    except Exception as e:
        logger.error(f"更新prompt配置失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@concept_bp.route('/api/concept/analysis', methods=['DELETE'])
def delete_concept_analysis():
    """删除股票概念分析数据"""
    try:
        ts_code = request.args.get('ts_code')
        if not ts_code:
            return jsonify({'error': '缺少ts_code参数'}), 400
        
        from services.concept_analysis_service import ConceptAnalysisService
        service = ConceptAnalysisService()
        service.delete_analysis(ts_code)
        
        return jsonify({'success': True, 'message': '数据已删除'})
        
    except Exception as e:
        logger.error(f"删除概念分析失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500
