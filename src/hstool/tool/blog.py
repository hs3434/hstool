from __future__ import annotations
import os
import frontmatter  # type: ignore # 解析Markdown元数据（需安装：pip install python-frontmatter）
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, TypedDict, NotRequired, cast
from sqlalchemy.orm.session import Session as SQLASession
from ..sql.blog import Blog, Tag, Category
from ..sql.db import Session
from .common import parse_date

class PostFront(TypedDict):
    title: str
    slug: NotRequired[str]
    create: NotRequired[str]
    update: NotRequired[str]
    tags: NotRequired[List[str]]
    categories: NotRequired[List[str]]
    

def parse_markdown_file(file_path: str | Path, slug: str| None=None) -> Dict[str, Any]:
    """解析Markdown文件，提取元数据和内容"""
    post = frontmatter.load(str(file_path))
    metadata = cast(PostFront, post.metadata)
    return {
        "slug": slug or metadata.get("slug", None),
        "title": metadata.get("title", "Untitled"),
        "create": parse_date(metadata.get("create", datetime.now())),
        "update": parse_date(metadata.get("update", datetime.now())),
        "category": metadata.get("category", "Unclassified"),
        "tags": metadata.get("tags", None),
        "content": post.content
    }

def import_blog(path: str | Path, slug: str | None=None):
    files = os.listdir(path)
    session = next(Session())
    for file in files:
        if file.endswith(".md"):
            parsed_data = parse_markdown_file(os.path.join(path, file), slug)
            need = {"slug", "title", "create", "update", "content"}
            need_date = {k: v for k, v in parsed_data.items() if k in need}
            new_blog = merge_blog_by_slug(session, need_date)
            
            tag_names = parsed_data.get("tags", [])  
            for tag_name in tag_names:
                # 先查询标签是否已存在（避免重复创建）
                existing_tag = session.query(Tag).filter(Tag.name == tag_name).first()
                if existing_tag:
                    # 标签已存在，直接关联
                    new_blog.tags.append(existing_tag)
                else:
                    # 标签不存在，创建新Tag实例并关联
                    new_tag = Tag(name=tag_name)
                    session.add(new_tag)  # 标记Tag为待插入
                    new_blog.tags.append(new_tag)  # 关联到Blog
            
            category = parsed_data.get("category", None)  
            if category:
                current_category = find_multilevel_category(session, category, create=True)
                new_blog.category = current_category
            session.commit()
            

            
def init_blog(path: str| Path):
    blogs = os.listdir(path)
    for blog in blogs:
        import_blog(os.path.join(path, blog), slug=blog)

def find_multilevel_category(
    session: SQLASession,
    category_levels: List[str],
    create: bool = True
) -> Optional[Category]:
    """
    根据多级分类列表查找最终的子分类实例
    
    Args:
        session: 数据库会话
        category_levels: 多级分类列表（如 ["技术", "后端", "Python"]）
    
    Returns:
        找到的最末级分类实例，未找到则返回None
    """
    if not category_levels:  # 空列表直接返回
        return None
    if isinstance(category_levels, str):  # 字符串类型转换为列表
        category_levels = [category_levels]
        
    # 1. 从顶级分类开始查找（parent_id 为 None）
    current_category = session.query(Category).filter(
        Category.name == category_levels[0],
        Category.parent_id.is_(None)  # 顶级分类的 parent_id 为 None
    ).first()
    
    if not current_category:
        if create:
            current_category = Category(name=category_levels[0])  # 创建顶级分类
            session.add(current_category)
            session.commit()
            session.refresh(current_category)
        else:
            return None 
    
    # 2. 从次级分类开始查找
    for level_name in category_levels[1:]:  # 从第二个元素开始遍历
        id = current_category.id
        current_category = session.query(Category).filter(
            Category.name == level_name,
            Category.parent_id == id  # 父分类ID为当前分类的ID
        ).first()
        
        if not current_category:
            if create:
                current_category = Category(name=level_name, parent_id=id)  # 创建顶级分类
                session.add(current_category)
                session.commit()
                session.refresh(current_category)
            else:
                return None 

    return current_category

def merge_blog_by_slug(session: SQLASession, blog_data: Dict[str, Any]) -> Blog:
    """
    根据slug合并更新博客：
    - 若slug已存在，更新博客内容
    - 若slug不存在，创建新博客
    
    Args:
        session: 数据库会话
        blog_data: 博客数据（需包含slug，其他字段如title、content等）
    
    Returns:
        处理后的博客实例（新建或更新后的）
    """
    # 必须包含slug字段
    if "slug" not in blog_data:
        raise ValueError("blog_data 必须包含 'slug' 字段")
    
    slug = blog_data["slug"]
    # 查找是否存在相同slug的博客
    existing_blog = session.query(Blog).filter(Blog.slug == slug).first()
    
    if existing_blog:
        # 1. 存在则更新（合并数据）
        # 更新字段（仅更新提供的字段，保留未提供的原有字段）
        for key, value in blog_data.items():
            if hasattr(existing_blog, key):  # 确保字段存在于模型中
                setattr(existing_blog, key, value)
        session.commit()
        return existing_blog
    else:
        # 2. 不存在则创建新博客
        new_blog = Blog(** blog_data)
        session.add(new_blog)
        session.commit()
        session.refresh(new_blog)
        return new_blog