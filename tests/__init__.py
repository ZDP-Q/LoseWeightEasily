"""
LossWeightEasily 测试套件

测试类型：
- 单元测试 (@pytest.mark.unit): 测试单个函数或类
- 集成测试 (@pytest.mark.integration): 测试多个组件协作
- 端到端测试 (@pytest.mark.e2e): 测试完整工作流程
- Mock 测试: 使用 Mock 对象隔离依赖

测试文件：
- test_bmr.py: BMR/TDEE 计算测试
- test_config.py: 配置系统测试
- test_container.py: 依赖注入容器测试
- test_database.py: 数据库管理器测试
- test_e2e.py: 端到端工作流程测试
- test_logging.py: 日志系统测试
- test_mock.py: Mock 测试
- test_models.py: Pydantic 模型测试
- test_search.py: 搜索引擎测试 (需要真实数据库)
- test_weight_tracker.py: 体重跟踪器测试

运行测试：
    uv run pytest tests/ -v                    # 运行所有测试
    uv run pytest tests/ -m unit               # 只运行单元测试
    uv run pytest tests/ -m integration        # 只运行集成测试
    uv run pytest tests/ -m e2e                # 只运行端到端测试
    uv run pytest tests/ --cov=src/loss_weight # 带覆盖率报告
"""
