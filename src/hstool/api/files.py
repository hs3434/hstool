from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional
# api/files.py
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import os
from hstool.config import config

# 创建该功能组的路由实例
router = APIRouter(
    prefix="/files",  # 该组路由的统一前缀
    tags=["文件管理"]  # 文档中分组显示的标签
)


def get_file_info(file_path: Path) -> dict:
    """获取文件的详细信息"""
    file_path = Path(file_path)
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "size": stat.st_size,  # 文件大小（字节）
        "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),  # 创建时间
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),  # 修改时间
        "path": str(file_path)
    }

def validate_file_path(filename: str, work_dir: Path):
    """验证文件路径，防止路径遍历攻击"""
    # 拼接用户目录和文件名（强制在用户目录内）
    file_path = work_dir / filename
    # 检查文件是否在用户目录内（防止 ../ 等路径遍历）
    if not file_path.resolve().startswith(work_dir.resolve()):
        raise HTTPException(status_code=403, detail="非法文件路径")
    return file_path

@router.post("/upload", summary="上传文件")
async def upload_file(
    file: UploadFile = File(..., description="要上传的本地文件"),
    overwrite: bool = Query(False, description="是否覆盖已存在的文件")
):
    """上传本地文件到服务器"""
    work_dir = config.UPLOAD
    file_path = validate_file_path(file.filename, work_dir)
    
    # 检查文件是否已存在
    if file_path.exists() and not overwrite:
        raise HTTPException(
            status_code=400,
            detail=f"文件 '{file.filename}' 已存在，若需覆盖请设置 overwrite=True"
        )
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "message": f"文件 '{file.filename}' 上传成功",
        "file_info": get_file_info(file_path)
    }


@router.get("/", summary="获取文件列表")
def get_file_list(
    suffix: Optional[str] = Query(None, description="按文件后缀过滤，如 'txt'、'pdf'"),
    sort_by: str = Query("created_at", description="排序字段：created_at / modified_at / size")
) -> List[dict]:
    """获取服务器上的所有文件列表（支持过滤和排序）"""
    # 获取所有文件
    work_dir = config.UPLOAD
    files = [f for f in work_dir.iterdir() if f.is_file()]
    
    # 按后缀过滤
    if suffix:
        files = [f for f in files if f.suffix.lower() == f".{suffix.lower()}"]
    
    # 排序
    if sort_by == "created_at":
        files.sort(key=lambda x: x.stat().st_ctime, reverse=True)  # 最新创建的在前
    elif sort_by == "modified_at":
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)  # 最新修改的在前
    elif sort_by == "size":
        files.sort(key=lambda x: x.stat().st_size, reverse=True)  # 从大到小
    else:
        raise HTTPException(status_code=400, detail="无效的排序字段")
    
    # 返回文件信息列表
    return [get_file_info(f) for f in files]


@router.get("/{filename}", summary="下载文件")
def download_file(filename: str):
    """下载指定文件"""
    work_dir = config.UPLOAD
    file_path = validate_file_path(filename, work_dir)
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"文件 '{filename}' 不存在")
    
    # 返回文件响应（自动处理下载）
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"  # 通用二进制类型
    )


@router.delete("/{filename}", summary="删除文件")
def delete_file(filename: str):
    """删除服务器上的指定文件"""
    work_dir = config.UPLOAD
    file_path = validate_file_path(filename, work_dir)
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"文件 '{filename}' 不存在")
    
    os.remove(file_path)
    return {"message": f"文件 '{filename}' 已成功删除"}

