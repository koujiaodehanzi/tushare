from utils.db import engine, Base
from models import *
from utils.logger import get_logger

logger = get_logger(__name__)

def init_database():
    """初始化数据库，创建所有表"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库表创建失败: {e}")
        raise

if __name__ == '__main__':
    init_database()
