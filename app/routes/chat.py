"""
聊天API路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json
import tempfile
import os

from app.models.schemas import ChatRequest, SessionInfo, MessageHistory
from app.services.chat_service import chat_service
from app.services.chat_history import history_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(request: ChatRequest):
    """非流式聊天接口
    
    Args:
        request: 聊天请求
        
    Returns:
        AI回复
    """
    try:
        # 生成会话ID
        session_id = request.sessionId
        if not session_id:
            session_id = history_service.generate_session_id()
        
        # 处理带文件的聊天
        if request.filePaths and len(request.filePaths) > 0:
            response = chat_service.chat_with_files(
                request.message,
                request.filePaths,
                request.fileNames or [],
                session_id
            )
        else:
            response = chat_service.chat(request.message, session_id)
        
        return {"response": response, "sessionId": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/with-files")
async def chat_with_files(
    message: str = Form(...),
    sessionId: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """带文件的聊天接口
    
    Args:
        message: 用户消息
        sessionId: 会话ID
        files: 上传的文件列表
        
    Returns:
        AI回复
    """
    try:
        if not sessionId:
            sessionId = history_service.generate_session_id()
        
        # 保存临时文件
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        file_names = []
        
        for file in files:
            if not file.filename:
                continue
            
            temp_file_path = os.path.join(temp_dir, file.filename)
            with open(temp_file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            file_paths.append(temp_file_path)
            file_names.append(file.filename)
        
        # 调用带文件的聊天服务
        response = chat_service.chat_with_files(
            message,
            file_paths,
            file_names,
            sessionId
        )
        
        # 清理临时文件
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except:
                pass
        
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        return {"response": response, "sessionId": sessionId}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_chat(request: ChatRequest):
    """流式聊天接口
    
    Args:
        request: 聊天请求
        
    Returns:
        SSE流式响应
    """
    try:
        # 生成会话ID
        session_id = request.sessionId
        if not session_id:
            session_id = history_service.generate_session_id()
        
        # 获取流式生成器
        if request.filePaths and len(request.filePaths) > 0:
            stream_generator = chat_service.stream_chat_with_files(
                request.message,
                request.filePaths,
                request.fileNames or [],
                session_id
            )
        else:
            stream_generator = chat_service.stream_chat(request.message, session_id)
        
        # 返回SSE流
        async def event_stream():
            for chunk in stream_generator:
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream;charset=UTF-8"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """列出所有会话
    
    Returns:
        会话信息列表
    """
    try:
        return history_service.list_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}", response_model=List[MessageHistory])
async def get_session(session_id: str):
    """获取会话详情
    
    Args:
        session_id: 会话ID
        
    Returns:
        消息历史列表
    """
    try:
        messages = history_service.load_session(session_id)
        return [MessageHistory(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """删除会话
    
    Args:
        session_id: 会话ID
        
    Returns:
        删除结果
    """
    try:
        success = history_service.delete_session(session_id)
        chat_service.clear_session(session_id)
        
        if success:
            return {"message": "删除成功"}
        else:
            return {"message": "删除失败"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions")
async def clear_all_sessions():
    """清除所有会话
    
    Returns:
        清除结果
    """
    try:
        history_service.clear_all()
        return {"message": "所有历史记录已清除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
