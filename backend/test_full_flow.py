import requests
import uuid

BASE_URL = "http://127.0.0.1:16666"


def run_full_test():
    # 1. 注册新用户
    username = f"user_{uuid.uuid4().hex[:6]}"
    password = "secret_password"

    print(f"\n--- 步骤 1: 注册新用户 [{username}] ---")
    reg_response = requests.post(
        f"{BASE_URL}/user/register",
        json={
            "username": username,
            "password": password,
            "email": f"{username}@test.com",
        },
    )
    print(f"状态码: {reg_response.status_code}")
    if reg_response.status_code != 200:
        print(f"错误: {reg_response.text}")
        return

    # 2. 登录并获取 Token
    print("\n--- 步骤 2: 登录 ---")
    login_response = requests.post(
        f"{BASE_URL}/user/login", json={"username": username, "password": password}
    )
    print(f"状态码: {login_response.status_code}")
    token = login_response.json().get("access_token")
    if token:
        print(f"获取到 Access Token: {token[:20]}...")
    else:
        print("登录失败: 没获取到 Token")
        return

    # 3. 访问 /me 验证权限
    print("\n--- 步骤 3: 验证权限 (/user/me) ---")
    headers = {"Authorization": f"Bearer {token}"}
    me_response = requests.get(f"{BASE_URL}/user/me", headers=headers)
    print(f"状态码: {me_response.status_code}")
    print(f"返回用户名: {me_response.json().get('username')}")

    # 4. 初始化资料 (模拟 Onboarding)
    print("\n--- 步骤 4: 初始化资料 (Onboarding) ---")
    profile_data = {
        "age": 25,
        "gender": "male",
        "height_cm": 175.0,
        "initial_weight_kg": 80.0,
        "target_weight_kg": 70.0,
        "activity_level": "moderate",
    }
    profile_response = requests.put(
        f"{BASE_URL}/user/profile", json=profile_data, headers=headers
    )
    print(f"状态码: {profile_response.status_code}")

    if profile_response.status_code == 200:
        result = profile_response.json()
        print(f"计算出的 BMR: {result.get('bmr')}")
        print(f"计算出的 TDEE: {result.get('tdee')}")
        print(f"每日热量目标: {result.get('daily_calorie_goal')}")
        print("\n✅ 全流程测试通过！后端逻辑完全正常。")
    else:
        print(f"初始化资料失败: {profile_response.text}")


if __name__ == "__main__":
    run_full_test()
