from __future__ import annotations
import os
from pydantic import BaseModel
from pathlib import Path
from pydantic import BaseModel, field_validator
from typing import Dict, Any
        
ENV_FILE_NAME = ".hstool.yaml"
HOME_ENV_FILE = os.path.join(os.path.expanduser("~"), ENV_FILE_NAME)
WORK_ENV_FILE = os.path.join(os.getcwd(), ENV_FILE_NAME)


# 假设存在这两个函数（读取/写入YAML）
def read_yaml(file_path: str| Path) -> Dict[str, Any]:
    """读取YAML文件并返回字典"""
    import yaml
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}

def write_yaml(file_path: str| Path, data: Dict[str, Any], update: bool = True) -> None:
    """写入YAML文件，支持更新模式"""
    import yaml
    if update and os.path.exists(file_path):
        existing = read_yaml(file_path)
        existing.update(data)
        data = existing
    with open(file_path, 'w') as f:
        yaml.safe_dump(data, f)

class Config(BaseModel):
    # 1. 声明配置源（使用pydantic字段，带类型注解）
    home_env: Dict[str, Any] = {}
    work_env: Dict[str, Any] = {}

    # 2. 核心配置项（作为pydantic字段，支持类型校验和默认值）
    SQL: str = "sqlite:///sqlite.db"
    UPLOAD: Path = Path(".")
    AUTHOR: str = "Unknown"
    BLOGPATH: str = "posts"
    ZONE: str = "Asia/Shanghai"

    def __init__(self,** data: Any):
        # 先加载配置文件（在pydantic初始化前执行）
        home_env = read_yaml(HOME_ENV_FILE) if os.path.exists(HOME_ENV_FILE) else {}
        work_env = read_yaml(WORK_ENV_FILE) if os.path.exists(WORK_ENV_FILE) else {}
        
        # 调用pydantic的初始化方法，传入基础配置
        super().__init__(home_env=home_env, work_env=work_env, **data)
        
        # 从配置源更新核心配置项
        self.update_from_envs()

    def update_from_envs(self) -> None:
        """从home_env/work_env/环境变量更新核心配置"""
        # 遍历所有核心配置字段，用getenv更新值
        for field_name in self.__class__.model_fields:
            if field_name in ["home_env", "work_env"]:
                continue  # 跳过配置源本身
            # 用当前值作为默认，从配置源获取新值
            current_value = getattr(self, field_name)
            new_value = self.getenv(field_name, str(current_value))
            # 转换为字段对应的类型（如Path）
            setattr(self, field_name, self._convert_value(field_name, new_value))

    def _convert_value(self, field_name: str, value: str) -> Any:
        """将字符串值转换为字段声明的类型（如Path）"""
        field_type = self.__class__.model_fields[field_name].annotation
        if field_type is Path:
            return Path(value)
        return value  # 其他类型暂时直接返回（可扩展）

    def getenv(self, key: str, default: str = "") -> str:
        """优先从work_env/home_env获取，最后 fallback 到环境变量"""
        if key in self.work_env:
            return str(self.work_env[key])  # 确保返回字符串，统一后续转换
        elif key in self.home_env:
            return str(self.home_env[key])
        else:
            return os.getenv(key, default)

    def set_config(self,** kwargs: str) -> None:
        """将配置写入YAML文件（优先工作目录）"""
        file = WORK_ENV_FILE if os.path.exists(WORK_ENV_FILE) else HOME_ENV_FILE
        write_yaml(file, kwargs, update=True)
        # 写入后更新内存中的配置
        self.work_env.update(kwargs) if os.path.exists(WORK_ENV_FILE) else self.home_env.update(kwargs)
        self.update_from_envs()  # 刷新核心配置

    @field_validator('UPLOAD')
    def ensure_upload_dir_exists(cls, v: Path) -> Path:
        """自动创建UPLOAD目录（pydantic验证器）"""
        v.mkdir(parents=True, exist_ok=True)
        return v

config = Config()
