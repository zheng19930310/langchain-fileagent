"""
Langchain FileAgent - 基于Langchain的智能文件助手
"""
# 必须先加载环境变量，再导入其他模块
import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import chat, knowledge_base
import uvicorn

app = FastAPI(
    title="Langchain FileAgent",
    description="AI Agent for file operations with Langchain",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(chat.router)
app.include_router(knowledge_base.router)

@app.get("/")
async def root():
    return {
        "message": "Langchain FileAgent API",
        "version": "1.0.0",
        "docs": "/docs",
        "ui": "/static/index.html"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8082))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
