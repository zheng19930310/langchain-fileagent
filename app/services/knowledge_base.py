"""
知识库服务 - 处理文档上传、解析和管理
"""
import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
from datetime import datetime


class KnowledgeBaseService:
    """知识库服务类"""
    
    def __init__(self):
        # 知识库基础路径
        self.kb_base_path = os.getenv("KB_BASE_PATH", "./data/knowledge-base")
        self.kb_data_dir = os.path.join(self.kb_base_path, ".data")
        self.kb_files_dir = os.path.join(self.kb_base_path, ".meta")
        
        # 确保目录存在
        os.makedirs(self.kb_data_dir, exist_ok=True)
        os.makedirs(self.kb_files_dir, exist_ok=True)
        
        # 会话知识库缓存: session_id -> chunks
        self.session_kb = {}
        
        # 会话文件元数据: session_id -> file_info_list
        self.session_files = {}
        
        logger.info(f"知识库服务初始化完成，基础路径: {self.kb_base_path}")
    
    def upload_file(self, session_id: str, file_path: str, file_name: str) -> Dict:
        """上传文件到知识库
        
        Args:
            session_id: 会话ID
            file_path: 文件路径
            file_name: 文件名
            
        Returns:
            上传结果
        """
        try:
            logger.info(f"开始上传文件: {file_name} (session: {session_id})")
            
            # 读取文件内容（简化版，只支持文本文件）
            content = self._read_file_content(file_path)
            
            if not content:
                return {"success": False, "error": "无法读取文件内容"}
            
            # 分块处理
            chunks = self._split_into_chunks(content)
            
            # 保存到会话知识库
            if session_id not in self.session_kb:
                self.session_kb[session_id] = []
            self.session_kb[session_id].extend(chunks)
            
            # 保存文件元数据
            file_info = {
                "fileName": file_name,
                "uploadTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "size": os.path.getsize(file_path),
                "chunks": len(chunks)
            }
            
            if session_id not in self.session_files:
                self.session_files[session_id] = []
            self.session_files[session_id].append(file_info)
            
            # 持久化到磁盘
            self._save_session_data(session_id)
            
            logger.info(f"文件上传成功: {file_name}, 分块数: {len(chunks)}")
            
            return {
                "success": True,
                "fileName": file_name,
                "chunkCount": len(chunks),
                "message": f"文件 '{file_name}' 已成功上传并处理"
            }
            
        except Exception as e:
            logger.error(f"文件上传失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_uploaded_files(self, session_id: str) -> List[Dict]:
        """获取会话已上传的文件列表
        
        Args:
            session_id: 会话ID
            
        Returns:
            文件信息列表
        """
        return self.session_files.get(session_id, [])
    
    def has_knowledge_base(self, session_id: str) -> bool:
        """检查会话是否有知识库
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否有知识库
        """
        return session_id in self.session_kb and len(self.session_kb[session_id]) > 0
    
    def get_chunk_count(self, session_id: str) -> int:
        """获取知识库分块数量
        
        Args:
            session_id: 会话ID
            
        Returns:
            分块数量
        """
        return len(self.session_kb.get(session_id, []))
    
    def get_knowledge_chunks(self, session_id: str) -> List[str]:
        """获取知识库的所有分块
        
        Args:
            session_id: 会话ID
            
        Returns:
            文本分块列表
        """
        return self.session_kb.get(session_id, [])
    
    def clear_session(self, session_id: str) -> None:
        """清除会话的知识库
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.session_kb:
            del self.session_kb[session_id]
        if session_id in self.session_files:
            del self.session_files[session_id]
        
        # 删除持久化文件
        kb_file = os.path.join(self.kb_data_dir, f"{session_id}.json")
        meta_file = os.path.join(self.kb_files_dir, f"{session_id}.json")
        
        if os.path.exists(kb_file):
            os.remove(kb_file)
        if os.path.exists(meta_file):
            os.remove(meta_file)
        
        logger.info(f"会话知识库已清除: {session_id}")
    
    def clear_all(self) -> None:
        """清除所有知识库"""
        self.session_kb.clear()
        self.session_files.clear()
        
        # 删除所有持久化文件
        for file in os.listdir(self.kb_data_dir):
            os.remove(os.path.join(self.kb_data_dir, file))
        for file in os.listdir(self.kb_files_dir):
            os.remove(os.path.join(self.kb_files_dir, file))
        
        logger.info("所有知识库已清除")
    
    def _read_file_content(self, file_path: str) -> str:
        """读取文件内容（简化版，仅支持文本文件）
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            # 检测文件类型
            ext = Path(file_path).suffix.lower()
            
            if ext in ['.txt', '.md', '.py', '.js', '.java', '.html', '.css', '.json', '.xml', '.yml', '.yaml']:
                # 文本文件直接读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 其他格式暂不支持
                logger.warning(f"不支持的文件格式: {ext}")
                return ""
                
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return ""
    
    def _split_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """将文本分割成块
        
        Args:
            text: 原始文本
            chunk_size: 每块大小（字符数）
            overlap: 重叠大小
            
        Returns:
            文本块列表
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # 如果还有更多内容，尝试在句子边界切割
            if end < len(text):
                # 查找最近的句号或换行符
                last_period = text.rfind('。', start, end)
                last_newline = text.rfind('\n', start, end)
                split_point = max(last_period, last_newline)
                
                if split_point > start:
                    end = split_point + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def _save_session_data(self, session_id: str) -> None:
        """保存会话数据到磁盘
        
        Args:
            session_id: 会话ID
        """
        try:
            # 保存知识库分块
            kb_file = os.path.join(self.kb_data_dir, f"{session_id}.json")
            with open(kb_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "chunks": self.session_kb.get(session_id, []),
                    "files": self.session_files.get(session_id, [])
                }, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"会话数据已保存: {session_id}")
        except Exception as e:
            logger.error(f"保存会话数据失败: {e}")
    
    def load_session_data(self, session_id: str) -> None:
        """从磁盘加载会话数据
        
        Args:
            session_id: 会话ID
        """
        try:
            kb_file = os.path.join(self.kb_data_dir, f"{session_id}.json")
            
            if os.path.exists(kb_file):
                with open(kb_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.session_kb[session_id] = data.get("chunks", [])
                self.session_files[session_id] = data.get("files", [])
                
                logger.info(f"会话数据已加载: {session_id}")
        except Exception as e:
            logger.error(f"加载会话数据失败: {e}")


# 创建全局实例
kb_service = KnowledgeBaseService()
