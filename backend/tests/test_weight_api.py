"""体重记录 API 集成测试。"""

from fastapi.testclient import TestClient


def test_create_weight_record(client: TestClient):
    """测试创建体重记录。"""
    response = client.post("/weight", json={"weight_kg": 75.5, "notes": "测试记录"})
    assert response.status_code == 200
    data = response.json()
    assert data["weight_kg"] == 75.5
    assert data["notes"] == "测试记录"
    assert "id" in data
    assert "recorded_at" in data


def test_create_weight_record_validation(client: TestClient):
    """测试体重值校验。"""
    # 超出范围
    response = client.post("/weight", json={"weight_kg": 600})
    assert response.status_code == 422

    # 负数
    response = client.post("/weight", json={"weight_kg": 0})
    assert response.status_code == 422


def test_get_weight_records(client: TestClient):
    """测试获取体重记录列表。"""
    # 先创建两条记录
    client.post("/weight", json={"weight_kg": 75.0})
    client.post("/weight", json={"weight_kg": 74.5})

    response = client.get("/weight")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_weight_records_with_limit(client: TestClient):
    """测试 limit 参数。"""
    for i in range(5):
        client.post("/weight", json={"weight_kg": 75.0 - i * 0.5})

    response = client.get("/weight?limit=3")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_update_weight_record(client: TestClient):
    """测试更新体重记录。"""
    # 创建
    create_resp = client.post("/weight", json={"weight_kg": 75.0, "notes": "旧备注"})
    record_id = create_resp.json()["id"]

    # 更新
    response = client.patch(
        f"/weight/{record_id}", json={"weight_kg": 74.0, "notes": "改了"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["weight_kg"] == 74.0
    assert data["notes"] == "改了"


def test_update_weight_record_partial(client: TestClient):
    """测试部分更新（只改 notes）。"""
    create_resp = client.post("/weight", json={"weight_kg": 75.0})
    record_id = create_resp.json()["id"]

    response = client.patch(f"/weight/{record_id}", json={"notes": "新备注"})
    assert response.status_code == 200
    assert response.json()["weight_kg"] == 75.0
    assert response.json()["notes"] == "新备注"


def test_update_weight_record_not_found(client: TestClient):
    """测试更新不存在的记录。"""
    response = client.patch("/weight/99999", json={"weight_kg": 74.0})
    assert response.status_code == 404


def test_delete_weight_record(client: TestClient):
    """测试删除体重记录。"""
    create_resp = client.post("/weight", json={"weight_kg": 75.0})
    record_id = create_resp.json()["id"]

    # 删除
    response = client.delete(f"/weight/{record_id}")
    assert response.status_code == 200

    # 确认删除后列表为空
    response = client.get("/weight")
    assert len(response.json()) == 0


def test_delete_weight_record_not_found(client: TestClient):
    """测试删除不存在的记录。"""
    response = client.delete("/weight/99999")
    assert response.status_code == 404
