"""测试工具调用"""
import requests

API_BASE = "http://localhost:8082"

# 测试1：读取文件
print("=" * 50)
print("测试1：读取 D:\\aa.txt")
print("=" * 50)

response = requests.post(
    f"{API_BASE}/api/chat",
    json={
        "message": "帮我读取 D:\\aa.txt 这个文件里的内容",
        "sessionId": "test-123"
    }
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"AI回复: {data.get('response', '无回复')}")
else:
    print(f"错误: {response.text}")

print("\n" + "=" * 50)
print("测试2：创建文件 D:\\bb.txt")
print("=" * 50)

response = requests.post(
    f"{API_BASE}/api/chat",
    json={
        "message": "帮我再d盘创建bb.txt,内容为：哈哈哈",
        "sessionId": "test-456"
    }
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"AI回复: {data.get('response', '无回复')}")
else:
    print(f"错误: {response.text}")
