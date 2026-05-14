# 知识库功能快速上手指南

## 🚀 快速开始

### 1. 启动服务

```bash
cd d:\aiwork\langchain-fileagent
start.bat
```

服务将在 `http://localhost:8082` 启动

### 2. 访问API文档

打开浏览器访问：`http://localhost:8082/docs`

你将看到所有可用的API接口，包括新增的知识库接口。

## 📚 使用示例

### 方式一：通过 Swagger UI（推荐）

1. 访问 `http://localhost:8082/docs`
2. 找到 `/api/kb/upload` 接口
3. 点击 "Try it out"
4. 选择要上传的文件
5. 输入 sessionId（例如：`test_session_001`）
6. 点击 "Execute"

### 方式二：使用 cURL

#### 上传文件到知识库

```bash
curl -X POST "http://localhost:8082/api/kb/upload" \
  -F "file=@D:/workspace/test.txt" \
  -F "sessionId=test_session_001"
```

#### 获取已上传的文件列表

```bash
curl -X GET "http://localhost:8082/api/kb/files?sessionId=test_session_001"
```

#### 获取知识库统计信息

```bash
curl -X GET "http://localhost:8082/api/kb/stats?sessionId=test_session_001"
```

#### 带文件的聊天

```bash
curl -X POST "http://localhost:8082/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "这个文档讲了什么？",
    "sessionId": "test_session_001",
    "filePaths": ["D:/workspace/test.txt"],
    "fileNames": ["test.txt"]
  }'
```

### 方式三：使用 Python requests

```python
import requests

BASE_URL = "http://localhost:8082"
session_id = "my_session_001"

# 1. 上传文件
with open("document.txt", "rb") as f:
    files = {"file": ("document.txt", f, "text/plain")}
    data = {"sessionId": session_id}
    response = requests.post(f"{BASE_URL}/api/kb/upload", files=files, data=data)
    print(response.json())

# 2. 查看文件列表
response = requests.get(f"{BASE_URL}/api/kb/files", params={"sessionId": session_id})
print(response.json())

# 3. 基于文档内容提问
chat_data = {
    "message": "总结这个文档的主要内容",
    "sessionId": session_id,
    "filePaths": ["document.txt"],
    "fileNames": ["document.txt"]
}
response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
print(response.text)
```

## 💡 实际应用场景

### 场景1：分析技术文档

```python
# 上传 Python 教程文档
with open("python_tutorial.md", "rb") as f:
    requests.post(
        f"{BASE_URL}/api/kb/upload",
        files={"file": ("python_tutorial.md", f)},
        data={"sessionId": "learning_session"}
    )

# 提问
response = requests.post(f"{BASE_URL}/api/chat", json={
    "message": "Python中的装饰器是什么？如何使用？",
    "sessionId": "learning_session",
    "filePaths": ["python_tutorial.md"],
    "fileNames": ["python_tutorial.md"]
})
print(response.text)
```

### 场景2：代码审查助手

```python
# 上传源代码文件
for code_file in ["main.py", "utils.py", "config.py"]:
    with open(code_file, "rb") as f:
        requests.post(
            f"{BASE_URL}/api/kb/upload",
            files={"file": (code_file, f)},
            data={"sessionId": "code_review"}
        )

# 请求代码审查
response = requests.post(f"{BASE_URL}/api/chat", json={
    "message": "这些代码有什么可以优化的地方？",
    "sessionId": "code_review",
    "filePaths": ["main.py", "utils.py", "config.py"],
    "fileNames": ["main.py", "utils.py", "config.py"]
})
print(response.text)
```

### 场景3：会议纪要分析

```python
# 上传会议记录
with open("meeting_notes.txt", "rb") as f:
    requests.post(
        f"{BASE_URL}/api/kb/upload",
        files={"file": ("meeting_notes.txt", f)},
        data={"sessionId": "meeting_20260512"}
    )

# 提取关键信息
response = requests.post(f"{BASE_URL}/api/chat", json={
    "message": "列出本次会议的决定事项和待办任务",
    "sessionId": "meeting_20260512",
    "filePaths": ["meeting_notes.txt"],
    "fileNames": ["meeting_notes.txt"]
})
print(response.text)
```

## 🔧 配置说明

### 环境变量配置

编辑 `.env` 文件：

```env
# OpenAI API配置
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_BASE_URL=https://api.openai.com/v1

# 服务器配置
PORT=8082
HOST=0.0.0.0

# 知识库配置
KB_BASE_PATH=./data/knowledge-base

# 日志级别
LOG_LEVEL=INFO
```

### 知识库存储位置

知识库数据存储在：
```
d:\aiwork\langchain-fileagent\data\knowledge-base\
├── .data\          # 知识库分块数据（JSON格式）
│   └── {session_id}.json
└── .meta\          # 文件元数据（JSON格式）
    └── {session_id}.json
```

## ⚠️ 注意事项

### 1. 支持的文件格式

**当前支持：**
- 纯文本文件：`.txt`, `.md`
- 代码文件：`.py`, `.js`, `.java`, `.html`, `.css`
- 配置文件：`.json`, `.xml`, `.yml`, `.yaml`

**暂不支持（未来版本）：**
- PDF 文档
- Word 文档（.docx, .doc）
- Excel 表格（.xlsx, .xls）
- PowerPoint 演示文稿（.pptx, .ppt）

### 2. 文件大小限制

- 建议单个文件不超过 1MB
- 大文件会被分割成多个分块（每块约1000字符）
- 每次对话最多使用5个分块作为上下文

### 3. Token 限制

- OpenAI API 有 token 限制
- 知识库内容会占用部分 token
- 如果文档太长，可能无法全部放入上下文

### 4. 会话管理

- 每个 sessionId 有独立的知识库
- 清除会话会同时清除该会话的知识库
- 会话数据持久化保存在磁盘上

## 🐛 常见问题

### Q1: 上传文件后提示"无法读取文件内容"

**原因：** 文件格式不支持或编码错误

**解决：** 
- 确保文件是 UTF-8 编码的文本文件
- 检查文件扩展名是否在支持列表中

### Q2: AI回答没有引用文档内容

**原因：** 知识库分块未正确注入上下文

**解决：**
- 检查知识库统计：`GET /api/kb/stats?sessionId=xxx`
- 确认 `chunkCount > 0`
- 查看日志确认文件上传成功

### Q3: 响应速度很慢

**原因：** 文档太大或网络延迟

**解决：**
- 减小文档大小
- 减少分块数量（修改 `_split_into_chunks` 参数）
- 检查网络连接

### Q4: 如何清除所有测试数据？

**方法1：** 使用API
```bash
curl -X DELETE "http://localhost:8082/api/kb/all"
```

**方法2：** 手动删除
```bash
# 删除知识库数据目录
rm -rf d:\aiwork\langchain-fileagent\data\knowledge-base\.data\*
rm -rf d:\aiwork\langchain-fileagent\data\knowledge-base\.meta\*
```

## 📖 更多资源

- [完整API文档](http://localhost:8082/docs)
- [项目README](README.md)
- [功能对齐总结](FUNCTION_ALIGNMENT_SUMMARY.md)

## 🎉 开始使用

现在你已经了解了如何使用知识库功能，开始上传你的文档并体验智能对话吧！

```bash
# 运行测试脚本验证功能
python test_kb.py
```

祝你使用愉快！🚀
