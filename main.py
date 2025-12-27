#!/usr/bin/env python3
"""
Tushare股票数据采集系统
主入口文件
"""

import sys
from api.app import app

def main():
    """启动API服务"""
    print("=" * 50)
    print("Tushare股票数据采集系统")
    print("=" * 50)
    print("API服务启动中...")
    print("访问地址: http://localhost:5001")
    print("健康检查: http://localhost:5001/health")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=False)

if __name__ == '__main__':
    main()
