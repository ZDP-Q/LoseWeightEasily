"""USDA Foundation Foods 数据导入脚本。

解析 USDA JSON → DashScope 向量化 → 写入 Milvus。
"""

import json
import logging
import sys
import time
from pathlib import Path

# 将 backend 目录添加到 path，以便导入 LoseWeightAgent 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

from LoseWeightAgent.src.services.embedding_service import EmbeddingService
from LoseWeightAgent.src.services.milvus_manager import MilvusManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("import_usda")

# 营养素编号映射
NUTRIENT_MAP = {
    "208": "calories",   # Energy (kcal)
    "203": "protein",    # Protein (g)
    "204": "fat",        # Total lipid (fat) (g)
    "205": "carbs",      # Carbohydrate, by difference (g)
}


def load_config() -> dict:
    """加载 config.yaml。"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_usda_json(json_path: str) -> list[dict]:
    """解析 USDA Foundation Foods JSON 文件。"""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    foods = data.get("FoundationFoods", [])
    parsed = []

    for food in foods:
        fdc_id = food.get("fdcId", 0)
        description = food.get("description", "").strip()

        # 解析食物分类
        category = food.get("foodCategory", {})
        if isinstance(category, dict):
            food_category = category.get("description", "")
        else:
            food_category = str(category)

        # 解析营养素
        nutrients = {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
        for fn in food.get("foodNutrients", []):
            nut = fn.get("nutrient", {})
            number = nut.get("number", "")
            if number in NUTRIENT_MAP:
                key = NUTRIENT_MAP[number]
                amount = fn.get("amount")
                if amount is not None:
                    nutrients[key] = float(amount)

        if not description:
            continue

        parsed.append({
            "fdc_id": fdc_id,
            "description": description,
            "food_category": food_category,
            "calories_per_100g": nutrients["calories"],
            "protein_per_100g": nutrients["protein"],
            "fat_per_100g": nutrients["fat"],
            "carbs_per_100g": nutrients["carbs"],
        })

    return parsed


def main():
    config = load_config()

    # 初始化服务
    api_key = config["llm"]["api_key"]
    milvus_cfg = config.get("milvus", {})
    embedding_cfg = config.get("embedding", {})

    embedding_service = EmbeddingService(
        api_key=api_key,
        model=embedding_cfg.get("model", "qwen3-vl-embedding"),
        dimension=embedding_cfg.get("dimension", 1024),
    )

    milvus_manager = MilvusManager(
        host=milvus_cfg.get("host", "127.0.0.1"),
        port=milvus_cfg.get("port", 19530),
        collection_name=milvus_cfg.get("collection", "usda_foods"),
        vector_dim=embedding_cfg.get("dimension", 1024),
    )

    # 解析 USDA 数据
    data_dir = Path(__file__).parent.parent / "data"
    json_files = list(data_dir.glob("FoodData_Central_*.json"))
    if not json_files:
        logger.error("未找到 USDA JSON 数据文件！")
        return

    json_path = json_files[0]
    logger.info("解析数据文件: %s", json_path)
    foods = parse_usda_json(str(json_path))
    logger.info("共解析 %d 种食物", len(foods))

    # 创建集合
    milvus_manager.create_collection(drop_if_exists=True)

    # 分批向量化并写入
    batch_size = 6
    total_inserted = 0

    for i in range(0, len(foods), batch_size):
        batch = foods[i : i + batch_size]
        texts = [f"{f['description']} ({f['food_category']})" for f in batch]

        try:
            embeddings = embedding_service.embed_texts(texts)
        except Exception as e:
            logger.error("向量化失败 (batch %d): %s", i // batch_size, e)
            time.sleep(2)
            continue

        # 组装 Milvus 插入数据
        insert_data = []
        for food, emb in zip(batch, embeddings):
            insert_data.append({**food, "embedding": emb})

        count = milvus_manager.insert_batch(insert_data)
        total_inserted += count
        logger.info(
            "进度: %d/%d (已插入 %d)", 
            min(i + batch_size, len(foods)), len(foods), total_inserted,
        )

        # 控制 API 调用频率
        time.sleep(0.5)

    # 刷新并验证
    stats = milvus_manager.get_collection_stats()
    logger.info("导入完成！集合统计: %s", stats)
    logger.info("总计导入: %d 种食物", total_inserted)


if __name__ == "__main__":
    main()
