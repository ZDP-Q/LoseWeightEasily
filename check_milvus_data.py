import sys
from pathlib import Path
import yaml

# 添加路径以便导入 LoseWeightAgent
sys.path.insert(0, str(Path.cwd() / "backend"))

from LoseWeightAgent.src.services.milvus_manager import MilvusManager

def check_milvus():
    with open("backend/config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    milvus_cfg = config.get("milvus", {})
    embedding_cfg = config.get("embedding", {})

    milvus = MilvusManager(
        host=milvus_cfg.get("host", "127.0.0.1"),
        port=milvus_cfg.get("port", 19530),
        collection_name=milvus_cfg.get("collection", "usda_foods"),
        vector_dim=embedding_cfg.get("dimension", 1024),
    )

    try:
        # 获取集合信息
        if milvus.client.has_collection(milvus.collection_name):
            stats = milvus.get_collection_stats()
            print(f"STATUS: SUCCESS")
            print(f"COLLECTION: {milvus.collection_name}")
            print(f"COUNT: {stats.get('row_count', 0)}")
        else:
            print(f"STATUS: NOT_FOUND")
            print(f"COLLECTION: {milvus.collection_name}")
    except Exception as e:
        print(f"STATUS: ERROR")
        print(f"MESSAGE: {str(e)}")

if __name__ == "__main__":
    check_milvus()
