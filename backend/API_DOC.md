# LoseWeightEasily 后端 API 文档 (v3.0.0)

本文档说明了基于 FastAPI 重构后的减肥助手后端接口。

## 🚀 基础信息

- **Base URL**: `http://127.0.0.1:16666`
- **内容类型**: `application/json`
- **认证**: 所有请求必须在 Header 中携带 `X-API-Key`。
    - Header: `X-API-Key: <your_api_key>`

---

## 🥗 食物识别 (Food Analysis)

### 1. 图片识别食物 (三路并发)
上传图片字节流，AI 会执行 3 次独立并发识别，并返回平均热量及详细成分。识别后的图片将自动存入 MinIO，记录存入 PostgreSQL。

- **URL**: `/food-analysis/recognize`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Request Body**:
    - `file` (UploadFile): 食物照片 (JPG/PNG)

- **Response Example**:
```json
{
  "final_food_name": "彩虹沙拉碗",
  "final_estimated_calories": 573,
  "raw_data": [
    {
      "food_name": "彩虹沙拉碗",
      "calories": 600,
      "confidence": 0.95,
      "components": ["牛油果", "红薯", "鹰嘴豆"]
    }
  ],
  "timestamp": "2026-02-20T13:15:25.254672"
}
```

---

## 💬 智能对话 (Chat)

### 1. 流式对话 (Xiao Song Agent)
支持 Tool Calling 和 RAG (基于 Milvus 检索 USDA 食物库)。对话过程中 Agent 会自动调用工具（如规划食谱、查询历史数据）。

- **URL**: `/chat/stream`
- **Method**: `POST`
- **Request Body**:
```json
{
  "message": "我今天中午吃了沙拉，晚上建议吃什么？",
  "history": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "user_info": "体重70kg, 目标减重"
}
```
- **Response Format**: `text/event-stream` (SSE)
    - `event: text`: 增量文本内容
    - `event: action_result`: 工具执行结果 (JSON)
    - `event: usage`: Token 消耗统计
    - `event: done`: 对话结束

---

## 📈 体重记录 (Weight Tracking)

### 1. 添加体重记录
- **URL**: `/weight`
- **Method**: `POST`
- **Request Body**:
```json
{
  "weight_kg": 68.5,
  "notes": "早起空腹"
}
```

### 2. 获取体重趋势
- **URL**: `/weight/history`
- **Method**: `GET`
- **Query Parameters**:
    - `limit` (int): 返回记录条数，默认 30

---

## 🍽️ 饮食计划 (Meal Plan)

### 1. 自动生成今日计划
- **URL**: `/meal-plan/generate`
- **Method**: `POST`
- **Request Body**:
```json
{
  "ingredients": ["鸡胸肉", "西兰花"],
  "target_calories": 1800
}
```

---

## 👤 用户管理 (User)

### 1. 获取/更新用户信息
- **URL**: `/user/profile`
- **Method**: `GET` / `PATCH`

---

## 🛠️ 运维接口

### 1. 健康检查
- **URL**: `/health`
- **Method**: `GET`
- **Response**: `{"status": "healthy", "version": "3.0.0"}`

---

## 💻 开发者控制台
- **Swagger UI**: [http://127.0.0.1:16666/docs](http://127.0.0.1:16666/docs)
- **Redoc**: [http://127.0.0.1:16666/redoc](http://127.0.0.1:16666/redoc)

### 本地启动
```bash
cd backend
uv sync
uv run uvicorn src.app:app --port 16666 --reload
```
