"""
搜索引擎模块

基于 FAISS 的向量语义搜索引擎，支持中英文跨语言搜索。
"""

import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from .config import config
from .database import DatabaseManager


class FoodSearchEngine:
    """食物语义搜索引擎"""
    
    def __init__(self, db_path: str = None):
        """
        初始化搜索引擎
        
        Args:
            db_path: 数据库路径，默认使用配置中的路径
        """
        self.db_manager = DatabaseManager(db_path)
        self._model: Optional[SentenceTransformer] = None
        self._index: Optional[faiss.Index] = None
        self._food_list: Optional[List[Dict[str, Any]]] = None
    
    @property
    def model(self) -> SentenceTransformer:
        """懒加载嵌入模型"""
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self) -> None:
        """加载嵌入模型"""
        print("🔄 加载多语言嵌入模型（首次运行会下载模型，需要几分钟）...")
        try:
            self._model = SentenceTransformer(config.EMBEDDING_MODEL)
            print("✅ 模型加载完成")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            print("💡 提示：请确保网络连接正常，模型会自动从HuggingFace下载")
            raise
    
    def _load_index(self) -> bool:
        """
        加载已有的 FAISS 索引
        
        Returns:
            是否成功加载
        """
        index_path = Path(config.INDEX_FILE)
        metadata_path = Path(config.METADATA_FILE)
        
        if not (index_path.exists() and metadata_path.exists()):
            return False
        
        print("📂 加载已有的向量索引...")
        self._index = faiss.read_index(str(index_path))
        
        with open(metadata_path, 'rb') as f:
            self._food_list = pickle.load(f)
        
        print(f"✅ 索引加载完成，包含 {len(self._food_list)} 个食物")
        return True
    
    def build_index(self, force_rebuild: bool = False) -> None:
        """
        构建食物名称的 FAISS 向量索引
        
        Args:
            force_rebuild: 是否强制重建索引
        """
        # 尝试加载已有索引
        if not force_rebuild and self._load_index():
            return
        
        print("🔨 构建食物向量索引...")
        
        # 从数据库获取所有食物
        foods = self.db_manager.get_all_foods()
        
        # 准备文本和元数据
        food_texts = []
        self._food_list = []
        
        for fdc_id, description, category in foods:
            # 组合描述和分类作为搜索文本
            text = f"{description} {category or ''}"
            food_texts.append(text)
            self._food_list.append({
                'fdc_id': fdc_id,
                'description': description,
                'category': category
            })
        
        # 生成向量
        print(f"🔄 为 {len(food_texts)} 个食物生成向量...")
        embeddings = self.model.encode(
            food_texts, 
            show_progress_bar=True, 
            convert_to_numpy=True
        )
        
        # 标准化向量（用于余弦相似度）
        faiss.normalize_L2(embeddings)
        
        # 创建 FAISS 索引
        dimension = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)  # 使用内积（余弦相似度）
        self._index.add(embeddings)
        
        # 保存索引和元数据
        faiss.write_index(self._index, config.INDEX_FILE)
        with open(config.METADATA_FILE, 'wb') as f:
            pickle.dump(self._food_list, f)
        
        print(f"✅ 向量索引构建完成并已保存")
    
    def ensure_index(self) -> None:
        """确保索引已加载或构建"""
        if self._index is None or self._food_list is None:
            self.build_index()
    
    def search(
        self, 
        query: str, 
        limit: int = None,
        threshold: float = None
    ) -> List[Tuple[int, str, str, float]]:
        """
        搜索食物（支持中英文语义搜索）
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            threshold: 相似度阈值
            
        Returns:
            匹配的食物列表，每项包含 (fdc_id, description, category, similarity)
        """
        self.ensure_index()
        
        limit = limit or config.DEFAULT_SEARCH_LIMIT
        threshold = threshold or config.SIMILARITY_THRESHOLD
        
        # 将搜索词转换为向量
        query_vector = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)
        
        # 搜索最相似的食物
        k = min(limit * 2, len(self._food_list))  # 多搜索一些以便过滤
        distances, indices = self._index.search(query_vector, k)
        
        # 准备结果
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if distance > threshold:
                food = self._food_list[idx]
                results.append((
                    food['fdc_id'],
                    food['description'],
                    food['category'],
                    float(distance)  # 相似度分数
                ))
        
        return results[:limit]
    
    def search_with_details(
        self, 
        query: str, 
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        搜索食物并返回完整详情
        
        Args:
            query: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            包含完整信息的食物列表
        """
        search_results = self.search(query, limit)
        
        results = []
        for fdc_id, description, category, similarity in search_results:
            food_info = self.db_manager.get_food_complete_info(fdc_id)
            if food_info:
                food_info['similarity'] = similarity
                results.append(food_info)
        
        return results
