import time
from threading import Lock
from collections import defaultdict

class RateLimiter:
    """滑动时间窗口限流器，支持按接口名称独立限流"""
    
    def __init__(self, max_calls, period=60):
        """
        初始化限流器
        :param max_calls: 时间窗口内最大调用次数
        :param period: 时间窗口大小（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self.interface_calls = defaultdict(list)  # 每个接口独立的调用记录
        self.lock = Lock()
    
    def acquire(self, interface_name: str):
        """
        获取调用许可（滑动时间窗口算法）
        :param interface_name: 接口名称
        """
        with self.lock:
            now = time.time()
            
            # 清理时间窗口外的记录
            self.interface_calls[interface_name] = [
                call_time for call_time in self.interface_calls[interface_name]
                if call_time > now - self.period
            ]
            
            # 检查是否超过限流阈值
            if len(self.interface_calls[interface_name]) >= self.max_calls:
                # 计算需要等待的时间（等到最早的调用超出时间窗口）
                oldest_call = self.interface_calls[interface_name][0]
                sleep_time = self.period - (now - oldest_call) + 0.1  # 加0.1秒缓冲
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = time.time()
                    # 重新清理
                    self.interface_calls[interface_name] = [
                        call_time for call_time in self.interface_calls[interface_name]
                        if call_time > now - self.period
                    ]
            
            # 记录本次调用
            self.interface_calls[interface_name].append(now)
    
    def get_stats(self, interface_name: str = None):
        """
        获取限流统计信息
        :param interface_name: 接口名称，None表示获取所有接口
        :return: 统计信息字典
        """
        with self.lock:
            now = time.time()
            if interface_name:
                calls = [c for c in self.interface_calls[interface_name] if c > now - self.period]
                return {
                    'interface': interface_name,
                    'calls_in_window': len(calls),
                    'max_calls': self.max_calls,
                    'period': self.period
                }
            else:
                stats = {}
                for iface, calls in self.interface_calls.items():
                    valid_calls = [c for c in calls if c > now - self.period]
                    stats[iface] = {
                        'calls_in_window': len(valid_calls),
                        'max_calls': self.max_calls,
                        'period': self.period
                    }
                return stats

