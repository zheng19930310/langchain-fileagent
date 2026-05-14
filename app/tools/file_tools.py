"""
文件操作工具 - 使用Langchain的Tool装饰器
"""
from langchain.tools import tool
import os
from pathlib import Path
from typing import Optional
from loguru import logger


@tool
def list_disk() -> str:
    """列出所有磁盘驱动器及容量信息（无参数）"""
    try:
        import psutil
        partitions = psutil.disk_partitions()
        result = "磁盘驱动器列表:\n"
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                free_gb = usage.free / (1024**3)
                
                result += f"  {partition.mountpoint} - 总容量: {total_gb:.2f} GB, "
                result += f"已用: {used_gb:.2f} GB, 可用: {free_gb:.2f} GB\n"
            except Exception as e:
                result += f"  {partition.mountpoint} - 无法获取信息: {str(e)}\n"
        
        return result
    except ImportError:
        # 如果没有psutil，使用简单方法
        if os.name == 'nt':  # Windows
            import string
            result = "磁盘驱动器列表:\n"
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    try:
                        import shutil
                        total, used, free = shutil.disk_usage(drive)
                        total_gb = total / (1024**3)
                        used_gb = used / (1024**3)
                        free_gb = free / (1024**3)
                        result += f"  {drive} - 总容量: {total_gb:.2f} GB, "
                        result += f"已用: {used_gb:.2f} GB, 可用: {free_gb:.2f} GB\n"
                    except:
                        result += f"  {drive}\n"
            return result
        else:
            return "请安装psutil库以获取磁盘信息: pip install psutil"
    except Exception as e:
        logger.error(f"获取磁盘信息失败: {e}")
        return f"获取磁盘信息失败: {str(e)}"


@tool
def list_files(directory_path: str, **kwargs) -> str:
    """列出目录内容
    
    Args:
        directory_path: 目录路径
    """
    try:
        path = Path(directory_path)
        
        if not path.exists():
            return f"目录不存在: {directory_path}"
        
        if not path.is_dir():
            return f"路径不是目录: {directory_path}"
        
        items = list(path.iterdir())
        items.sort(key=lambda x: x.name.lower())
        
        result = f"目录内容 ({directory_path}):\n"
        for item in items:
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            size = item.stat().st_size if item.is_file() else 0
            result += f"  {item_type} {item.name:<40} {size} bytes\n"
        
        return result
    except Exception as e:
        logger.error(f"列出目录失败: {directory_path}, 错误: {e}")
        return f"列出目录失败: {str(e)}"


@tool
def get_file_size(file_path: str, **kwargs) -> str:
    """获取文件或目录大小
    
    Args:
        file_path: 文件路径
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"文件/目录不存在: {file_path}"
        
        if path.is_file():
            size = path.stat().st_size
        else:
            # 计算目录大小
            size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        
        # 格式化大小
        if size >= 1024**3:
            size_str = f"{size / (1024**3):.2f} GB"
        elif size >= 1024**2:
            size_str = f"{size / (1024**2):.2f} MB"
        elif size >= 1024:
            size_str = f"{size / 1024:.2f} KB"
        else:
            size_str = f"{size} bytes"
        
        return f"{file_path} - 大小: {size_str} ({size} bytes)"
    except Exception as e:
        logger.error(f"获取文件大小失败: {file_path}, 错误: {e}")
        return f"获取文件大小失败: {str(e)}"


@tool
def read_file(file_path: str, max_length: int = None, **kwargs) -> str:
    """读取文件内容
    
    Args:
        file_path: 文件路径
        max_length: 最大读取长度，可选
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"文件不存在: {file_path}"
        
        if not path.is_file():
            return f"路径不是文件: {file_path}"
        
        # 读取文件内容
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if max_length and len(content) > max_length:
            content = content[:max_length] + f"\n... (内容被截断，总长度: {len(content)} 字符)"
        
        return f"文件内容 ({file_path}):\n{content}"
    except Exception as e:
        logger.error(f"读取文件失败: {file_path}, 错误: {e}")
        return f"读取文件失败: {str(e)}"


@tool
def create_file(file_path: str, content: str = "", **kwargs) -> str:
    """创建新文件
    
    Args:
        file_path: 文件路径
        content: 文件内容
    """
    try:
        path = Path(file_path)
        
        # 创建父目录
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"文件创建成功: {file_path}"
    except Exception as e:
        logger.error(f"创建文件失败: {file_path}, 错误: {e}")
        return f"创建文件失败: {str(e)}"


@tool
def edit_file(file_path: str, new_content: str = "", **kwargs) -> str:
    """编辑文件内容
    
    Args:
        file_path: 文件路径
        new_content: 新的文件内容
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"文件不存在: {file_path}"
        
        # 写入新内容
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return f"文件编辑成功: {file_path}"
    except Exception as e:
        logger.error(f"编辑文件失败: {file_path}, 错误: {e}")
        return f"编辑文件失败: {str(e)}"


@tool
def delete_file(file_path: str, **kwargs) -> str:
    """删除文件或目录
    
    Args:
        file_path: 文件路径
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"文件/目录不存在: {file_path}"
        
        if path.is_file():
            path.unlink()
        else:
            # 递归删除目录
            import shutil
            shutil.rmtree(path)
        
        return f"删除成功: {file_path}"
    except Exception as e:
        logger.error(f"删除文件失败: {file_path}, 错误: {e}")
        return f"删除文件失败: {str(e)}"


# 导出所有工具
file_tools = [
    list_disk,
    list_files,
    get_file_size,
    read_file,
    create_file,
    edit_file,
    delete_file
]
