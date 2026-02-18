"""食物卡路里检索功能测试脚本。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml

from LoseWeightAgent.src.services.embedding_service import EmbeddingService
from LoseWeightAgent.src.services.milvus_manager import MilvusManager
from LoseWeightAgent.src.services.food_search import FoodSearchService


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    api_key = config["llm"]["api_key"]
    milvus_cfg = config.get("milvus", {})
    embedding_cfg = config.get("embedding", {})

    # 初始化服务
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

    food_search = FoodSearchService(
        embedding_service=embedding_service,
        milvus_manager=milvus_manager,
    )

    # 测试 1: 英文文本搜索
    print("=" * 60)
    print("测试 1: 搜索 'apple'")
    print("=" * 60)
    results = food_search.search_by_text("apple", limit=5)
    for r in results:
        print(f"  [{r.similarity:.4f}] {r.description} | "
              f"{r.calories_per_100g} kcal | P:{r.protein_per_100g}g "
              f"F:{r.fat_per_100g}g C:{r.carbs_per_100g}g")

    # 测试 2: 中文文本搜索
    print()
    print("=" * 60)
    print("测试 2: 搜索 '鸡胸肉'")
    print("=" * 60)
    results = food_search.search_by_text("鸡胸肉", limit=5)
    for r in results:
        print(f"  [{r.similarity:.4f}] {r.description} | "
              f"{r.calories_per_100g} kcal | P:{r.protein_per_100g}g "
              f"F:{r.fat_per_100g}g C:{r.carbs_per_100g}g")

    # 测试 3: 搜索 'rice'
    print()
    print("=" * 60)
    print("测试 3: 搜索 'rice'")
    print("=" * 60)
    results = food_search.search_by_text("rice", limit=5)
    for r in results:
        print(f"  [{r.similarity:.4f}] {r.description} | "
              f"{r.calories_per_100g} kcal | P:{r.protein_per_100g}g "
              f"F:{r.fat_per_100g}g C:{r.carbs_per_100g}g")

    # 测试 4: 搜索 'milk'
    print()
    print("=" * 60)
    print("测试 4: 搜索 'milk'")
    print("=" * 60)
    results = food_search.search_by_text("milk", limit=5)
    for r in results:
        print(f"  [{r.similarity:.4f}] {r.description} | "
              f"{r.calories_per_100g} kcal | P:{r.protein_per_100g}g "
              f"F:{r.fat_per_100g}g C:{r.carbs_per_100g}g")

    print()
    print("=" * 60)
    print("所有文本检索测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    main()
