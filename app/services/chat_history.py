"""
聊天历史管理服务
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger
from app.models.schemas import SessionInfo, MessageHistory


class ChatHistoryService:
    """聊天历史服务类"""
    
    def __init__(self, history_dir: str = "./data/chat-history"):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_session_id(self) -> str:
        """生成会话ID"""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return f"session_{timestamp}_{unique_id}"
    
    def save_session(self, session_id: str, messages: List[Dict[str, str]]) -> None:
        """保存会话历史
        
        Args:
            session_id: 会话ID
            messages: 消息列表，每个消息包含type和text字段
        """
        try:
            session_file = self.history_dir / f"{session_id}.json"
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存会话历史: {session_id}, 消息数: {len(messages)}")
        except Exception as e:
            logger.error(f"保存会话历史失败: {session_id}, 错误: {e}")
    
    def load_session(self, session_id: str) -> List[Dict[str, str]]:
        """加载会话历史
        
        Args:
            session_id: 会话ID
            
        Returns:
            消息列表
        """
        try:
            session_file = self.history_dir / f"{session_id}.json"
            
            if not session_file.exists():
                return []
            
            with open(session_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            logger.info(f"加载会话历史: {session_id}")
            return messages
        except Exception as e:
            logger.error(f"加载会话历史失败: {session_id}, 错误: {e}")
            return []
    
    def list_sessions(self) -> List[SessionInfo]:
        """列出所有会话
        
        Returns:
            会话信息列表
        """
        try:
            sessions = []
            
            for file_path in self.history_dir.glob("*.json"):
                session_id = file_path.stem
                
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                # 读取消息数量
                messages = self.load_session(session_id)
                message_count = len(messages)
                
                # 生成标题
                title = f"会话 {session_id[:20]}"
                
                sessions.append(SessionInfo(
                    sessionId=session_id,
                    title=title,
                    lastUpdateTime=mtime,
                    messageCount=message_count
                ))
            
            # 按时间排序（最新的在前）
            sessions.sort(key=lambda x: x.lastUpdateTime, reverse=True)
            return sessions
        except Exception as e:
            logger.error(f"列出会话失败: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        try:
            session_file = self.history_dir / f"{session_id}.json"
            
            if session_file.exists():
                session_file.unlink()
                logger.info(f"删除会话: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"删除会话失败: {session_id}, 错误: {e}")
            return False
    
    def clear_all(self) -> None:
        """清除所有会话历史"""
        try:
            for file_path in self.history_dir.glob("*.json"):
                file_path.unlink()
            logger.info("清除所有会话历史")
        except Exception as e:
            logger.error(f"清除所有会话失败: {e}")


# 创建全局实例
history_service = ChatHistoryService()
