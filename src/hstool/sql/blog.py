from __future__ import annotations
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Connection
from sqlalchemy.orm import relationship
from sqlalchemy.event import listens_for
from datetime import datetime
from typing import Dict, Any
from .db import Base
    
class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String(50), nullable=False) 

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String(50), nullable=False)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)  # 可选：多级分类的父分类ID


    # 可选：多级分类的自关联（1个父分类可包含多个子分类）
    children = relationship("Category", back_populates="parent", remote_side=[id])
    parent = relationship("Category", back_populates="children")

# 监听 Category 表的创建事件，自动插入默认分类
@listens_for(Category.__table__, 'after_create')
def insert_default_category(
    target: Table, 
    connection: Connection, 
    **kwargs: Dict[str, Any]
) -> None:
    """监听Category表的创建事件，自动插入默认分类"""
    connection.execute(target.insert().values(id=1, name="Unclassified"))

class Blog(Base):
    __tablename__ = 'blog'

    id = Column(Integer, primary_key=True, autoincrement=True)  
    title = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    create = Column(DateTime, default=datetime.now)
    update = Column(DateTime, default=datetime.now) 
    category_id = Column(Integer, ForeignKey('category.id', ondelete='RESTRICT'), default=1)
    content = Column(Text, nullable=False) 

tag_blog = Table(
    'tag_blog', 
    Base.metadata,
    Column('blog_id', Integer, ForeignKey('blog.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True)
)


Tag.blogs = relationship(
        'Blog',
        secondary=tag_blog,
        back_populates='tags'
    )

Category.blogs = relationship(
        "Blog",
        back_populates="category"
    )

Blog.category = relationship('Category', back_populates='blogs')
Blog.tags = relationship(
        'Tag',
        secondary=tag_blog,
        back_populates='blogs'
    )
