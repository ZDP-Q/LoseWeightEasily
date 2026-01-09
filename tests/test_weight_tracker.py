"""
体重跟踪器模块测试

测试体重记录和统计功能。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import pytest

from loss_weight.models import WeightRecord, WeightRecordCreate, WeightStatistics
from loss_weight.weight_tracker import WeightTracker


@pytest.mark.unit
class TestWeightRecordValidation:
    """体重记录验证测试"""

    def test_valid_weight_record_create(self):
        """测试创建有效的体重记录"""
        record = WeightRecordCreate(weight_kg=70.5, notes="早上空腹")
        assert record.weight_kg == 70.5
        assert record.notes == "早上空腹"

    def test_weight_record_default_notes(self):
        """测试默认备注为空字符串"""
        record = WeightRecordCreate(weight_kg=65.0)
        assert record.notes == ""

    def test_weight_record_with_datetime(self):
        """测试带时间戳的体重记录"""
        now = datetime.now()
        record = WeightRecord(
            id=1,
            weight_kg=72.0,
            recorded_at=now,
            notes="测试记录"
        )
        assert record.id == 1
        assert record.weight_kg == 72.0
        assert record.recorded_at == now


@pytest.mark.unit
class TestWeightTrackerInit:
    """体重跟踪器初始化测试"""

    def test_init_with_db_manager(self, temp_db):
        """测试使用数据库管理器初始化"""
        tracker = WeightTracker(db_manager=temp_db)
        assert tracker._db_manager is temp_db

    def test_init_with_db_path(self, temp_db_path):
        """测试使用数据库路径初始化"""
        tracker = WeightTracker(db_path=str(temp_db_path))
        assert tracker._db_path == str(temp_db_path)

    def test_lazy_db_manager_loading(self, temp_db_path):
        """测试数据库管理器懒加载"""
        tracker = WeightTracker(db_path=str(temp_db_path))
        # _db_manager 初始为 None
        assert tracker._db_manager is None
        # 访问属性触发懒加载
        db = tracker.db_manager
        assert db is not None


@pytest.mark.integration
class TestWeightTrackerRecordWeight:
    """体重记录功能测试"""

    def test_record_weight_basic(self, temp_db_with_weight_table):
        """测试基本体重记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        record_id = tracker.record_weight(70.5)
        
        assert record_id is not None
        assert record_id > 0

    def test_record_weight_with_notes(self, temp_db_with_weight_table):
        """测试带备注的体重记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        record_id = tracker.record_weight(68.0, notes="运动后")
        
        # 验证记录已保存
        record = tracker.get_latest_record()
        assert record is not None
        assert record.weight_kg == 68.0
        assert record.notes == "运动后"

    def test_record_multiple_weights(self, temp_db_with_weight_table):
        """测试多次体重记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        
        id1 = tracker.record_weight(70.0, "第一天")
        id2 = tracker.record_weight(69.5, "第二天")
        id3 = tracker.record_weight(69.0, "第三天")
        
        # ID 应该递增
        assert id1 < id2 < id3
        
        # 最新记录应该是最后一条
        latest = tracker.get_latest_record()
        assert latest.weight_kg == 69.0


@pytest.mark.integration
class TestWeightTrackerGetRecords:
    """获取体重记录测试"""

    def test_get_latest_record_empty(self, temp_db_with_weight_table):
        """测试空数据库获取最新记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        record = tracker.get_latest_record()
        assert record is None

    def test_get_latest_record(self, temp_db_with_weight_table):
        """测试获取最新记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        tracker.record_weight(70.0)
        tracker.record_weight(69.0)
        
        latest = tracker.get_latest_record()
        assert latest is not None
        assert latest.weight_kg == 69.0

    def test_get_records_empty(self, temp_db_with_weight_table):
        """测试空数据库获取历史记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        records = tracker.get_records()
        assert records == []

    def test_get_records_default_limit(self, temp_db_with_weight_table):
        """测试默认限制获取记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        
        # 添加超过默认限制的记录
        for i in range(35):
            tracker.record_weight(70.0 - i * 0.1)
        
        records = tracker.get_records()
        # 默认限制 30 条
        assert len(records) == 30

    def test_get_records_custom_limit(self, temp_db_with_weight_table):
        """测试自定义限制获取记录"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        
        for i in range(10):
            tracker.record_weight(70.0 - i * 0.1)
        
        records = tracker.get_records(limit=5)
        assert len(records) == 5

    def test_get_records_ordering(self, temp_db_with_weight_table):
        """测试记录按时间倒序排列"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        
        tracker.record_weight(70.0, "第一条")
        tracker.record_weight(69.0, "第二条")
        tracker.record_weight(68.0, "第三条")
        
        records = tracker.get_records()
        # 最新的在前面
        assert records[0].notes == "第三条"
        assert records[1].notes == "第二条"
        assert records[2].notes == "第一条"


@pytest.mark.integration
class TestWeightTrackerStatistics:
    """体重统计功能测试"""

    def test_statistics_empty_database(self, temp_db_with_weight_table):
        """测试空数据库统计"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        stats = tracker.get_weight_statistics()
        
        assert isinstance(stats, WeightStatistics)
        assert stats.total_records == 0

    def test_statistics_single_record(self, temp_db_with_weight_table):
        """测试单条记录统计"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        tracker.record_weight(70.0)
        
        stats = tracker.get_weight_statistics()
        assert stats.total_records == 1
        assert stats.latest_weight == 70.0
        assert stats.earliest_weight == 70.0

    def test_statistics_multiple_records(self, temp_db_with_weight_table):
        """测试多条记录统计"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        
        # 添加多条记录
        tracker.record_weight(72.0)
        tracker.record_weight(71.0)
        tracker.record_weight(70.0)
        tracker.record_weight(69.0)
        tracker.record_weight(68.0)
        
        stats = tracker.get_weight_statistics()
        assert stats.total_records == 5
        assert stats.latest_weight == 68.0
        assert stats.earliest_weight == 72.0
        assert stats.weight_change == -4.0  # 68 - 72 = -4

    def test_statistics_average_weight(self, temp_db_with_weight_table):
        """测试平均体重计算"""
        tracker = WeightTracker(db_manager=temp_db_with_weight_table)
        
        # 添加记录: 70, 71, 72 平均 71
        tracker.record_weight(70.0)
        tracker.record_weight(71.0)
        tracker.record_weight(72.0)
        
        stats = tracker.get_weight_statistics()
        assert stats.average_weight is not None
        assert abs(stats.average_weight - 71.0) < 0.01


@pytest.mark.unit
class TestWeightStatisticsModel:
    """体重统计模型测试"""

    def test_empty_statistics(self):
        """测试空统计默认值"""
        stats = WeightStatistics(total_records=0)
        assert stats.total_records == 0
        assert stats.latest_weight is None
        assert stats.earliest_weight is None
        assert stats.weight_change is None
        assert stats.average_weight is None

    def test_statistics_with_all_fields(self):
        """测试完整统计字段"""
        stats = WeightStatistics(
            total_records=10,
            latest_weight=68.0,
            earliest_weight=72.0,
            weight_change=-4.0,
            average_weight=70.0,
            min_weight=67.0,
            max_weight=73.0,
        )
        
        assert stats.total_records == 10
        assert stats.latest_weight == 68.0
        assert stats.earliest_weight == 72.0
        assert stats.weight_change == -4.0
        assert stats.average_weight == 70.0
        assert stats.min_weight == 67.0
        assert stats.max_weight == 73.0
