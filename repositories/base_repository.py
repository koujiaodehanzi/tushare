from sqlalchemy.orm import Session
from sqlalchemy.dialects.mysql import insert
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseRepository:
    def __init__(self, model, db: Session):
        self.model = model
        self.db = db
    
    def batch_upsert(self, data_list: List[Dict[str, Any]], unique_fields: List[str]):
        """批量插入或更新数据"""
        if not data_list:
            return 0
        
        try:
            # 获取模型的有效字段和必填字段
            valid_columns = {col.name for col in self.model.__table__.columns if col.name not in ['id', 'created_at', 'updated_at']}
            required_fields = {col.name for col in self.model.__table__.columns if not col.nullable and col.name not in ['id', 'created_at', 'updated_at']}
            
            # 过滤数据，只保留模型中存在的字段，并排除必填字段为None的记录
            filtered_data = []
            for item in data_list:
                filtered_item = {k: v for k, v in item.items() if k in valid_columns}
                # 检查必填字段是否都有值
                if all(filtered_item.get(field) is not None for field in required_fields):
                    filtered_data.append(filtered_item)
            
            if not filtered_data:
                return 0
            
            # 获取数据中实际存在的字段
            actual_fields = set(filtered_data[0].keys())
            
            stmt = insert(self.model).values(filtered_data)
            
            # 构建更新字典，只包含数据中实际存在的字段
            update_dict = {}
            for col_name in actual_fields:
                if col_name not in unique_fields:  # 不更新唯一键字段
                    update_dict[col_name] = stmt.inserted[col_name]
            
            if update_dict:
                stmt = stmt.on_duplicate_key_update(**update_dict)
            
            result = self.db.execute(stmt)
            self.db.commit()
            return result.rowcount
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量upsert失败: {e}")
            raise
    
    def batch_insert(self, data_list: List[Dict[str, Any]]):
        """批量插入数据"""
        if not data_list:
            return 0
        
        try:
            self.db.bulk_insert_mappings(self.model, data_list)
            self.db.commit()
            return len(data_list)
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量插入失败: {e}")
            raise
    
    def get_by_id(self, id: int):
        """根据ID查询"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self):
        """查询所有数据"""
        return self.db.query(self.model).all()
    
    def delete_by_id(self, id: int):
        """根据ID删除"""
        try:
            obj = self.get_by_id(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除失败: {e}")
            raise
