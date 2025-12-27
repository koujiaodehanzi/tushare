from services.data_access import DataAccessService
from repositories import *
from repositories.sync_record_repository import SyncRecordRepository
from models import (
    StockList, StockHolder, StockHotMoney, StockHotMoneyDaily, SyncRecord,
    StockDaily, StockChip, StockTechFactor, StockTechFactorPro, StockMoneyFlow,
    BlockThsMoneyFlow, IndustryThsMoneyFlow, StockLhbDaily,
    StockLhbInst, StockLimitStatus, StockLimitLadder, BlockLimitStrong,
    ThsIndustryAndBlock, ThsIndustryAndBlockDetail, ThsIndustryAndBlockDaily,
    DcIndustryAndBlock, DcIndustryAndBlockDetail, DcIndustryAndBlockDaily,
    StockMoneyFlowThs, StockMoneyFlowDc, BlockDcMoneyFlow, IndustryDcMoneyFlow
)
from utils.db import SessionLocal
from utils.logger import get_logger
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import numpy as np

logger = get_logger(__name__)

class DataSyncService:
    def __init__(self):
        self.data_access = DataAccessService()
    
    def sync_stock_list(self):
        """股票列表全量同步"""
        logger.info("开始同步股票列表")
        db = SessionLocal()
        try:
            repo = StockListRepository(db)
            df = self.data_access.get_stock_list()
            
            if df.empty:
                logger.warning("股票列表数据为空")
                return 0
            
            # 处理NaN值
            df = df.replace({np.nan: None})
            
            # 获取模型的有效字段
            valid_fields = {c.name for c in StockList.__table__.columns if c.name not in ['id', 'created_at', 'updated_at']}
            
            count = 0
            for _, row in df.iterrows():
                ts_code = row.get('ts_code')
                # 查询本地是否存在
                existing = db.query(StockList).filter(StockList.ts_code == ts_code).first()
                
                # 只保留有效字段
                row_dict = {k: v for k, v in row.to_dict().items() if k in valid_fields}
                
                if existing:
                    # 更新
                    for key, value in row_dict.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # 插入
                    new_stock = StockList(**row_dict)
                    db.add(new_stock)
                count += 1
            
            db.commit()
            logger.info(f"股票列表同步完成，共{count}条")
            return count
        except Exception as e:
            db.rollback()
            logger.error(f"股票列表同步失败: {e}")
            raise
        finally:
            db.close()
    
    def sync_stock_holder(self, ts_code: str):
        """股东持股增量同步"""
        logger.info(f"开始同步股东持股: {ts_code}")
        db = SessionLocal()
        try:
            repo = StockHolderRepository(db)
            df = self.data_access.get_stock_holder(ts_code=ts_code)
            
            if df.empty:
                logger.warning(f"股东持股数据为空: {ts_code}")
                return 0
            
            # 处理NaN值
            df = df.replace({np.nan: None})
            
            # 获取模型的有效字段
            valid_fields = {c.name for c in StockHolder.__table__.columns if c.name not in ['id', 'created_at', 'updated_at']}
            
            # 删除该股票的旧数据
            db.query(StockHolder).filter(StockHolder.ts_code == ts_code).delete()
            
            # 批量插入新数据
            data_list = df.to_dict('records')
            for data in data_list:
                # 只保留有效字段
                filtered_data = {k: v for k, v in data.items() if k in valid_fields}
                holder = StockHolder(**filtered_data)
                db.add(holder)
            
            db.commit()
            logger.info(f"股东持股同步完成: {ts_code}，共{len(data_list)}条")
            return len(data_list)
        except Exception as e:
            db.rollback()
            logger.error(f"股东持股同步失败: {ts_code}, {e}")
            raise
        finally:
            db.close()
    
    def sync_stock_hot_money(self):
        """股票游资名录全量同步"""
        logger.info("开始同步股票游资名录")
        db = SessionLocal()
        try:
            repo = StockHotMoneyRepository(db)
            df = self.data_access.get_stock_hot_money()
            
            if df.empty:
                logger.warning("游资名录数据为空")
                return 0
            
            # 处理NaN值
            df = df.replace({np.nan: None})
            
            # 获取模型的有效字段
            valid_fields = {c.name for c in StockHotMoney.__table__.columns if c.name not in ['id', 'created_at', 'updated_at']}
            
            # 全量删除
            db.query(StockHotMoney).delete()
            
            # 全量插入
            count = 0
            for _, row in df.iterrows():
                # 只保留有效字段
                row_dict = {k: v for k, v in row.to_dict().items() if k in valid_fields}
                new_hot_money = StockHotMoney(**row_dict)
                db.add(new_hot_money)
                count += 1
            
            db.commit()
            logger.info(f"游资名录同步完成，共{count}条")
            return count
        except Exception as e:
            db.rollback()
            logger.error(f"游资名录同步失败: {e}")
            raise
        finally:
            db.close()
            return count
    
    def sync_base_data(self):
        """基础数据全量同步"""
        logger.info("开始基础数据全量同步")
        
        # 1. 同步股票列表
        self.sync_stock_list()
        
        # 2. 查询所有股票，同步股东持股
        db = SessionLocal()
        try:
            repo = StockListRepository(db)
            stocks = repo.get_all_stocks()
            logger.info(f"共{len(stocks)}只股票需要同步股东持股")
            
            for stock in stocks:
                try:
                    self.sync_stock_holder(stock.ts_code)
                except Exception as e:
                    logger.error(f"同步股东持股失败: {stock.ts_code}, {e}")
                    continue
        finally:
            db.close()
        
        # 3. 同步游资名录
        self.sync_stock_hot_money()
        
        logger.info("基础数据全量同步完成")
    
    def sync_daily_data_by_date(self, trade_date: str, ts_codes: list = None):
        """按当天日期同步每日数据"""
        logger.info(f"开始同步每日数据: {trade_date}, ts_codes={ts_codes}")
        
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            
            # 如果指定了ts_codes，使用不同的sync_type
            sync_type = f'daily_all_{"_".join(ts_codes)}' if ts_codes else 'daily_all'
            
            # 检查是否已同步
            if sync_repo.is_synced(trade_date, sync_type):
                logger.info(f"日期 {trade_date} 已同步，跳过")
                return {'total_count': 0, 'details': {}, 'skipped': True}
            
            stock_repo = StockListRepository(db)
            if ts_codes:
                # 只同步指定股票列表
                stocks = []
                for ts_code in ts_codes:
                    stock = stock_repo.get_by_ts_code(ts_code)
                    if stock:
                        stocks.append(stock)
            else:
                # 同步所有股票
                stocks = stock_repo.get_all_stocks()
            
            logger.info(f"共{len(stocks)}只股票需要同步")
            
            counts = {
                'stock_daily': 0,
                'stock_chip': 0,
                'stock_tech_factor': 0,
                'stock_tech_factor_pro': 0,
                'stock_money_flow': 0,
                'stock_money_flow_ths': 0,
                'stock_money_flow_dc': 0,
                'stock_lhb_daily': 0,
                'stock_lhb_inst': 0,
                'block_ths_money_flow': 0,
                'industry_ths_money_flow': 0,
                'block_dc_money_flow': 0,
                'industry_dc_money_flow': 0,
                'stock_limit_status': 0,
                'stock_limit_ladder': 0,
                'block_limit_strong': 0,
                'stock_hot_money_daily': 0,
                'ths_daily': 0,
                'dc_daily': 0
            }
            
           
            # tech_factor_pro按日期批量同步所有股票
            try:
                counts['stock_daily'] += self._sync_stock_daily(None, trade_date=trade_date)
                counts['stock_money_flow'] += self._sync_stock_money_flow(None, trade_date=trade_date)
                
                # 同步同花顺个股资金流向
                result = self.sync_stock_money_flow_ths(trade_date, trade_date)
                counts['stock_money_flow_ths'] += result.get('count', 0)
                
                counts['stock_tech_factor'] += self._sync_stock_tech_factor(None, trade_date=trade_date)
                counts['stock_tech_factor_pro'] += self._sync_stock_tech_factor_pro(None, trade_date=trade_date)
            except Exception as e:
                logger.error(f"同步每日数据失败: {trade_date}, {e}")
            

            # 同步个股数据
            for stock in stocks:
                stock_ts_code = stock.ts_code
                try:
                    counts['stock_chip'] += self._sync_stock_chip(stock_ts_code, trade_date=trade_date)
                except Exception as e:
                    logger.error(f"同步筹码失败: {stock_ts_code}, {e}")
                    continue
            

            # 只有全量同步时才同步市场数据
            if not ts_codes:
                try:
                    counts['stock_lhb_daily'] += self._sync_stock_lhb_daily(None, trade_date=trade_date)
                    counts['stock_lhb_inst'] += self._sync_stock_lhb_inst(None, trade_date=trade_date)

                    counts['block_ths_money_flow'] += self._sync_block_ths_money_flow(trade_date)
                    counts['industry_ths_money_flow'] += self._sync_industry_ths_money_flow(trade_date)
                    counts['stock_limit_status'] += self._sync_stock_limit_status(trade_date)
                    # counts['stock_limit_ladder'] += self._sync_stock_limit_ladder(trade_date)
                    # counts['block_limit_strong'] += self._sync_block_limit_strong(trade_date)
                    counts['stock_hot_money_daily'] += self._sync_stock_hot_money_daily(trade_date)
                    
                    # 同步同花顺板块行情
                    result = self.sync_ths_daily(trade_date, trade_date)
                    counts['ths_daily'] += result.get('count', 0)
                    
                    # 同步东方财富个股资金流向
                    result = self.sync_stock_money_flow_dc(trade_date, trade_date)
                    counts['stock_money_flow_dc'] += result.get('count', 0)
                    
                    # 同步东方财富板块资金流向
                    result = self.sync_block_dc_money_flow(trade_date, trade_date)
                    counts['block_dc_money_flow'] += result.get('count', 0)
                    
                    # 同步东方财富行业资金流向
                    result = self.sync_industry_dc_money_flow(trade_date, trade_date)
                    counts['industry_dc_money_flow'] += result.get('count', 0)
                    
                    # 同步东方财富板块行情
                    result = self.sync_dc_daily(trade_date, trade_date)
                    counts['dc_daily'] += result.get('count', 0)
                except Exception as e:
                    logger.error(f"同步市场数据失败: {e}")
            
            total_count = sum(counts.values())
            
            # 记录同步成功
            sync_repo.record_sync(trade_date, sync_type, 'success', total_count)
            logger.info(f"每日数据同步完成: {trade_date}，共{total_count}条")
            
            return {'total_count': total_count, 'details': counts, 'skipped': False}
        except Exception as e:
            # 记录同步失败
            sync_type = f'daily_all_{"_".join(ts_codes)}' if ts_codes else 'daily_all'
            sync_repo = SyncRecordRepository(db)
            sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
            logger.error(f"每日数据同步失败: {trade_date}, {e}")
            raise
        finally:
            db.close()
    
    def sync_daily_data_by_range(self, start_date: str, end_date: str, ts_codes: list = None):
        """按日期范围同步每日数据（批量优化）"""
        logger.info(f"开始同步日期范围数据: {start_date} - {end_date}, ts_codes={ts_codes}")
        
        db = SessionLocal()
        try:
            # 获取交易日历，过滤非交易日
            trade_cal_df = self.data_access.get_trade_cal(start_date, end_date)
            if trade_cal_df.empty:
                logger.warning(f"未获取到交易日历数据: {start_date} - {end_date}")
                return {'total_count': 0, 'details': {}, 'synced_dates': 0}
            
            # 筛选交易日（is_open=1）
            trade_dates = trade_cal_df[trade_cal_df['is_open'] == 1]['cal_date'].tolist()
            logger.info(f"日期范围包含 {len(trade_dates)} 个交易日")
            
            if not trade_dates:
                logger.info("日期范围内无交易日")
                return {'total_count': 0, 'details': {}, 'synced_dates': 0}
            
            total_counts = {
                'stock_daily': 0,
                'stock_chip': 0,
                'stock_tech_factor': 0,
                'stock_tech_factor_pro': 0,
                'stock_money_flow': 0,
                'stock_lhb_daily': 0,
                'stock_lhb_inst': 0,
                'block_ths_money_flow': 0,
                'industry_ths_money_flow': 0,
                'stock_limit_status': 0,
                'stock_limit_ladder': 0,
                'block_limit_strong': 0,
                'stock_hot_money_daily': 0
            }
            
            # 批量同步个股数据（按日期范围一次性拉取）
            if ts_codes:
                # 同步指定股票
                for ts_code in ts_codes:
                    try:
                        total_counts['stock_daily'] += self._sync_stock_daily(ts_code, start_date=start_date, end_date=end_date)
                        total_counts['stock_chip'] += self._sync_stock_chip(ts_code, start_date=start_date, end_date=end_date)
                        total_counts['stock_tech_factor'] += self._sync_stock_tech_factor(ts_code, start_date=start_date, end_date=end_date)
                        total_counts['stock_tech_factor_pro'] += self._sync_stock_tech_factor_pro(ts_code, start_date=start_date, end_date=end_date)
                        total_counts['stock_money_flow'] += self._sync_stock_money_flow(ts_code, start_date=start_date, end_date=end_date)
                    except Exception as e:
                        logger.error(f"同步股票 {ts_code} 失败: {e}")
                        continue
                
       
            else:
                # 批量同步所有股票（按交易日）
                for trade_date in trade_dates:
                    try:
                        # 按日期批量拉取所有股票数据
                        total_counts['stock_daily'] += self._sync_stock_daily(None, trade_date=trade_date)
                        total_counts['stock_tech_factor'] += self._sync_stock_tech_factor(None, trade_date=trade_date)
                        total_counts['stock_tech_factor_pro'] += self._sync_stock_tech_factor_pro(None, trade_date=trade_date)
                        total_counts['stock_money_flow'] += self._sync_stock_money_flow(None, trade_date=trade_date)
                    except Exception as e:
                        logger.error(f"批量同步日期 {trade_date} 失败: {e}")
                        continue
                
                # 筹码数据需要遍历所有股票和交易日（每次同步一只股票一个交易日）
                stock_repo = StockListRepository(db)
                stocks = stock_repo.get_all_stocks()
                logger.info(f"开始同步筹码数据，共{len(stocks)}只股票 × {len(trade_dates)}个交易日")
                for stock in stocks:
                    for trade_date in trade_dates:
                        try:
                            total_counts['stock_chip'] += self._sync_stock_chip(stock.ts_code, trade_date=trade_date)
                        except Exception as e:
                            logger.error(f"同步筹码数据失败 {stock.ts_code} {trade_date}: {e}")
                        continue
            
            # 同步市场数据（逐日）
            for trade_date in trade_dates:
                try:
                    total_counts['stock_lhb_daily'] += self._sync_stock_lhb_daily(None, trade_date=trade_date)
                    total_counts['stock_lhb_inst'] += self._sync_stock_lhb_inst(None, trade_date=trade_date)
                    total_counts['block_ths_money_flow'] += self._sync_block_ths_money_flow(trade_date)
                    total_counts['industry_ths_money_flow'] += self._sync_industry_ths_money_flow(trade_date)
                    total_counts['stock_limit_status'] += self._sync_stock_limit_status(trade_date)
                    # total_counts['stock_limit_ladder'] += self._sync_stock_limit_ladder(trade_date)
                    # total_counts['block_limit_strong'] += self._sync_block_limit_strong(trade_date)
                    # total_counts['stock_hot_money_daily'] += self._sync_stock_hot_money_daily(trade_date)
                except Exception as e:
                    logger.error(f"同步市场数据 {trade_date} 失败: {e}")
                    continue
            
            total = sum(total_counts.values())
            logger.info(f"日期范围数据同步完成: {start_date} - {end_date}，共{total}条")
            
            return {'total_count': total, 'details': total_counts, 'synced_dates': len(trade_dates)}
        finally:
            db.close()
    
    def _generate_date_list(self, start_date: str, end_date: str):
        """生成日期列表"""
        start = datetime.strptime(start_date, '%Y%m%d')
        end = datetime.strptime(end_date, '%Y%m%d')
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime('%Y%m%d'))
            current += timedelta(days=1)
        return date_list
    
    def _sync_stock_daily(self, ts_code: str = None, trade_date: str = None, 
                         start_date: str = None, end_date: str = None):
        """同步日线行情"""
        db = SessionLocal()
        try:
            # 检查是否已同步（仅针对单个股票）
            if trade_date and ts_code:
                sync_repo = SyncRecordRepository(db)
                sync_type = f"stock_daily_{ts_code}"
                if sync_repo.is_synced(trade_date, sync_type):
                    logger.info(f"日线数据已同步，跳过: {ts_code}, {trade_date}")
                    return 0
            
            repo = StockDailyRepository(db)
            df = self.data_access.get_stock_daily(ts_code, trade_date, start_date, end_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                
                # 记录同步成功（仅针对单个股票）
                if trade_date and ts_code:
                    sync_repo.record_sync(trade_date, sync_type, 'success', count)
                
                return count
            return 0
        except Exception as e:
            # 记录同步失败（仅针对单个股票）
            if trade_date and ts_code:
                sync_repo = SyncRecordRepository(db)
                sync_type = f"stock_daily_{ts_code}"
                sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
            raise
        finally:
            db.close()
    
    def _sync_stock_chip(self, ts_code: str, trade_date: str = None,
                        start_date: str = None, end_date: str = None):
        """同步每日筹码"""
        db = SessionLocal()
        try:
            # 检查是否已同步（仅针对单个股票）
            if trade_date and ts_code:
                sync_repo = SyncRecordRepository(db)
                sync_type = f"stock_chip_{ts_code}"
                if sync_repo.is_synced(trade_date, sync_type):
                    logger.info(f"筹码数据已同步，跳过: {ts_code}, {trade_date}")
                    return 0
            
            repo = StockChipRepository(db)
            df = self.data_access.get_stock_chip(ts_code, trade_date, start_date, end_date)

            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                
                # 记录同步成功（仅针对单个股票）
                if trade_date and ts_code:
                    sync_repo.record_sync(trade_date, sync_type, 'success', count)
                
                return count
            return 0
        except Exception as e:
            # 记录同步失败（仅针对单个股票）
            if trade_date and ts_code:
                sync_repo = SyncRecordRepository(db)
                sync_type = f"stock_chip_{ts_code}"
                sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
            raise
        finally:
            db.close()
    
    def _sync_stock_tech_factor(self, ts_code: str = None, trade_date: str = None,
                               start_date: str = None, end_date: str = None):
        """同步技术面因子"""
        db = SessionLocal()
        try:
            repo = StockTechFactorRepository(db)
            df = self.data_access.get_stock_tech_factor(ts_code, trade_date, start_date, end_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                return len(data_list)
            return 0
        except Exception as e:
            raise
        finally:
            db.close()
    
    def _sync_stock_tech_factor_pro(self, ts_code: str = None, trade_date: str = None,
                                   start_date: str = None, end_date: str = None):
        """同步技术面因子专业版"""
        db = SessionLocal()
        try:
            repo = StockTechFactorProRepository(db)
            df = self.data_access.get_stock_tech_factor_pro(ts_code, trade_date, start_date, end_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                return len(data_list)
            return 0
        except Exception as e:
            raise
        finally:
            db.close()
    
    def _sync_stock_money_flow(self, ts_code: str = None, trade_date: str = None,
                              start_date: str = None, end_date: str = None):
        """同步个股资金流向（支持日期范围遍历）"""
        db = SessionLocal()
        try:
            # 如果提供了日期范围，按日期遍历同步
            if start_date and end_date and not trade_date:
                from repositories.sync_record_repository import SyncRecordRepository
                sync_repo = SyncRecordRepository(db)
                
                # 获取交易日历
                trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
                if trade_dates.empty:
                    return 0
                
                trade_dates = trade_dates[trade_dates['is_open'] == 1]
                total_count = 0
                
                for _, row in trade_dates.iterrows():
                    date = row['cal_date']
                    sync_type = f'stock_money_flow_{date}'
                    
                    if sync_repo.is_synced(date, sync_type):
                        continue
                    
                    try:
                        df = self.data_access.get_stock_money_flow(ts_code, trade_date=date)
                        if not df.empty:
                            df = df.replace({np.nan: None})
                            data_list = df.to_dict('records')
                            repo = StockMoneyFlowRepository(db)
                            repo.batch_upsert_data(data_list)
                            count = len(data_list)
                            total_count += count
                            sync_repo.record_sync(date, sync_type, 'success', count)
                    except Exception as e:
                        logger.error(f"同步日期{date}失败: {e}")
                        sync_repo.record_sync(date, sync_type, 'failed', 0, str(e))
                        continue
                
                return total_count
            
            # 原有逻辑：单日同步
            if trade_date and ts_code:
                sync_repo = SyncRecordRepository(db)
                sync_type = f"stock_money_flow_{ts_code}"
                if sync_repo.is_synced(trade_date, sync_type):
                    return 0
            
            repo = StockMoneyFlowRepository(db)
            df = self.data_access.get_stock_money_flow(ts_code, trade_date, start_date, end_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                if trade_date and ts_code:
                    sync_repo.record_sync(trade_date, sync_type, 'success', count)
                return count
            return 0
        except Exception as e:
            if trade_date and ts_code:
                sync_repo = SyncRecordRepository(db)
                sync_repo.record_sync(trade_date, f"stock_money_flow_{ts_code}", 'failed', 0, str(e))
            raise
        finally:
            db.close()
    
    def _sync_block_ths_money_flow(self, trade_date: str):
        """同步板块资金流向"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            if sync_repo.is_synced(trade_date, 'block_ths_money_flow'):
                return 0
            
            repo = BlockThsMoneyFlowRepository(db)
            df = self.data_access.get_block_ths_money_flow(trade_date)

            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                logger.info(f"获取板块资金流向数据: 行数: {len(data_list)}")
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, 'block_ths_money_flow', 'success', count)
                return count
            else:
                sync_repo.record_sync(trade_date, 'block_ths_money_flow', 'success', 0)
                return 0
        except Exception as e:
            try:
                sync_repo = SyncRecordRepository(db)
                sync_repo.record_sync(trade_date, 'block_ths_money_flow', 'failed', 0, str(e))
            except:
                pass
            raise
        finally:
            db.close()
    
    def _sync_industry_ths_money_flow(self, trade_date: str):
        """同步行业资金流向"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            if sync_repo.is_synced(trade_date, 'industry_ths_money_flow'):
                return 0
            
            repo = IndustryThsMoneyFlowRepository(db)
            df = self.data_access.get_industry_ths_money_flow(trade_date)
            
            if not df.empty:
                
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, 'industry_ths_money_flow', 'success', count)
                return count
            else:
                sync_repo.record_sync(trade_date, 'industry_ths_money_flow', 'success', 0)
                return 0
        except Exception as e:
            try:
                sync_repo = SyncRecordRepository(db)
                sync_repo.record_sync(trade_date, 'industry_ths_money_flow', 'failed', 0, str(e))
            except:
                pass
            raise
        finally:
            db.close()
    
    def _sync_stock_lhb_daily(self, ts_code: str, trade_date: str):
        """同步龙虎榜每日统计"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            sync_type = f"stock_lhb_daily_{ts_code}"
            if sync_repo.is_synced(trade_date, sync_type):
                return 0
            
            repo = StockLhbDailyRepository(db)
            df = self.data_access.get_stock_lhb_daily(trade_date, ts_code)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, sync_type, 'success', count)
                return count
            return 0
        except Exception as e:
            sync_repo = SyncRecordRepository(db)
            sync_repo.record_sync(trade_date, f"stock_lhb_daily_{ts_code}", 'failed', 0, str(e))
            raise
        finally:
            db.close()
    
    def _sync_stock_lhb_inst(self, ts_code: str, trade_date: str):
        """同步龙虎榜机构交易"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            sync_type = f"stock_lhb_inst_{ts_code}"
            if sync_repo.is_synced(trade_date, sync_type):
                return 0
            
            repo = StockLhbInstRepository(db)
            df = self.data_access.get_stock_lhb_inst(trade_date, ts_code)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, sync_type, 'success', count)
                return count
            return 0
        except Exception as e:
            sync_repo = SyncRecordRepository(db)
            sync_repo.record_sync(trade_date, f"stock_lhb_inst_{ts_code}", 'failed', 0, str(e))
            raise
        finally:
            db.close()
    
    def _sync_stock_limit_status(self, trade_date: str):
        """同步涨跌停和炸板数据"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            if sync_repo.is_synced(trade_date, 'stock_limit_status'):
                return 0
            
            repo = StockLimitStatusRepository(db)
            df = self.data_access.get_stock_limit_status(trade_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, 'stock_limit_status', 'success', count)
                return count
            else:
                sync_repo.record_sync(trade_date, 'stock_limit_status', 'success', 0)
                return 0
        except Exception as e:
            try:
                sync_repo = SyncRecordRepository(db)
                sync_repo.record_sync(trade_date, 'stock_limit_status', 'failed', 0, str(e))
            except:
                pass
            raise
        finally:
            db.close()
    
    def _sync_stock_limit_ladder(self, trade_date: str):
        """同步涨停股票连板天梯"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            if sync_repo.is_synced(trade_date, 'stock_limit_ladder'):
                return 0
            
            repo = StockLimitLadderRepository(db)
            df = self.data_access.get_stock_limit_ladder(trade_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, 'stock_limit_ladder', 'success', count)
                return count
            else:
                sync_repo.record_sync(trade_date, 'stock_limit_ladder', 'success', 0)
                return 0
        except Exception as e:
            try:
                sync_repo = SyncRecordRepository(db)
                sync_repo.record_sync(trade_date, 'stock_limit_ladder', 'failed', 0, str(e))
            except:
                pass
            raise
        finally:
            db.close()
    
    def _sync_block_limit_strong(self, trade_date: str):
        """同步涨停板块最强统计"""
        db = SessionLocal()
        try:
            sync_repo = SyncRecordRepository(db)
            if sync_repo.is_synced(trade_date, 'block_limit_strong'):
                return 0
            
            repo = BlockLimitStrongRepository(db)
            df = self.data_access.get_block_limit_strong(trade_date)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, 'block_limit_strong', 'success', count)
                return count
            else:
                sync_repo.record_sync(trade_date, 'block_limit_strong', 'success', 0)
                return 0
        except Exception as e:
            try:
                sync_repo = SyncRecordRepository(db)
                sync_repo.record_sync(trade_date, 'block_limit_strong', 'failed', 0, str(e))
            except:
                pass
            raise
        finally:
            db.close()
    
    def _sync_stock_hot_money_daily(self, trade_date: str, ts_code: str = None):
        """同步游资每日明细"""
        db = SessionLocal()
        sync_type = f'stock_hot_money_daily_{ts_code}' if ts_code else 'stock_hot_money_daily'
        try:
            sync_repo = SyncRecordRepository(db)
            if sync_repo.is_synced(trade_date, sync_type):
                return 0
            
            repo = StockHotMoneyDailyRepository(db)
            df = self.data_access.get_stock_hot_money_daily(trade_date, ts_code)
            
            if not df.empty:
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                repo.batch_upsert_data(data_list)
                count = len(data_list)
                sync_repo.record_sync(trade_date, sync_type, 'success', count)
                return count
            return 0
        except Exception as e:
            sync_repo = SyncRecordRepository(db)
            sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
            raise
        finally:
            db.close()
    

    def sync_ths_index(self, ts_code: str = None, exchange: str = None, type: str = None):
        """同步同花顺行业和概念板块"""
        logger.info(f"开始同步同花顺板块: ts_code={ts_code}, exchange={exchange}, type={type}")
        db = SessionLocal()
        try:
            from repositories.ths_industry_and_block_repository import ThsIndustryAndBlockRepository
            repo = ThsIndustryAndBlockRepository(db)
            df = self.data_access.get_ths_index(ts_code=ts_code, exchange=exchange, type=type)
            
            if df.empty:
                logger.warning("同花顺板块数据为空")
                return 0
            
            # 过滤count为0或空的数据
            df = df[df['count'].notna() & (df['count'] > 0)]
            
            if df.empty:
                logger.warning("过滤后无有效板块数据")
                return 0
            
            df = df.replace({np.nan: None})
            data_list = df.to_dict('records')
            count = repo.batch_upsert(data_list)
            logger.info(f"同花顺板块同步完成，共{count}条")
            return count
        except Exception as e:
            logger.error(f"同步同花顺板块失败: {e}")
            raise
        finally:
            db.close()
    
    def sync_ths_member(self, ts_code: str = None):
        """同步同花顺板块成分"""
        logger.info(f"开始同步同花顺板块成分: {ts_code or '全部'}")
        db = SessionLocal()
        try:
            from repositories.ths_industry_and_block_detail_repository import ThsIndustryAndBlockDetailRepository
            from repositories.ths_industry_and_block_repository import ThsIndustryAndBlockRepository
            repo = ThsIndustryAndBlockDetailRepository(db)
            
            if ts_code:
                # 同步单个板块
                repo.delete_by_ts_code(ts_code)
                df = self.data_access.get_ths_member(ts_code=ts_code)
                if df.empty:
                    logger.warning(f"板块{ts_code}成分数据为空")
                    return 0
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                count = repo.batch_insert(data_list)
                logger.info(f"板块{ts_code}成分同步完成，共{count}条")
                return count
            else:
                # 同步所有板块成分
                block_repo = ThsIndustryAndBlockRepository(db)
                blocks = db.query(ThsIndustryAndBlock).all()
                total_count = 0
                for block in blocks:
                    try:
                        repo.delete_by_ts_code(block.ts_code)
                        df = self.data_access.get_ths_member(ts_code=block.ts_code)
                        if not df.empty:
                            df = df.replace({np.nan: None})
                            data_list = df.to_dict('records')
                            count = repo.batch_insert(data_list)
                            total_count += count
                            logger.info(f"板块{block.ts_code}成分同步完成，共{count}条")
                    except Exception as e:
                        logger.error(f"同步板块{block.ts_code}成分失败: {e}")
                        continue
                logger.info(f"所有板块成分同步完成，共{total_count}条")
                return total_count
        except Exception as e:
            logger.error(f"同步板块成分失败: {e}")
            raise
        finally:
            db.close()

    def sync_ths_daily(self, start_date: str, end_date: str):
        """同步同花顺板块每日行情"""
        logger.info(f"开始同步同花顺板块行情: {start_date} - {end_date}")
        db = SessionLocal()
        try:
            from repositories.ths_industry_and_block_daily_repository import ThsIndustryAndBlockDailyRepository
            from repositories.sync_record_repository import SyncRecordRepository
            
            repo = ThsIndustryAndBlockDailyRepository(db)
            sync_repo = SyncRecordRepository(db)
            
            # 获取交易日历
            trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
            if trade_dates.empty:
                logger.warning("交易日历为空")
                return {'dates': 0, 'count': 0}
            
            # 过滤交易日
            trade_dates = trade_dates[trade_dates['is_open'] == 1]
            if trade_dates.empty:
                logger.warning("日期范围内无交易日")
                return {'dates': 0, 'count': 0}
            
            # 获取所有板块
            blocks = db.query(ThsIndustryAndBlock).all()
            if not blocks:
                logger.warning("板块列表为空，请先同步板块数据")
                return {'dates': 0, 'count': 0}
            
            total_count = 0
            synced_dates = 0
            
            for _, row in trade_dates.iterrows():
                trade_date = row['cal_date']
                sync_type = f'ths_daily_{trade_date}'
                
                # 检查是否已同步
                if sync_repo.is_synced(trade_date, sync_type):
                    logger.info(f"日期{trade_date}已同步，跳过")
                    continue
                
                try:
                    # 按交易日期同步所有板块
                    df = self.data_access.get_ths_daily(trade_date=trade_date)
                    
                    if not df.empty:
                        df = df.replace({np.nan: None})
                        data_list = df.to_dict('records')
                        count = repo.batch_upsert(data_list)
                        total_count += count
                        sync_repo.record_sync(trade_date, sync_type, 'success', count)
                        logger.info(f"日期{trade_date}同步完成，共{count}条")
                    else:
                        sync_repo.record_sync(trade_date, sync_type, 'success', 0)
                        logger.info(f"日期{trade_date}无数据")
                    
                    synced_dates += 1
                except Exception as e:
                    logger.error(f"同步日期{trade_date}失败: {e}")
                    sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
                    continue
            
            logger.info(f"同花顺板块行情同步完成，共{synced_dates}个交易日，{total_count}条记录")
            return {'dates': synced_dates, 'count': total_count}
        except Exception as e:
            logger.error(f"同步同花顺板块行情失败: {e}")
            raise
        finally:
            db.close()
    
    def sync_stock_money_flow_ths(self, start_date: str, end_date: str):
        """同步同花顺个股资金流向（按日期范围）"""
        logger.info(f"开始同步同花顺个股资金流向: {start_date} - {end_date}")
        db = SessionLocal()
        try:
            from repositories.stock_money_flow_ths_repository import StockMoneyFlowThsRepository
            from repositories.sync_record_repository import SyncRecordRepository
            
            repo = StockMoneyFlowThsRepository(db)
            sync_repo = SyncRecordRepository(db)
            
            # 获取交易日历
            trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
            if trade_dates.empty:
                logger.warning("交易日历为空")
                return {'dates': 0, 'count': 0}
            
            # 过滤交易日
            trade_dates = trade_dates[trade_dates['is_open'] == 1]
            if trade_dates.empty:
                logger.warning("日期范围内无交易日")
                return {'dates': 0, 'count': 0}
            
            total_count = 0
            synced_dates = 0
            
            for _, row in trade_dates.iterrows():
                trade_date = row['cal_date']
                sync_type = f'stock_money_flow_ths_{trade_date}'
                
                # 检查是否已同步
                if sync_repo.is_synced(trade_date, sync_type):
                    logger.info(f"日期{trade_date}已同步，跳过")
                    continue
                
                try:
                    # 按交易日期同步所有股票
                    df = self.data_access.get_moneyflow_ths(trade_date=trade_date)
                    
                    if not df.empty:
                        df = df.replace({np.nan: None})
                        data_list = df.to_dict('records')
                        count = repo.batch_upsert(data_list)
                        total_count += count
                        sync_repo.record_sync(trade_date, sync_type, 'success', count)
                        logger.info(f"日期{trade_date}同步完成，共{count}条")
                    else:
                        sync_repo.record_sync(trade_date, sync_type, 'success', 0)
                        logger.info(f"日期{trade_date}无数据")
                    
                    synced_dates += 1
                except Exception as e:
                    logger.error(f"同步日期{trade_date}失败: {e}")
                    sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
                    continue
            
            logger.info(f"同花顺个股资金流向同步完成，共{synced_dates}个交易日，{total_count}条记录")
            return {'dates': synced_dates, 'count': total_count}
        except Exception as e:
            logger.error(f"同步同花顺个股资金流向失败: {e}")
            raise
        finally:
            db.close()

    def sync_stock_money_flow_dc(self, start_date: str, end_date: str):
        """同步东方财富个股资金流向"""
        logger.info(f"开始同步东方财富个股资金流向: {start_date} - {end_date}")
        db = SessionLocal()
        try:
            from repositories.stock_money_flow_dc_repository import StockMoneyFlowDcRepository
            from repositories.sync_record_repository import SyncRecordRepository
            
            repo = StockMoneyFlowDcRepository(db)
            sync_repo = SyncRecordRepository(db)
            
            trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            trade_dates = trade_dates[trade_dates['is_open'] == 1]
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            total_count = 0
            synced_dates = 0
            
            for _, row in trade_dates.iterrows():
                trade_date = row['cal_date']
                sync_type = f'stock_money_flow_dc_{trade_date}'
                
                if sync_repo.is_synced(trade_date, sync_type):
                    continue
                
                try:
                    df = self.data_access.get_moneyflow_dc(trade_date=trade_date)
                    if not df.empty:
                        df = df.replace({np.nan: None})
                        data_list = df.to_dict('records')
                        count = repo.batch_upsert(data_list)
                        total_count += count
                        sync_repo.record_sync(trade_date, sync_type, 'success', count)
                        logger.info(f"日期{trade_date}同步完成，共{count}条")
                    else:
                        sync_repo.record_sync(trade_date, sync_type, 'success', 0)
                    synced_dates += 1
                except Exception as e:
                    logger.error(f"同步日期{trade_date}失败: {e}")
                    sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
                    continue
            
            logger.info(f"东方财富个股资金流向同步完成，共{synced_dates}个交易日，{total_count}条记录")
            return {'dates': synced_dates, 'count': total_count}
        except Exception as e:
            logger.error(f"同步东方财富个股资金流向失败: {e}")
            raise
        finally:
            db.close()
    
    def sync_block_dc_money_flow(self, start_date: str, end_date: str):
        """同步东方财富板块资金流向"""
        logger.info(f"开始同步东方财富板块资金流向: {start_date} - {end_date}")
        db = SessionLocal()
        try:
            from repositories.block_dc_money_flow_repository import BlockDcMoneyFlowRepository
            from repositories.sync_record_repository import SyncRecordRepository
            
            repo = BlockDcMoneyFlowRepository(db)
            sync_repo = SyncRecordRepository(db)
            
            trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            trade_dates = trade_dates[trade_dates['is_open'] == 1]
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            total_count = 0
            synced_dates = 0
            
            for _, row in trade_dates.iterrows():
                trade_date = row['cal_date']
                sync_type = f'block_dc_money_flow_{trade_date}'
                
                if sync_repo.is_synced(trade_date, sync_type):
                    continue
                
                try:
                    df = self.data_access.get_moneyflow_dc_cnt(trade_date=trade_date)
                    if not df.empty:
                        df = df.replace({np.nan: None})
                        data_list = df.to_dict('records')
                        count = repo.batch_upsert(data_list)
                        total_count += count
                        sync_repo.record_sync(trade_date, sync_type, 'success', count)
                        logger.info(f"日期{trade_date}同步完成，共{count}条")
                    else:
                        sync_repo.record_sync(trade_date, sync_type, 'success', 0)
                    synced_dates += 1
                except Exception as e:
                    logger.error(f"同步日期{trade_date}失败: {e}")
                    sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
                    continue
            
            logger.info(f"东方财富板块资金流向同步完成，共{synced_dates}个交易日，{total_count}条记录")
            return {'dates': synced_dates, 'count': total_count}
        except Exception as e:
            logger.error(f"同步东方财富板块资金流向失败: {e}")
            raise
        finally:
            db.close()
    
    def sync_industry_dc_money_flow(self, start_date: str, end_date: str):
        """同步东方财富行业资金流向"""
        logger.info(f"开始同步东方财富行业资金流向: {start_date} - {end_date}")
        db = SessionLocal()
        try:
            from repositories.industry_dc_money_flow_repository import IndustryDcMoneyFlowRepository
            from repositories.sync_record_repository import SyncRecordRepository
            
            repo = IndustryDcMoneyFlowRepository(db)
            sync_repo = SyncRecordRepository(db)
            
            trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            trade_dates = trade_dates[trade_dates['is_open'] == 1]
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            total_count = 0
            synced_dates = 0
            
            for _, row in trade_dates.iterrows():
                trade_date = row['cal_date']
                sync_type = f'industry_dc_money_flow_{trade_date}'
                
                if sync_repo.is_synced(trade_date, sync_type):
                    continue
                
                try:
                    df = self.data_access.get_moneyflow_dc_industry(trade_date=trade_date)
                    if not df.empty:
                        df = df.replace({np.nan: None})
                        data_list = df.to_dict('records')
                        count = repo.batch_upsert(data_list)
                        total_count += count
                        sync_repo.record_sync(trade_date, sync_type, 'success', count)
                        logger.info(f"日期{trade_date}同步完成，共{count}条")
                    else:
                        sync_repo.record_sync(trade_date, sync_type, 'success', 0)
                    synced_dates += 1
                except Exception as e:
                    logger.error(f"同步日期{trade_date}失败: {e}")
                    sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
                    continue
            
            logger.info(f"东方财富行业资金流向同步完成，共{synced_dates}个交易日，{total_count}条记录")
            return {'dates': synced_dates, 'count': total_count}
        except Exception as e:
            logger.error(f"同步东方财富行业资金流向失败: {e}")
            raise
        finally:
            db.close()

    def sync_dc_index(self, ts_code: str = None, name: str = None, trade_date: str = None):
        """同步东方财富概念板块"""
        logger.info(f"开始同步东方财富板块: ts_code={ts_code}, name={name}, trade_date={trade_date}")
        db = SessionLocal()
        try:
            from repositories.dc_industry_and_block_repository import DcIndustryAndBlockRepository
            repo = DcIndustryAndBlockRepository(db)
            df = self.data_access.get_dc_index(ts_code=ts_code, name=name, trade_date=trade_date)
            
            if df.empty:
                logger.warning("东方财富板块数据为空")
                return 0
            
            df = df.replace({np.nan: None})
            data_list = df.to_dict('records')
            count = repo.batch_upsert(data_list)
            logger.info(f"东方财富板块同步完成，共{count}条")
            return count
        except Exception as e:
            logger.error(f"同步东方财富板块失败: {e}")
            raise
        finally:
            db.close()
    
    def sync_dc_member(self, ts_code: str = None, trade_date: str = None):
        """同步东方财富板块成分"""
        logger.info(f"开始同步东方财富板块成分: ts_code={ts_code}, trade_date={trade_date}")
        db = SessionLocal()
        try:
            from repositories.dc_industry_and_block_detail_repository import DcIndustryAndBlockDetailRepository
            from repositories.dc_industry_and_block_repository import DcIndustryAndBlockRepository
            repo = DcIndustryAndBlockDetailRepository(db)
            
            if ts_code:
                repo.delete_by_ts_code(ts_code)
                df = self.data_access.get_dc_member(ts_code=ts_code, trade_date=trade_date)
                if df.empty:
                    logger.warning(f"板块{ts_code}成分数据为空")
                    return 0
                df = df.replace({np.nan: None})
                data_list = df.to_dict('records')
                count = repo.batch_insert(data_list)
                logger.info(f"板块{ts_code}成分同步完成，共{count}条")
                return count
            else:
                blocks = db.query(DcIndustryAndBlock).filter(
                    DcIndustryAndBlock.trade_date == trade_date
                ).all() if trade_date else db.query(DcIndustryAndBlock).all()
                total_count = 0
                for block in blocks:
                    try:
                        repo.delete_by_ts_code(block.ts_code)
                        df = self.data_access.get_dc_member(ts_code=block.ts_code, trade_date=trade_date)
                        if not df.empty:
                            df = df.replace({np.nan: None})
                            data_list = df.to_dict('records')
                            count = repo.batch_insert(data_list)
                            total_count += count
                            logger.info(f"板块{block.ts_code}成分同步完成，共{count}条")
                    except Exception as e:
                        logger.error(f"同步板块{block.ts_code}成分失败: {e}")
                        continue
                logger.info(f"所有板块成分同步完成，共{total_count}条")
                return total_count
        except Exception as e:
            logger.error(f"同步板块成分失败: {e}")
            raise
        finally:
            db.close()

    def sync_dc_daily(self, start_date: str, end_date: str, idx_type: str = None):
        """同步东方财富板块每日行情"""
        logger.info(f"开始同步东方财富板块行情: {start_date} - {end_date}, type={idx_type}")
        db = SessionLocal()
        try:
            from repositories.dc_industry_and_block_daily_repository import DcIndustryAndBlockDailyRepository
            from repositories.sync_record_repository import SyncRecordRepository
            
            repo = DcIndustryAndBlockDailyRepository(db)
            sync_repo = SyncRecordRepository(db)
            
            trade_dates = self.data_access.get_trade_cal(start_date=start_date, end_date=end_date)
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            trade_dates = trade_dates[trade_dates['is_open'] == 1]
            if trade_dates.empty:
                return {'dates': 0, 'count': 0}
            
            total_count = 0
            synced_dates = 0
            
            for _, row in trade_dates.iterrows():
                trade_date = row['cal_date']
                sync_type = f'dc_daily_{trade_date}'
                
                if sync_repo.is_synced(trade_date, sync_type):
                    continue
                
                try:
                    df = self.data_access.get_dc_daily(trade_date=trade_date, idx_type=idx_type)
                    if not df.empty:
                        df = df.replace({np.nan: None})
                        data_list = df.to_dict('records')
                        count = repo.batch_upsert(data_list)
                        total_count += count
                        sync_repo.record_sync(trade_date, sync_type, 'success', count)
                        logger.info(f"日期{trade_date}同步完成，共{count}条")
                    else:
                        sync_repo.record_sync(trade_date, sync_type, 'success', 0)
                    synced_dates += 1
                except Exception as e:
                    logger.error(f"同步日期{trade_date}失败: {e}")
                    sync_repo.record_sync(trade_date, sync_type, 'failed', 0, str(e))
                    continue
            
            logger.info(f"东方财富板块行情同步完成，共{synced_dates}个交易日，{total_count}条记录")
            return {'dates': synced_dates, 'count': total_count}
        except Exception as e:
            logger.error(f"同步东方财富板块行情失败: {e}")
            raise
        finally:
            db.close()
