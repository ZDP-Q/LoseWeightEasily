import json
import sqlite3
from pathlib import Path
from difflib import SequenceMatcher


def create_database(db_path="food_data.db"):
    """创建SQLite数据库和表结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建食品主表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            fdc_id INTEGER PRIMARY KEY,
            food_class TEXT,
            description TEXT,
            data_type TEXT,
            ndb_number INTEGER,
            publication_date TEXT,
            food_category TEXT,
            scientific_name TEXT
        )
    """)
    
    # 创建营养素表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nutrients (
            id INTEGER PRIMARY KEY,
            nutrient_id INTEGER,
            nutrient_number TEXT,
            nutrient_name TEXT,
            unit_name TEXT,
            rank INTEGER,
            UNIQUE(nutrient_id)
        )
    """)
    
    # 创建食品营养素关联表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_nutrients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fdc_id INTEGER,
            nutrient_id INTEGER,
            amount REAL,
            data_points INTEGER,
            derivation_code TEXT,
            min_value REAL,
            max_value REAL,
            median_value REAL,
            FOREIGN KEY (fdc_id) REFERENCES foods (fdc_id),
            FOREIGN KEY (nutrient_id) REFERENCES nutrients (nutrient_id)
        )
    """)
    
    # 创建食品份量表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_portions (
            id INTEGER PRIMARY KEY,
            fdc_id INTEGER,
            amount REAL,
            measure_unit_name TEXT,
            measure_unit_abbreviation TEXT,
            gram_weight REAL,
            modifier TEXT,
            sequence_number INTEGER,
            FOREIGN KEY (fdc_id) REFERENCES foods (fdc_id)
        )
    """)
    
    conn.commit()
    return conn


def insert_food(cursor, food_data):
    """插入食品数据"""
    food_category = food_data.get("foodCategory", {})
    
    cursor.execute("""
        INSERT OR REPLACE INTO foods 
        (fdc_id, food_class, description, data_type, ndb_number, 
         publication_date, food_category, scientific_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        food_data.get("fdcId"),
        food_data.get("foodClass"),
        food_data.get("description"),
        food_data.get("dataType"),
        food_data.get("ndbNumber"),
        food_data.get("publicationDate"),
        food_category.get("description") if food_category else None,
        food_data.get("scientificName")
    ))


def insert_nutrient(cursor, nutrient_data):
    """插入营养素数据"""
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO nutrients 
            (nutrient_id, nutrient_number, nutrient_name, unit_name, rank)
            VALUES (?, ?, ?, ?, ?)
        """, (
            nutrient_data.get("id"),
            nutrient_data.get("number"),
            nutrient_data.get("name"),
            nutrient_data.get("unitName"),
            nutrient_data.get("rank")
        ))
    except sqlite3.IntegrityError:
        pass  # 营养素已存在


def insert_food_nutrient(cursor, fdc_id, food_nutrient):
    """插入食品营养素关联数据"""
    nutrient = food_nutrient.get("nutrient", {})
    
    # 先插入营养素
    insert_nutrient(cursor, nutrient)
    
    # 插入食品营养素关系
    cursor.execute("""
        INSERT INTO food_nutrients 
        (fdc_id, nutrient_id, amount, data_points, derivation_code, 
         min_value, max_value, median_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        fdc_id,
        nutrient.get("id"),
        food_nutrient.get("amount"),
        food_nutrient.get("dataPoints"),
        food_nutrient.get("foodNutrientDerivation", {}).get("code"),
        food_nutrient.get("min"),
        food_nutrient.get("max"),
        food_nutrient.get("median")
    ))


