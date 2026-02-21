import sys
import os
from sqlmodel import SQLModel

# 将 src 目录添加到路径，以便导入
sys.path.append(os.path.join(os.getcwd(), "src"))

from core.database import engine, init_db


def reset_database():
    print("正在连接数据库并重置表结构...")
    # 强制删除所有已存在的表（注意：这会清空所有数据）
    SQLModel.metadata.drop_all(engine)
    print("旧表已删除。")

    # 重新创建所有表
    init_db()
    print("新表结构已根据最新 models.py 创建成功！")


if __name__ == "__main__":
    reset_database()
