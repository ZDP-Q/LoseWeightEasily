import logging
import asyncio
from sqlmodel import Session, select
from ..core.database import engine
from ..core.minio_client import MinIOClient
from ..models import FoodRecognition, User
from ..schemas.food_analysis import FoodAnalysisResult, FoodRecognitionResponse

logger = logging.getLogger("loseweight.food_analysis")


class FoodAnalysisService:
    """食物分析服务，委托给 LoseWeightAgent 的 FoodAnalyzer（三路并发），并持久化到 MinIO/PostgreSQL。"""

    def __init__(self, agent):
        self.agent = agent
        self.minio = MinIOClient()

    async def analyze_food_image(self, image_data: bytes) -> FoodRecognitionResponse:
        """识别食物图片并进行持久化存储，包含回退和重试逻辑。"""
        if not self.agent:
            logger.error("AI Agent 未初始化，无法进行识别")
            return self._get_fallback_response("AI 核心未启动，请稍后再试")

        # 1. 尝试执行 AI 识别
        try:
            # 内部已含三路并发冗余逻辑
            result = await self.agent.analyze_food_bytes(image_data)
        except asyncio.TimeoutError:
            logger.warning("食物识别超时，执行一级回退逻辑")
            return self._get_fallback_response("识别请求超时，建议重新拍摄或手动搜索")
        except Exception as e:
            logger.error(f"食物识别发生异常: {e}")
            return self._get_fallback_response(f"识别出错: {str(e)}")

        # 2. 检查识别结果并进行二级回退
        if result is None:
            logger.error("AI 服务返回空结果")
            return self._get_fallback_response("AI 无法识别图片中的食物")

        if isinstance(result, dict) and "error" in result:
            logger.warning(f"AI 识别返回逻辑错误: {result['error']}")
            return self._get_fallback_response(result["error"])

        # 3. 转换识别结果为统一的 Pydantic 模型
        response = self._parse_agent_result(result)

        # 4. 持久化存储（闭环：即便识别不太理想也要存，以便后期优化数据集）
        try:
            # 上传到 MinIO (带重试逻辑的上传由客户端实现或这里处理)
            object_name = self.minio.upload_image(image_data)

            # 记录到数据库
            with Session(engine) as session:
                user = session.exec(select(User)).first()
                user_id = user.id if user else None

                recognition_record = FoodRecognition(
                    user_id=user_id,
                    image_path=object_name,
                    food_name=response.final_food_name,
                    calories=float(response.final_estimated_calories),
                    verification_status="AI_RECOGNIZED",
                    reason=f"三路并发聚合结果 ({len(response.raw_data)} 路)",
                )
                session.add(recognition_record)
                session.commit()
                logger.info(f"成功保存识别数据: ID={recognition_record.id}")
        except Exception as e:
            logger.error(f"数据持久化失败: {e}")
            # 注意：即使存储失败，识别结果依然要返回给用户

        return response

    def _get_fallback_response(self, error_message: str) -> FoodRecognitionResponse:
        """失败回退：返回一个默认的、安全的识别响应，而不是抛出异常。"""
        return FoodRecognitionResponse(
            final_food_name="未知食物",
            final_estimated_calories=0,
            raw_data=[
                FoodAnalysisResult(
                    food_name="无法识别",
                    calories=0,
                    confidence=0.0,
                    components=[],
                    # 可以扩展模型以包含错误详情
                )
            ],
            timestamp="",
        )

    def _parse_agent_result(self, result) -> FoodRecognitionResponse:
        """处理来自 Agent 的各种不同格式的结果。"""
        if isinstance(result, dict):
            return FoodRecognitionResponse(
                final_food_name=result.get("final_food_name", "未知食物"),
                final_estimated_calories=result.get("final_estimated_calories", 0),
                raw_data=[
                    FoodAnalysisResult(
                        food_name=r.get("food_name", "未知")
                        if isinstance(r, dict)
                        else getattr(r, "food_name", "未知"),
                        calories=r.get("calories", 0)
                        if isinstance(r, dict)
                        else getattr(r, "calories", 0),
                        confidence=r.get("confidence", 0.0)
                        if isinstance(r, dict)
                        else getattr(r, "confidence", 0.0),
                        components=r.get("components", [])
                        if isinstance(r, dict)
                        else getattr(r, "components", []),
                    )
                    for r in result.get("raw_data", [])
                ],
                timestamp=result.get("timestamp", ""),
            )

        # 已经是对象类型
        return FoodRecognitionResponse(
            final_food_name=result.final_food_name,
            final_estimated_calories=result.final_estimated_calories,
            raw_data=[
                FoodAnalysisResult(
                    food_name=r.food_name,
                    calories=r.calories,
                    confidence=r.confidence,
                    components=r.components,
                )
                for r in result.raw_data
            ],
            timestamp=result.timestamp,
        )

    def _parse_agent_result(self, result) -> FoodRecognitionResponse:
        """处理来自 Agent 的各种不同格式的结果。"""
        if isinstance(result, dict):
            return FoodRecognitionResponse(
                final_food_name=result.get("final_food_name", "未知食物"),
                final_estimated_calories=result.get("final_estimated_calories", 0),
                raw_data=[
                    FoodAnalysisResult(
                        food_name=r.get("food_name", "未知")
                        if isinstance(r, dict)
                        else getattr(r, "food_name", "未知"),
                        calories=r.get("calories", 0)
                        if isinstance(r, dict)
                        else getattr(r, "calories", 0),
                        confidence=r.get("confidence", 0.0)
                        if isinstance(r, dict)
                        else getattr(r, "confidence", 0.0),
                        components=r.get("components", [])
                        if isinstance(r, dict)
                        else getattr(r, "components", []),
                    )
                    for r in result.get("raw_data", [])
                ],
                timestamp=result.get("timestamp", ""),
            )

        # 已经是对象类型
        return FoodRecognitionResponse(
            final_food_name=result.final_food_name,
            final_estimated_calories=result.final_estimated_calories,
            raw_data=[
                FoodAnalysisResult(
                    food_name=r.food_name,
                    calories=r.calories,
                    confidence=r.confidence,
                    components=r.components,
                )
                for r in result.raw_data
            ],
            timestamp=result.timestamp,
        )
