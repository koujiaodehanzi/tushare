#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试get_cyq_perf接口的性能
"""

import time
from services.data_access import DataAccessService
from utils.logger import get_logger

logger = get_logger(__name__)


class CyqPerfPerformanceTest:
    """筹码接口性能测试类"""
    
    def __init__(self):
        self.data_access = DataAccessService()
    
    def test_single_request(self, ts_code: str, trade_date: str = None):
        """测试单次请求耗时"""
        start_time = time.time()
        
        try:
            result = self.data_access.get_stock_chip(ts_code, trade_date=trade_date)
            end_time = time.time()
            elapsed = end_time - start_time
            
            record_count = len(result) if result is not None and hasattr(result, '__len__') else 0
            
            logger.info(f"单次请求完成 - ts_code: {ts_code}, trade_date: {trade_date}")
            logger.info(f"耗时: {elapsed:.3f}秒, 返回记录数: {record_count}")
            
            return {
                'ts_code': ts_code,
                'trade_date': trade_date,
                'elapsed_time': elapsed,
                'record_count': record_count,
                'success': True
            }
        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            logger.error(f"请求失败 - ts_code: {ts_code}, 错误: {e}")
            
            return {
                'ts_code': ts_code,
                'trade_date': trade_date,
                'elapsed_time': elapsed,
                'record_count': 0,
                'success': False,
                'error': str(e)
            }
    
    def test_multiple_requests(self, ts_codes: list, trade_date: str = None, count: int = 1):
        """测试多次请求的平均耗时"""
        results = []
        
        logger.info(f"开始测试 - 股票数: {len(ts_codes)}, 每只股票请求次数: {count}")
        
        for ts_code in ts_codes:
            for i in range(count):
                logger.info(f"测试 {ts_code} 第 {i+1}/{count} 次")
                result = self.test_single_request(ts_code, trade_date)
                results.append(result)
                
                # 避免频繁请求，间隔0.5秒
                if i < count - 1 or ts_code != ts_codes[-1]:
                    time.sleep(0.5)
        
        # 统计结果
        success_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if success_results:
            total_time = sum(r['elapsed_time'] for r in success_results)
            avg_time = total_time / len(success_results)
            min_time = min(r['elapsed_time'] for r in success_results)
            max_time = max(r['elapsed_time'] for r in success_results)
            
            logger.info("=" * 60)
            logger.info(f"测试完成 - 总请求数: {len(results)}")
            logger.info(f"成功: {len(success_results)}, 失败: {len(failed_results)}")
            logger.info(f"平均耗时: {avg_time:.3f}秒")
            logger.info(f"最短耗时: {min_time:.3f}秒")
            logger.info(f"最长耗时: {max_time:.3f}秒")
            logger.info(f"总耗时: {total_time:.3f}秒")
            logger.info("=" * 60)
        
        return {
            'total_requests': len(results),
            'success_count': len(success_results),
            'failed_count': len(failed_results),
            'avg_time': avg_time if success_results else 0,
            'min_time': min_time if success_results else 0,
            'max_time': max_time if success_results else 0,
            'total_time': total_time if success_results else 0,
            'details': results
        }


if __name__ == '__main__':
    # 创建测试实例
    test = CyqPerfPerformanceTest()
    
    # 测试单只股票
    print("\n【测试1：单只股票单次请求】")
    test.test_single_request('000001.SZ', '20231213')
    
    # 测试单只股票多次请求
    print("\n【测试2：单只股票多次请求】")
    test.test_multiple_requests(['000001.SZ'], '20231213', count=3)
    
    # 测试多只股票
    print("\n【测试3：多只股票单次请求】")
    test.test_multiple_requests(['000001.SZ', '000002.SZ', '600000.SH'], '20231213', count=1)
