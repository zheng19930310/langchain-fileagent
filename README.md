# Langchain FileAgent

基于Python Langchain实现的智能文件助手AI Agent，支持文件操作和对话功能。

## 功能特性

- 📁 文件管理：查看磁盘、列出目录、获取文件大小
- 📝 文件操作：读取、创建、编辑、删除文件
- 📚 知识库管理：上传PDF、Word、Excel等文档并基于内容对话
- 💬 智能对话：基于OpenAI GPT模型的智能对话
- 🔄 会话管理：支持多会话和历史记录保存
- 🚀 流式响应：支持SSE流式输出

## 技术栈

- **Python 3.9+** - 编程语言
- **FastAPI** - Web框架
- **Langchain** - Python AI应用框架
- **OpenAI API** - 大语言模型
- **Pydantic** - 数据验证

## 快速开始

### 1. 环境要求

- Python 3.9+
- OpenAI API Key

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API Key

复制环境配置文件：
```bash
copy .env.example .env
```

编辑 `.env`，填入你的OpenAI API Key：
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 4. 启动应用

#### 方式一：使用启动脚本（推荐）
```bash
start.bat
```

#### 方式二：使用Python命令
```bash
python main.py
```

#### 方式三：使用Uvicorn
```bash
uvicorn main:app --reload --port 8082
```

### 5. 访问应用

应用启动后，默认运行在 http://localhost:8082

- **Web界面**: http://localhost:8082/static/index.html
- **API文档**: http://localhost:8082/docs
- **健康检查**: http://localhost:8082/health

## Web界面

项目提供了一个美观的Web聊天界面，可以直接在浏览器中使用。

### 访问方式

启动服务后，打开浏览器访问：http://localhost:8082/static/index.html

### 功能特性

- 💬 **智能对话**：与AI助手进行自然语言对话
- 📁 **文件操作**：通过对话管理本地文件（查看、创建、编辑、删除）
- 📚 **知识库**：上传PDF、Word、Excel等文档，基于内容提问
- 🔄 **会话管理**：支持多会话切换和历史记录查看
- 📎 **文件上传**：拖拽或点击上传文件到知识库

### 使用示例

1. **查看文件**
   ```
   用户：帮我查看D盘有哪些文件
   AI：调用list_disk工具，显示磁盘列表...
   ```

2. **创建文件**
   ```
   用户：在D:/workspace创建一个test.txt文件，内容为"Hello World"
   AI：调用create_file工具，创建成功！
   ```

3. **上传文档**
   - 点击输入框左侧的 📎 按钮
   - 选择要上传的文件（支持PDF、Word、Excel、PPT等）
   - 发送消息，AI会基于文档内容回答

4. **切换会话**
   - 点击顶部的 + 按钮创建新会话
   - 使用下拉菜单切换已有会话
   - 点击 ↻ 刷新会话列表

## API接口

### 聊天接口

**非流式聊天**
```http
POST /api/chat
Content-Type: application/json

{
  "message": "帮我查看D盘有哪些文件",
  "sessionId": "session_001"
}
```

**带文件的聊天**
```http
POST /api/chat
Content-Type: multipart/form-data

{
  "message": "分析这个文档的内容",
  "sessionId": "session_001",
  "files": [file1.pdf, file2.docx]
}
```

**流式聊天**
```http
POST /api/chat/stream
Content-Type: application/json

{
  "message": "创建一个测试文件",
  "sessionId": "session_001"
}
```

### 会话管理接口

**列出所有会话**
```http
GET /api/chat/sessions
```

**获取会话详情**
```http
GET /api/chat/session/{sessionId}
```

**删除会话**
```http
DELETE /api/chat/session/{sessionId}
```

**清除所有会话**
```http
DELETE /api/chat/sessions
```

### 知识库接口

**上传文件到知识库**
```http
POST /api/kb/upload
Content-Type: multipart/form-data

file: (binary)
sessionId: session_001
```

**获取已上传的文件列表**
```http
GET /api/kb/files?sessionId=session_001
```

**获取知识库统计信息**
```http
GET /api/kb/stats?sessionId=session_001
```

**清除会话的知识库**
```http
DELETE /api/kb/session/{sessionId}
```

**清除所有知识库**
```http
DELETE /api/kb/all
```

## 文件操作工具

AI Agent支持以下文件操作工具：

1. **list_disk** - 查看所有磁盘驱动器及容量信息
2. **list_files** - 列出目录内容
3. **get_file_size** - 获取文件/目录大小
4. **read_file** - 读取文件内容
5. **create_file** - 创建新文件
6. **edit_file** - 编辑文件内容
7. **delete_file** - 删除文件/目录

## 项目结构

```
langchain-fileagent/
├── main.py                           # 主应用入口
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py                 # 聊天API路由
│   │   └── knowledge_base.py       # 知识库API路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py         # 聊天服务
│   │   ├── chat_history.py         # 会话历史服务
│   │   └── knowledge_base.py       # 知识库服务
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # 数据模型
│   └── tools/
│       ├── __init__.py
│       └── file_tools.py           # 文件操作工具
├── data/
│   ├── chat-history/               # 会话历史存储
│   └── knowledge-base/             # 知识库存储
│       ├── .data/                  # 知识库分块数据
│       └── .meta/                  # 文件元数据
├── requirements.txt                 # 依赖包列表
├── .env.example                     # 环境配置示例
└── start.bat                        # 启动脚本
```

## 与原fileAgent的区别

| 特性 | fileAgent (Spring AI) | langchain4j-fileagent | langchain-fileagent |
|------|----------------------|----------------------|---------------------|
| 编程语言 | Java | Java | Python |
| AI框架 | Spring AI Alibaba | Langchain4J | Langchain |
| 模型提供商 | 阿里云通义千问 | OpenAI | OpenAI |
| 工具调用 | 自定义标记解析 | Langchain4J原生支持 | Langchain原生支持 |
| 配置方式 | application.yml | application.yml | .env文件 |
| 知识库功能 | ✅ 支持PDF/Word/Excel/PPT | ❌ 未实现 | ✅ 基础文本文件支持 |
| 文件附件 | ✅ 完整支持 | ❌ 未实现 | ⚠️ 简化版（仅文本） |

## 注意事项

1. **API费用**：使用OpenAI API会产生费用，请注意控制使用量
2. **安全限制**：AI Agent可以访问本地文件系统，请谨慎使用
3. **会话存储**：会话历史保存在 `./data/chat-history` 目录下

## 许可证

MIT License
