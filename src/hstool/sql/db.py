from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import config

Base = declarative_base()

from .blog import *

engine = create_engine(config.SQL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def Session():
    db = SessionLocal()  # 创建新会话
    try:
        yield db  # 提供会话给业务逻辑
    finally:
        db.close()  # 无论是否报错，都关闭会话