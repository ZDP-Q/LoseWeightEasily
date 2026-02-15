"""用户 API 集成测试。"""

from fastapi.testclient import TestClient


def test_get_user_not_found(client: TestClient):
    """测试获取不存在的用户。"""
    response = client.get("/user")
    assert response.status_code == 404


def test_create_user(client: TestClient):
    """测试创建用户。"""
    user_data = {
        "name": "测试用户",
        "age": 25,
        "gender": "male",
        "height_cm": 175,
        "initial_weight_kg": 80,
        "target_weight_kg": 70,
    }
    response = client.post("/user", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "测试用户"
    assert data["age"] == 25
    assert data["gender"] == "male"
    assert data["height_cm"] == 175
    assert "id" in data


def test_create_user_duplicate(client: TestClient):
    """测试重复创建用户。"""
    user_data = {
        "name": "用户A",
        "age": 25,
        "gender": "male",
        "height_cm": 175,
        "initial_weight_kg": 80,
        "target_weight_kg": 70,
    }
    client.post("/user", json=user_data)
    response = client.post("/user", json=user_data)
    assert response.status_code == 400


def test_get_user_after_create(client: TestClient):
    """测试创建后获取用户。"""
    user_data = {
        "name": "用户B",
        "age": 30,
        "gender": "female",
        "height_cm": 165,
        "initial_weight_kg": 65,
        "target_weight_kg": 55,
    }
    client.post("/user", json=user_data)
    response = client.get("/user")
    assert response.status_code == 200
    assert response.json()["name"] == "用户B"


def test_update_user(client: TestClient):
    """测试更新用户信息。"""
    user_data = {
        "name": "初始名",
        "age": 25,
        "gender": "male",
        "height_cm": 175,
        "initial_weight_kg": 80,
        "target_weight_kg": 70,
    }
    client.post("/user", json=user_data)

    response = client.patch("/user", json={"name": "新名字", "age": 26})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "新名字"
    assert data["age"] == 26
    # 未修改的字段保持不变
    assert data["height_cm"] == 175


def test_update_user_not_found(client: TestClient):
    """测试更新不存在的用户。"""
    response = client.patch("/user", json={"name": "somebody"})
    assert response.status_code == 404


def test_create_user_validation(client: TestClient):
    """测试用户创建校验。"""
    # 缺少必填字段
    response = client.post("/user", json={"name": "test"})
    assert response.status_code == 422

    # 性别无效
    response = client.post(
        "/user",
        json={
            "name": "test",
            "age": 25,
            "gender": "other",
            "height_cm": 175,
            "initial_weight_kg": 80,
            "target_weight_kg": 70,
        },
    )
    assert response.status_code == 422
