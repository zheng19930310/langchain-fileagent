"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息")
    sessionId: Optional[str] = Field(None, description="会话ID")
    filePaths: Optional[List[str]] = Field(None, description="文件路径列表")
    fileNames: Optional[List[str]] = Field(None, description="文件名列表")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI回复")
    sessionId: str = Field(..., description="会话ID")


class SessionInfo(BaseModel):
    """会话信息模型"""
    sessionId: str = Field(..., description="会话ID")
    title: str = Field(..., description="会话标题")
    lastUpdateTime: datetime = Field(..., description="最后更新时间")
    messageCount: int = Field(0, description="消息数量")


class MessageHistory(BaseModel):
    """消息历史模型"""
    type: str = Field(..., description="消息类型")
    text: str = Field(..., description="消息内容")
