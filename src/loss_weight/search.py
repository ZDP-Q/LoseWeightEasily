"""
搜索引擎模块

基于 FAISS 的向量语义搜索引擎，支持中英文跨语言搜索。
使用懒加载模式提升启动速度。
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .models import FoodCompleteInfo, FoodSearchResult, SearchQuery

if TYPE_CHECKING:
    import faiss
    from sentence_transformers import SentenceTransformer

    from .config import Settings
    from .database import DatabaseManager


class FoodSearchEngine:
    """食物语义搜索引擎"""

    def __init__(
        self,
        db_manager: DatabaseManager | None = None,
        db_path: str | None = None,
        settings: Settings | None = None,
    ):
        """
        初始化搜索引擎

        Args:
            db_manager: 数据库管理器实例
            db_path: 数据库路径（兼容旧代码）
            settings: 配置实例
        """
        self._db_manager = db_manager
        self._db_path = db_path
        self._settings = settings
        self._model: SentenceTransformer | None = None
        self._index: faiss.Index | None = None
        self._food_list: list[dict[str, Any]] | None = None
        self._logger = None

    @property
    def logger(self):
        """懒加载日志记录器"""
        if self._logger is None:
            from .container import get_logger

            self._logger = get_logger(__name__)
        return self._logger

    @property
    def settings(self) -> Settings:
        """懒加载配置"""
        if self._settings is None:
            from .config import get_settings

            self._settings = get_settings()
        return self._settings

    @property
    def db_manager(self) -> DatabaseManager:
        """懒加载数据库管理器"""
        if self._db_manager is None:
            from .database import DatabaseManager

            self._db_manager = DatabaseManager(db_path=self._db_path, settings=self.settings)
        return self._db_manager

    @property
    def model(self) -> SentenceTransformer:
        """懒加载嵌入模型"""
        if self._model is None:
            self._load_model()
        return self._model

    def _load_model(self) -> None:
        """加载嵌入模型"""
        # 懒加载 sentence_transformers
        from sentence_transformers import SentenceTransformer

        self.logger.info("加载多语言嵌入模型（首次运行会下载模型，需要几分钟）...")
        try:
            self._model = SentenceTransformer(self.settings.EMBEDDING_MODEL)
            self.logger.info(f"模型加载完成: {self.settings.EMBEDDING_MODEL}")
        except Exception as e:
            self.logger.error(f"模型加载失败: {e}")
            self.logger.info("提示：请确保网络连接正常，模型会自动从 HuggingFace 下载")
            raise

    def _load_index(self) -> bool:
        """
        加载已有的 FAISS 索引

        Returns:
            是否成功加载
        """
        # 懒加载 faiss
        import faiss

        index_path = Path(self.settings.INDEX_FILE)
        metadata_path = Path(self.settings.METADATA_FILE)

        if not (index_path.exists() and metadata_path.exists()):
            self.logger.debug(f"索引文件不存在: {index_path}")
            return False

        self.logger.info(f"加载已有的向量索引: {index_path}")
        self._index = faiss.read_index(str(index_path))

        with open(metadata_path, "rb") as f:
            self._food_list = pickle.load(f)

        self.logger.info(f"索引加载完成，包含 {len(self._food_list)} 个食物")
        return True

    def build_index(self, force_rebuild: bool = False) -> None:
        """
        构建食物名称的 FAISS 向量索引

        Args:
            force_rebuild: 是否强制重建索引
        """
        # 懒加载 faiss
        import faiss

        # 尝试加载已有索引
        if not force_rebuild and self._load_index():
            return

        self.logger.info("构建食物向量索引...")

        # 从数据库获取所有食物
        foods = self.db_manager.get_all_foods()

        # 准备文本和元数据
        food_texts = []
        self._food_list = []

        for fdc_id, description, category in foods:
            # 组合描述和分类作为搜索文本
            text = f"{description} {category or ''}"
            food_texts.append(text)
            self._food_list.append(
                {"fdc_id": fdc_id, "description": description, "category": category}
            )

        # 懒加载 faiss（在方法开头已导入）
        # 生成向量
        self.logger.info(f"为 {len(food_texts)} 个食物生成向量...")
        embeddings = self.model.encode(food_texts, show_progress_bar=True, convert_to_numpy=True)

        # 标准化向量（用于余弦相似度）
        faiss.normalize_L2(embeddings)

        # 创建 FAISS 索引
        dimension = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)  # 使用内积（余弦相似度）
        self._index.add(embeddings)

        # 保存索引和元数据
        faiss.write_index(self._index, self.settings.INDEX_FILE)
        with open(self.settings.METADATA_FILE, "wb") as f:
            pickle.dump(self._food_list, f)

        self.logger.info("向量索引构建完成并已保存")

    def ensure_index(self) -> None:
        """确保索引已加载或构建"""
        if self._index is None or self._food_list is None:
            self.build_index()

    def search(
        self, query: str | SearchQuery, limit: int | None = None, threshold: float | None = None
    ) -> list[FoodSearchResult]:
        """
        搜索食物（支持中英文语义搜索）

        Args:
            query: 搜索关键词或 SearchQuery 对象
            limit: 返回结果数量限制
            threshold: 相似度阈值

        Returns:
            匹配的食物列表 (FoodSearchResult 对象)
        """
        # 懒加载 faiss
        import faiss

        self.ensure_index()

        # 处理 SearchQuery 对象
        if isinstance(query, SearchQuery):
            search_text = query.query
            limit = query.limit
            threshold = query.threshold
        else:
            search_text = query

        limit = limit or self.settings.DEFAULT_SEARCH_LIMIT
        threshold = threshold or self.settings.SIMILARITY_THRESHOLD

        self.logger.debug(f"搜索: query={search_text!r}, limit={limit}, threshold={threshold}")

        # 将搜索词转换为向量
        query_vector = self.model.encode([search_text], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        # 搜索最相似的食物
        k = min(limit * 2, len(self._food_list))  # 多搜索一些以便过滤
        distances, indices = self._index.search(query_vector, k)

        # 准备结果
        results = []
        for idx, distance in zip(indices[0], distances[0], strict=False):
            if distance > threshold:
                food = self._food_list[idx]
                results.append(
                    FoodSearchResult(
                        fdc_id=food["fdc_id"],
                        description=food["description"],
                        category=food["category"],
                        similarity=float(distance),
                    )
                )

        self.logger.debug(f"搜索完成: 找到 {len(results[:limit])} 个结果")
        return results[:limit]

    def search_with_details(
        self, query: str | SearchQuery, limit: int | None = None
    ) -> list[FoodCompleteInfo]:
        """
        搜索食物并返回完整详情

        Args:
            query: 搜索关键词或 SearchQuery 对象
            limit: 返回结果数量限制

        Returns:
            包含完整信息的食物列表 (FoodCompleteInfo 对象)
        """
        search_results = self.search(query, limit)

        results = []
        for result in search_results:
            food_info = self.db_manager.get_food_complete_info(result.fdc_id)
            if food_info:
                food_info.similarity = result.similarity
                results.append(food_info)

        self.logger.debug(f"详细搜索完成: 找到 {len(results)} 个完整结果")
        return results
