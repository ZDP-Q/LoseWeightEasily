"""
体重打卡模块

记录和管理每日体重数据。
"""

from datetime import datetime

from .database import DatabaseManager


class WeightTracker:
    """体重跟踪器"""

    def __init__(self, db_path: str = None):
        """
        初始化体重跟踪器

        Args:
            db_path: 数据库路径
        """
        self.db_manager = DatabaseManager(db_path)

    def record_weight(self, weight_kg: float, notes: str = "") -> int:
        """
        记录体重

        Args:
            weight_kg: 体重（千克）
            notes: 备注信息（可选）

        Returns:
            记录 ID
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO weight_records (weight_kg, notes)
            VALUES (?, ?)
        """, (weight_kg, notes))

        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return record_id

    def get_latest_record(self) -> dict | None:
        """
        获取最新的体重记录

        Returns:
            最新记录的字典，包含 id, weight_kg, recorded_at, notes
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, weight_kg, recorded_at, notes
            FROM weight_records
            ORDER BY recorded_at DESC
            LIMIT 1
        """)

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'id': result[0],
                'weight_kg': result[1],
                'recorded_at': result[2],
                'notes': result[3]
            }
        return None

    def get_records(self, limit: int = 30) -> list[dict]:
        """
        获取历史体重记录

        Args:
            limit: 返回记录数量限制

        Returns:
            记录列表
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, weight_kg, recorded_at, notes
            FROM weight_records
            ORDER BY recorded_at DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()

        records = []
        for row in results:
            records.append({
                'id': row[0],
                'weight_kg': row[1],
                'recorded_at': row[2],
                'notes': row[3]
            })

        return records

    def get_weight_statistics(self) -> dict:
        """
        获取体重统计信息

        Returns:
            包含统计信息的字典
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        # 获取总记录数
        cursor.execute("SELECT COUNT(*) FROM weight_records")
        total_records = cursor.fetchone()[0]

        if total_records == 0:
            conn.close()
            return {
                'total_records': 0,
                'latest_weight': None,
                'earliest_weight': None,
                'weight_change': None,
                'average_weight': None,
                'min_weight': None,
                'max_weight': None
            }

        # 获取最新和最早记录
        cursor.execute("""
            SELECT weight_kg, recorded_at
            FROM weight_records
            ORDER BY recorded_at DESC
            LIMIT 1
        """)
        latest = cursor.fetchone()

        cursor.execute("""
            SELECT weight_kg, recorded_at
            FROM weight_records
            ORDER BY recorded_at ASC
            LIMIT 1
        """)
        earliest = cursor.fetchone()

        # 获取平均、最小、最大体重
        cursor.execute("""
            SELECT AVG(weight_kg), MIN(weight_kg), MAX(weight_kg)
            FROM weight_records
        """)
        stats = cursor.fetchone()

        conn.close()

        weight_change = latest[0] - earliest[0] if latest and earliest else None

        return {
            'total_records': total_records,
            'latest_weight': latest[0] if latest else None,
            'latest_date': latest[1] if latest else None,
            'earliest_weight': earliest[0] if earliest else None,
            'earliest_date': earliest[1] if earliest else None,
            'weight_change': weight_change,
            'average_weight': stats[0] if stats else None,
            'min_weight': stats[1] if stats else None,
            'max_weight': stats[2] if stats else None
        }


def interactive_weight_checkin() -> None:
    """交互式体重打卡"""
    print("\n" + "=" * 60)
    print("⚖️  每日体重打卡")
    print("=" * 60)

    tracker = WeightTracker()

    # 显示最近一次记录
    latest = tracker.get_latest_record()
    if latest:
        print(f"\n上次记录：{latest['recorded_at']} - {latest['weight_kg']:.1f} kg")
        if latest['notes']:
            print(f"备注：{latest['notes']}")

    # 输入体重
    print("\n请输入今天的体重（千克）:")
    try:
        weight_input = input("> ").strip()
        weight_kg = float(weight_input)

        if weight_kg <= 0 or weight_kg > 300:
            print("❌ 体重数值不合理")
            return

    except ValueError:
        print("❌ 请输入有效的数字")
        return

    # 输入备注（可选）
    print("\n备注（可选，直接回车跳过）:")
    notes = input("> ").strip()

    # 记录体重
    try:
        tracker.record_weight(weight_kg, notes)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("\n✅ 打卡成功！")
        print(f"📅 时间：{now}")
        print(f"⚖️  体重：{weight_kg:.1f} kg")

        # 计算变化
        if latest:
            change = weight_kg - latest['weight_kg']
            change_text = f"{change:+.1f}" if change != 0 else "0.0"
            emoji = "📉" if change < 0 else "📈" if change > 0 else "➡️"
            print(f"{emoji} 变化：{change_text} kg")

        if notes:
            print(f"📝 备注：{notes}")

    except Exception as e:
        print(f"❌ 记录失败: {e}")


def show_weight_history(limit: int = 30) -> None:
    """显示体重历史记录"""
    print("\n" + "=" * 60)
    print("📊 体重历史记录")
    print("=" * 60)

    tracker = WeightTracker()

    # 获取统计信息
    stats = tracker.get_weight_statistics()

    if stats['total_records'] == 0:
        print("\n暂无体重记录")
        return

    print(f"\n📈 统计信息 (共 {stats['total_records']} 条记录)")
    print("-" * 60)
    print(f"当前体重：{stats['latest_weight']:.1f} kg ({stats['latest_date']})")
    print(f"初始体重：{stats['earliest_weight']:.1f} kg ({stats['earliest_date']})")

    if stats['weight_change'] is not None:
        change_text = f"{stats['weight_change']:+.1f}"
        emoji = "🎉" if stats['weight_change'] < 0 else "⚠️" if stats['weight_change'] > 0 else "➡️"
        print(f"{emoji} 总变化：{change_text} kg")

    print(f"平均体重：{stats['average_weight']:.1f} kg")
    print(f"最低体重：{stats['min_weight']:.1f} kg")
    print(f"最高体重：{stats['max_weight']:.1f} kg")

    # 获取历史记录
    records = tracker.get_records(limit)

    if records:
        print(f"\n📝 最近 {len(records)} 条记录:")
        print("-" * 60)

        for i, record in enumerate(records, 1):
            date_str = record['recorded_at']
            weight = record['weight_kg']
            notes = record['notes']

            print(f"{i:2d}. {date_str} - {weight:6.1f} kg", end="")

            # 计算与上一次的变化
            if i < len(records):
                prev_weight = records[i]['weight_kg']
                change = weight - prev_weight
                if abs(change) >= 0.1:
                    change_text = f"{change:+.1f}"
                    emoji = "↓" if change < 0 else "↑"
                    print(f"  {emoji} {change_text}", end="")

            if notes:
                print(f"  ({notes})", end="")

            print()