def insert_food_portions(cursor, fdc_id, portions):
    """插入食品份量数据"""
    for portion in portions:
        measure_unit = portion.get("measureUnit", {})
        cursor.execute("""
            INSERT OR REPLACE INTO food_portions 
            (id, fdc_id, amount, measure_unit_name, measure_unit_abbreviation,
             gram_weight, modifier, sequence_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            portion.get("id"),
            fdc_id,
            portion.get("amount"),
            measure_unit.get("name"),
            measure_unit.get("abbreviation"),
            portion.get("gramWeight"),
            portion.get("modifier"),
            portion.get("sequenceNumber")
        ))


def parse_json_to_sqlite(json_file_path, db_path="food_data.db"):
    """解析JSON文件并存入SQLite数据库"""
    print(f"正在读取JSON文件: {json_file_path}")
    
    # 读取JSON文件
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建数据库连接
    conn = create_database(db_path)
    cursor = conn.cursor()
    
    # 获取食品列表
    foundation_foods = data.get("FoundationFoods", [])
    total_foods = len(foundation_foods)
    
    print(f"找到 {total_foods} 个食品条目")
    
    # 处理每个食品
    for idx, food in enumerate(foundation_foods, 1):
        if idx % 100 == 0:
            print(f"处理进度: {idx}/{total_foods}")
        
        fdc_id = food.get("fdcId")
        
        # 插入食品基本信息
        insert_food(cursor, food)
        
        # 插入营养素信息
        food_nutrients = food.get("foodNutrients", [])
        for nutrient in food_nutrients:
            insert_food_nutrient(cursor, fdc_id, nutrient)
        
        # 插入食品份量信息
        food_portions = food.get("foodPortions", [])
        if food_portions:
            insert_food_portions(cursor, fdc_id, food_portions)
    
    # 提交事务
    conn.commit()
    print(f"\n数据导入完成！")
    print(f"数据库文件: {db_path}")
    
    # 显示统计信息
    cursor.execute("SELECT COUNT(*) FROM foods")
    food_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM nutrients")
    nutrient_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM food_nutrients")
    food_nutrient_count = cursor.fetchone()[0]
    
    print(f"\n统计信息:")
    print(f"  食品数量: {food_count}")
    print(f"  营养素种类: {nutrient_count}")
    print(f"  食品-营养素关联: {food_nutrient_count}")
    
    conn.close()


def query_example(db_path="food_data.db"):
    """查询示例"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n=== 查询示例 ===")
    
    # 查询所有食品
    print("\n1. 前5个食品:")
    cursor.execute("""
        SELECT fdc_id, description, food_category 
        FROM foods 
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  - {row[1]} (ID: {row[0]}, 分类: {row[2]})")
    
    # 查询某个食品的营养成分
    cursor.execute("SELECT fdc_id FROM foods LIMIT 1")
    first_food_id = cursor.fetchone()[0]
    
    print(f"\n2. 食品ID {first_food_id} 的营养成分 (前10个):")
    cursor.execute("""
        SELECT n.nutrient_name, fn.amount, n.unit_name
        FROM food_nutrients fn
        JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
        WHERE fn.fdc_id = ?
        LIMIT 10
    """, (first_food_id,))
    
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} {row[2]}")
    
    conn.close()


# 中英文食物名称映射词典
FOOD_TRANSLATION = {
    # 蔬菜类
    "番茄": "tomato", "西红柿": "tomato", "圣女果": "grape tomato",
    "豆角": "snap bean", "四季豆": "snap bean", "青豆": "green bean",
    "胡萝卜": "carrot", "红萝卜": "carrot",
    "土豆": "potato", "马铃薯": "potato",
    "玉米": "corn",
    "黄瓜": "cucumber",
    "生菜": "lettuce",
    "菠菜": "spinach",
    "西兰花": "broccoli",
    "花椰菜": "cauliflower",
    "洋葱": "onion",
    "大蒜": "garlic",
    
    # 肉类
    "牛肉": "beef",
    "猪肉": "pork",
    "鸡肉": "chicken",
    "火腿": "ham",
    "香肠": "sausage",
    "热狗": "frankfurter", "热狗肠": "frankfurter",
    "培根": "bacon",
    
    # 豆制品
    "鹰嘴豆泥": "hummus",
    "豆腐": "tofu",
    "豆浆": "soy milk",
    
    # 坚果
    "杏仁": "almond", "扁桃仁": "almond",
    "核桃": "walnut",
    "花生": "peanut",
    "腰果": "cashew",
    "开心果": "pistachio",
    
    # 水果
    "苹果": "apple",
    "香蕉": "banana",
    "橙子": "orange",
    "葡萄": "grape",
    "草莓": "strawberry",
    "蓝莓": "blueberry",
    
    # 谷物
    "米饭": "rice",
    "面包": "bread",
    "面条": "noodle",
    "意大利面": "pasta",
    "燕麦": "oat",
    
    # 乳制品
    "牛奶": "milk",
    "酸奶": "yogurt",
    "奶酪": "cheese",
    "黄油": "butter",
}


def translate_to_english(chinese_text):
    """将中文食物名称翻译为英文"""
    chinese_text = chinese_text.strip().lower()
    
    # 直接匹配
    if chinese_text in FOOD_TRANSLATION:
        return FOOD_TRANSLATION[chinese_text]
    
    # 部分匹配
    for zh, en in FOOD_TRANSLATION.items():
        if zh in chinese_text or chinese_text in zh:
            return en
    
    return chinese_text


def similarity(a, b):
    """计算两个字符串的相似度"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def search_food_by_name(db_path, search_term, limit=10):
    """根据名称搜索食物（支持模糊搜索）"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 如果是中文，先翻译
    english_term = translate_to_english(search_term)
    
    # 搜索食物
    cursor.execute("""
        SELECT fdc_id, description, food_category
        FROM foods
        WHERE LOWER(description) LIKE ?
        OR LOWER(food_category) LIKE ?
        LIMIT ?
    """, (f"%{english_term}%", f"%{english_term}%", limit * 2))
    
    results = cursor.fetchall()
    conn.close()
    
    # 如果没有结果，尝试模糊匹配
    if not results and english_term != search_term:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT fdc_id, description, food_category FROM foods")
        all_foods = cursor.fetchall()
        conn.close()
        
        # 计算相似度并排序
        scored_results = []
        for food in all_foods:
            score = max(
                similarity(english_term, food[1]),
                similarity(search_term, food[1])
            )
            if score > 0.3:  # 相似度阈值
                scored_results.append((food, score))
        
        scored_results.sort(key=lambda x: x[1], reverse=True)
        results = [item[0] for item in scored_results[:limit]]
    
    return results[:limit]


def get_food_calories(db_path, fdc_id):
    """获取食物的卡路里信息"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取食物基本信息
    cursor.execute("""
        SELECT description, food_category
        FROM foods
        WHERE fdc_id = ?
    """, (fdc_id,))
    
    food_info = cursor.fetchone()
    if not food_info:
        conn.close()
        return None
    
    # 获取卡路里信息（Energy in kcal）
    cursor.execute("""
        SELECT fn.amount, n.unit_name
        FROM food_nutrients fn
        JOIN nutrients n ON fn.nutrient_id = n.nutrient_id
        WHERE fn.fdc_id = ? AND n.nutrient_number = '208'
    """, (fdc_id,))
    
    calorie_info = cursor.fetchone()
    
    # 获取份量信息
    cursor.execute("""
        SELECT amount, measure_unit_name, gram_weight
        FROM food_portions
        WHERE fdc_id = ?
        ORDER BY sequence_number
        LIMIT 3
    """, (fdc_id,))
    
    portions = cursor.fetchall()
    conn.close()
    
    result = {
        "name": food_info[0],
        "category": food_info[1],
        "calories_per_100g": calorie_info[0] if calorie_info else None,
        "unit": calorie_info[1] if calorie_info else None,
        "portions": portions
    }
    
    return result


def query_food_calories(search_term, db_path="food_data.db"):
    """查询食物卡路里的主函数"""
    print(f"\n🔍 搜索: {search_term}")
    print("=" * 60)
    
    # 搜索食物
    results = search_food_by_name(db_path, search_term)
    
    if not results:
        print("❌ 未找到匹配的食物")
        return
    
    print(f"\n找到 {len(results)} 个匹配结果:\n")
    
    # 显示搜索结果
    for idx, (fdc_id, description, category) in enumerate(results, 1):
        print(f"{idx}. {description}")
        print(f"   分类: {category or '未分类'}")
        
        # 获取卡路里信息
        calorie_info = get_food_calories(db_path, fdc_id)
        if calorie_info and calorie_info["calories_per_100g"]:
            print(f"   📊 热量: {calorie_info['calories_per_100g']:.1f} {calorie_info['unit']}/100g")
            
            # 显示常用份量的热量
            if calorie_info["portions"]:
                print(f"   📏 常用份量:")
                for amount, unit, gram_weight in calorie_info["portions"][:2]:
                    calories_for_portion = (calorie_info['calories_per_100g'] * gram_weight) / 100
                    print(f"      • {amount} {unit} ({gram_weight}g) = {calories_for_portion:.1f} {calorie_info['unit']}")
        print()


def interactive_query(db_path="food_data.db"):
    """交互式查询界面"""
    print("\n" + "=" * 60)
    print("🍎 食物卡路里查询系统")
    print("=" * 60)
    print("支持中文和英文搜索，输入 'q' 或 'quit' 退出")
    print("=" * 60)
    
    while True:
        try:
            search_term = input("\n请输入食物名称: ").strip()
            
            if not search_term:
                continue
            
            if search_term.lower() in ['q', 'quit', 'exit', '退出']:
                print("\n👋 再见！")
                break
            
            query_food_calories(search_term, db_path)
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 查询出错: {e}")


def main():
    db_path = "food_data.db"
    
    # 如果数据库不存在，先导入数据
    if not Path(db_path).exists():
        json_file = "FoodData_Central_foundation_food_json_2025-12-18.json"
        
        if not Path(json_file).exists():
            print(f"错误: 找不到文件 {json_file}")
            return
        
        print("首次运行，正在导入数据...")
        parse_json_to_sqlite(json_file, db_path)
        print("\n数据导入完成！\n")
    
    # 启动交互式查询
    interactive_query(db_path)


if __name__ == "__main__":
    main()
