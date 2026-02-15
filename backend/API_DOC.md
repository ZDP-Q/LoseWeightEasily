# LoseWeightEasily 后端 API 文档 (v2.0.0)

本文档详细说明了重构后的减肥助手后端接口。

## 🚀 基础信息

- **Base URL**: `http://localhost:8000`
- **内容类型**: `application/json`
- **认证**: 目前为公开接口（待添加）

---

## 🥗 食物搜索 (Food Search)

### 1. 语义搜索食物
通过 FAISS 向量索引和语义模型查找最匹配的食物。

- **URL**: `/search`
- **Method**: `GET`
- **Query Parameters**:
    - `query` (string, required): 搜索关键词（如 "苹果", "高蛋白晚餐"）
    - `limit` (int, optional): 返回结果数量，默认 10

- **Response Example**:
```json
[
  {
    "fdc_id": 1102653,
    "description": "Apples, raw, gala, with skin",
    "category": "Fruits and Fruit Juices",
    "calories_per_100g": 52.0,
    "similarity": 0.85
  }
]
```

---

## 📈 健康指标计算 (Calculation)

### 1. 计算 BMR 和 TDEE
根据个人信息计算基础代谢率（BMR）及不同活动强度下的总日能量消耗（TDEE）。

- **URL**: `/calculate/bmr`
- **Method**: `POST`
- **Request Body**:
```json
{
  "weight_kg": 70.5,
  "height_cm": 175.0,
  "age": 25,
  "gender": "male"
}
```
- **Response Example**:
```json
{
  "bmr": 1724.05,
  "tdee": {
    "sedentary": 2068.86,
    "light": 2370.57,
    "moderate": 2672.28,
    "active": 2973.99,
    "very_active": 3275.69
  }
}
```

---

## 📝 体重追踪 (Weight Tracking)

### 1. 记录体重
添加一条新的体重记录。

- **URL**: `/weight`
- **Method**: `POST`
- **Request Body**:
```json
{
  "weight_kg": 68.5,
  "notes": "早起空腹体重"
}
```
- **Response Example**:
```json
{
  "id": 1,
  "weight_kg": 68.5,
  "recorded_at": "2024-02-15T08:00:00Z",
  "notes": "早起空腹体重"
}
```

### 2. 获取体重历史
按记录时间倒序获取体重历史记录。

- **URL**: `/weight`
- **Method**: `GET`
- **Query Parameters**:
    - `limit` (int, optional): 返回记录条数，默认 100

---

## 🍽️ 饮食计划 (Meal Planning)

### 1. AI 生成饮食计划
基于现有食材和偏好，利用 AI 生成个性化的一日三餐计划。

- **URL**: `/meal-plan`
- **Method**: `POST`
- **Request Body**:
```json
{
  "ingredients": ["鸡胸肉", "西兰花", "糙米"],
  "preferences": "简单易做",
  "dietary_restrictions": "无"
}
```
- **Response Example**:
```json
{
  "plan": "### 早餐
- 糙米粥配水煮蛋...
### 午餐
- 香煎鸡胸肉配水煮西兰花...",
  "ingredients": ["鸡胸肉", "西兰花", "糙米"]
}
```

---

## 🛠️ 其他接口

### 1. 健康检查
- **URL**: `/health`
- **Method**: `GET`
- **Response**: `{"status": "healthy", "version": "2.0.0"}`

---

## 💻 开发者说明

### 本地运行
1. 安装依赖: `cd backend && uv sync`
2. 启动服务: `uv run uvicorn src.app:app --reload`
3. 交互式文档: 启动后访问 [http://localhost:8000/docs](http://localhost:8000/docs) 即可查看 Swagger UI。

### 注意事项
- 确保 `data/` 目录下存在 `food_index.faiss` 和 `food_metadata.pkl` 文件，否则搜索功能不可用。
- AI 生成计划需要配置 OpenAI API Key。
