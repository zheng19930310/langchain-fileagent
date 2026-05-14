"""
知识库API路由
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List
import os
import tempfile
from pathlib import Path

from app.services.knowledge_base import kb_service

router = APIRouter(prefix="/api/kb", tags=["knowledge-base"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Form(...)
):
    """上传文件到知识库
    
    Args:
        file: 上传的文件
        session_id: 会话ID
        
    Returns:
        上传结果
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名为空")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="sessionId 不能为空")
        
        # 保存临时文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # 上传到知识库
        result = kb_service.upload_file(session_id, temp_file_path, file.filename)
        
        # 清理临时文件
        os.remove(temp_file_path)
        os.rmdir(temp_dir)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def get_uploaded_files(session_id: str):
    """获取已上传的文件列表
    
    Args:
        session_id: 会话ID
        
    Returns:
        文件列表
    """
    try:
        files = kb_service.get_uploaded_files(session_id)
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats(session_id: str):
    """获取知识库统计信息
    
    Args:
        session_id: 会话ID
        
    Returns:
        统计信息
    """
    try:
        return {
            "hasKB": kb_service.has_knowledge_base(session_id),
            "chunkCount": kb_service.get_chunk_count(session_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """清除会话的知识库
    
    Args:
        session_id: 会话ID
        
    Returns:
        清除结果
    """
    try:
        kb_service.clear_session(session_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/all")
async def clear_all():
    """清除所有知识库
    
    Returns:
        清除结果
    """
    try:
        kb_service.clear_all()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
