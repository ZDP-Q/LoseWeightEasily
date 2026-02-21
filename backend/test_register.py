import requests
import uuid

BASE_URL = "http://127.0.0.1:16666"


def test_registration():
    # 生成一个随机用户名，确保不会重复
    unique_username = f"test_{uuid.uuid4().hex[:6]}"
    payload = {
        "username": unique_username,
        "password": "password123",
        "email": f"{unique_username}@example.com",
    }

    print(f"尝试注册用户: {payload['username']}")

    try:
        response = requests.post(f"{BASE_URL}/user/register", json=payload)
        print(f"状态码: {response.status_code}")
        print(f"响应体: {response.text}")

        if response.status_code == 200:
            print("注册成功！")
        else:
            print(f"注册失败，错误详情: {response.json().get('detail', '未知错误')}")

    except Exception as e:
        print(f"连接失败: {e}")


if __name__ == "__main__":
    test_registration()
