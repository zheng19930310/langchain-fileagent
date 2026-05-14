"""
测试聊天API接口
"""
import requests
import json

print("=" * 60)
print("测试聊天API接口")
print("=" * 60)

# 测试健康检查
print("\n[测试1] 健康检查...")
try:
    response = requests.get("http://localhost:8082/health")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.json()}")
except Exception as e:
    print(f"   失败: {e}")

# 测试获取会话列表
print("\n[测试2] 获取会话列表...")
try:
    response = requests.get("http://localhost:8082/api/chat/sessions")
    print(f"  状态码: {response.status_code}")
    sessions = response.json()
    print(f"  会话数量: {len(sessions)}")
except Exception as e:
    print(f"  ❌ 失败: {e}")

# 测试发送消息
print("\n[测试3] 发送测试消息...")
try:
    # 先创建一个会话
    session_response = requests.post("http://localhost:8082/api/chat/sessions")
    session_data = session_response.json()
    session_id = session_data.get("sessionId", session_data.get("id", ""))
    print(f"  会话ID: {session_id}")
    
    # 发送消息
    response = requests.post(
        "http://localhost:8082/api/chat",
        json={
            "message": "你好，请简单介绍一下你自己",
            "sessionId": session_id
        }
    )
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  响应内容: {data}")
        if "response" in data or "message" in data:
            print(f"  ✅ 成功收到回复!")
            reply = data.get("response") or data.get("message")
            print(f"  AI回复: {reply[:200]}...")
        else:
            print(f"  ❌ 响应格式不正确")
    else:
        print(f"  ❌ 请求失败: {response.text}")
        
except Exception as e:
    print(f"  ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
