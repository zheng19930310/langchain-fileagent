"""
知识库功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8082"

def test_knowledge_base():
    """测试知识库功能"""
    
    session_id = "test_session_001"
    
    print("=" * 60)
    print("知识库功能测试")
    print("=" * 60)
    
    # 1. 检查初始状态
    print("\n1. 检查初始状态...")
    response = requests.get(f"{BASE_URL}/api/kb/stats", params={"sessionId": session_id})
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 2. 创建测试文件
    print("\n2. 创建测试文件...")
    test_file_path = "test_document.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("""这是一个测试文档。
        
Langchain FileAgent 是一个基于 Python Langchain 实现的智能文件助手。
它支持以下功能：
1. 文件管理：查看磁盘、列出目录、获取文件大小
2. 文件操作：读取、创建、编辑、删除文件
3. 知识库管理：上传文档并基于内容对话
4. 智能对话：基于OpenAI GPT模型的智能对话

这个项目的目标是提供一个简单易用的文件操作AI助手。
""")
    print(f"   测试文件已创建: {test_file_path}")
    
    # 3. 上传文件到知识库
    print("\n3. 上传文件到知识库...")
    with open(test_file_path, "rb") as f:
        files = {"file": (test_file_path, f, "text/plain")}
        data = {"sessionId": session_id}
        response = requests.post(f"{BASE_URL}/api/kb/upload", files=files, data=data)
    
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 获取已上传的文件列表
    print("\n4. 获取已上传的文件列表...")
    response = requests.get(f"{BASE_URL}/api/kb/files", params={"sessionId": session_id})
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 5. 获取知识库统计信息
    print("\n5. 获取知识库统计信息...")
    response = requests.get(f"{BASE_URL}/api/kb/stats", params={"sessionId": session_id})
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 6. 测试带文件的聊天
    print("\n6. 测试带文件的聊天...")
    chat_data = {
        "message": "这个文档主要讲了什么？",
        "sessionId": session_id,
        "filePaths": [test_file_path],
        "fileNames": [test_file_path]
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text[:200]}...")
    
    # 7. 清除会话知识库
    print("\n7. 清除会话知识库...")
    response = requests.delete(f"{BASE_URL}/api/kb/session/{session_id}")
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 清理测试文件
    import os
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print(f"\n   测试文件已删除: {test_file_path}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_knowledge_base()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

