"""
聊天服务 - 使用Langchain实现AI对话和工具调用
"""
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List, Dict, Optional
from loguru import logger
import os

from app.tools.file_tools import file_tools
from app.services.chat_history import history_service
from app.services.knowledge_base import kb_service


class ChatService:
    """聊天服务类"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        # 调试日志
        logger.debug(f"[ChatService] API Key: {self.api_key[:10]}..." if self.api_key else "[ChatService] API Key: 空")
        logger.debug(f"[ChatService] Model: {self.model_name}")
        logger.debug(f"[ChatService] Base URL: {self.base_url}")
        
        # 会话内存缓存
        self.session_memories = {}
        
        # 系统提示词
        self.system_prompt = """你是一个智能文件助手，可以帮助用户管理本地文件和回答问题。

你拥有以下文件操作工具，当用户需要时会自动调用：
1. list_disk - 查看所有磁盘驱动器及容量信息（无参数）
2. list_files - 列出目录内容（参数：directory_path - 目录路径）
3. get_file_size - 获取文件/目录大小（参数：file_path - 文件路径）
4. read_file - 读取文件内容（参数：file_path - 文件路径, max_length - 最大长度，可选）
5. create_file - 创建新文件（参数：file_path - 文件路径, content - 文件内容）
6. edit_file - 编辑文件内容（参数：file_path - 文件路径, new_content - 新的文件内容）
7. delete_file - 删除文件/目录（参数：file_path - 文件路径）

使用规则：
1. 当需要调用工具时，直接调用相应的工具函数
2. 调用工具后，用自然语言向用户解释结果
3. 路径格式使用正斜杠，如 D:/workspace/test.txt
4. 如果问题不涉及文件操作，直接回答
"""
    
    def _create_llm(self):
        """创建语言模型实例"""
        return ChatOpenAI(
            openai_api_key=self.api_key,
            model_name=self.model_name,
            openai_api_base=self.base_url,
            temperature=0.7
        )
    
    def _get_session_messages(self, session_id: str) -> List:
        """获取会话消息列表"""
        if session_id not in self.session_memories:
            messages = []
            
            # 添加系统提示词
            messages.append(SystemMessage(content=self.system_prompt))
            
            # 加载历史消息
            saved_messages = history_service.load_session(session_id)
            if saved_messages:
                for msg in saved_messages:
                    msg_type = msg.get('type', '')
                    msg_text = msg.get('text', '')
                    
                    if msg_type == 'human':
                        messages.append(HumanMessage(content=msg_text))
                    elif msg_type == 'ai':
                        messages.append(AIMessage(content=msg_text))
                
                logger.info(f"从文件加载 {len(saved_messages)} 条历史消息: {session_id}")
            
            self.session_memories[session_id] = messages
        
        return self.session_memories[session_id]
    
    def chat(self, message: str, session_id: str) -> str:
        """普通聊天
        
        Args:
            message: 用户消息
            session_id: 会话ID
            
        Returns:
            AI回复
        """
        logger.info(f"=== [chat] 用户输入: {message} ===")
        
        try:
            # 获取会话消息
            messages = self._get_session_messages(session_id)
            
            # 创建LLM
            llm = self._create_llm()
            
            # 创建 Agent
            agent = create_agent(
                llm,
                file_tools,
                system_prompt=self.system_prompt
            )
            
            # 执行对话
            response = agent.invoke({
                "messages": [HumanMessage(content=message)]
            })
            
            # 从响应中获取最后一条 AI 消息
            messages = response.get("messages", [])
            result = "抱歉，我没有生成回复"
            for msg in reversed(messages):
                if hasattr(msg, 'content') and hasattr(msg, 'type') and msg.type == 'ai':
                    result = msg.content
                    break
            
            logger.info(f"[chat] AI回复: {result}")
            
            # 保存会话
            messages.append(HumanMessage(content=message))
            messages.append(AIMessage(content=result))
            self._save_session(session_id)
            
            return result
        except Exception as e:
            logger.error(f"聊天失败: {e}")
            return f"抱歉，处理您的请求时出现错误: {str(e)}"
    
    def chat_with_files(self, message: str, file_paths: List[str], 
                       file_names: List[str], session_id: str) -> str:
        """带文件的聊天（使用知识库）
        
        Args:
            message: 用户消息
            file_paths: 文件路径列表
            file_names: 文件名列表
            session_id: 会话ID
            
        Returns:
            AI回复
        """
        logger.info(f"=== [chatWithFiles] 用户输入: {message}, 文件数: {len(file_paths)} ===")
        
        try:
            # 上传文件到知识库
            for file_path, file_name in zip(file_paths, file_names):
                result = kb_service.upload_file(session_id, file_path, file_name)
                if result.get("success"):
                    logger.info(f"文件已添加到知识库: {file_name}")
                else:
                    logger.warning(f"文件上传失败: {file_name} - {result.get('error')}")
            
            # 获取知识库内容
            kb_chunks = kb_service.get_knowledge_chunks(session_id)
            
            # 如果有知识库内容，将其添加到消息中
            if kb_chunks:
                kb_context = "\n\n".join(kb_chunks[:5])  # 只取前5个分块，避免上下文过长
                enhanced_message = f"""基于以下文档内容回答问题：

{kb_context}

用户问题：{message}"""
                return self.chat(enhanced_message, session_id)
            else:
                return self.chat(message, session_id)
                
        except Exception as e:
            logger.error(f"带文件聊天失败: {e}")
            return f"抱歉，处理文件时出现错误: {str(e)}"
    
    def stream_chat(self, message: str, session_id: str):
        """流式聊天（简化版，返回单个响应）
        
        Args:
            message: 用户消息
            session_id: 会话ID
            
        Yields:
            AI回复片段
        """
        logger.info(f"=== [stream] 用户输入: {message} ===")
        
        # Langchain的流式支持较为复杂，这里先返回完整响应
        response = self.chat(message, session_id)
        yield response
    
    def stream_chat_with_files(self, message: str, file_paths: List[str],
                               file_names: List[str], session_id: str):
        """带文件的流式聊天"""
        try:
            # 上传文件到知识库
            for file_path, file_name in zip(file_paths, file_names):
                result = kb_service.upload_file(session_id, file_path, file_name)
                if result.get("success"):
                    logger.info(f"文件已添加到知识库: {file_name}")
            
            # 获取知识库内容
            kb_chunks = kb_service.get_knowledge_chunks(session_id)
            
            if kb_chunks:
                kb_context = "\n\n".join(kb_chunks[:5])
                enhanced_message = f"""基于以下文档内容回答问题：

{kb_context}

用户问题：{message}"""
                yield from self.stream_chat(enhanced_message, session_id)
            else:
                yield from self.stream_chat(message, session_id)
        except Exception as e:
            logger.error(f"带文件流式聊天失败: {e}")
            yield f"抱歉，处理文件时出现错误: {str(e)}"
    
    def _save_session(self, session_id: str) -> None:
        """保存会话历史"""
        if session_id in self.session_memories:
            messages = self.session_memories[session_id]
            
            # 转换为字典格式
            msg_list = []
            for msg in messages:
                msg_type = msg.type
                msg_text = msg.content
                
                msg_list.append({
                    'type': msg_type,
                    'text': msg_text
                })
            
            history_service.save_session(session_id, msg_list)
    
    def clear_session(self, session_id: str) -> None:
        """清除会话"""
        if session_id in self.session_memories:
            del self.session_memories[session_id]


# 创建全局实例
chat_service = ChatService()
