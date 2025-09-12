import os
from pathlib import Path
import yaml

def read_yaml(file_path):
    if not os.path.exists(file_path):
        res = {}
    else:
        with open(file_path, 'r') as file:
            res = yaml.safe_load(file)
            if res is None:
                res = {}
    return res

def write_yaml(file_path, data: dict, update=True):
    cfg = read_yaml(file_path)
    with open(file_path, 'w') as file:
        if update:
            cfg.update(data)
        else:
            cfg = data
        yaml.dump(cfg, file)
        
ENV_FILE_NAME = ".hstool.yaml"
HOME_ENV_FILE = os.path.join(os.path.expanduser("~"), ENV_FILE_NAME)
WORK_ENV_FILE = os.path.join(os.getcwd(), ENV_FILE_NAME)


class Config:
    home_env = read_yaml(HOME_ENV_FILE) if os.path.exists(HOME_ENV_FILE) else {}
    work_env = read_yaml(WORK_ENV_FILE) if os.path.exists(WORK_ENV_FILE) else {}

    def __init__(self):
        self.update()
        
    def update(self):
        self.SQL = self.getenv("SQL", "sqlite:///sqlite.db")  # 'mysql+pymysql://root:密码@localhost:3306/数据库名?charset=utf8mb4'
        self.UPLOAD = Path(self.getenv("UPLOAD", "."))
        self.AUTHOR = self.getenv("AUTHOR", "Unknown")
        self.BLOGPATH = self.getenv("BLOGPATH", "posts")
        self.ZONE = "Asia/Shanghai"
    
    def set_config(self, **kwargs):
        file = WORK_ENV_FILE if os.path.exists(WORK_ENV_FILE) else HOME_ENV_FILE
        write_yaml(file, kwargs, update=True)
        
    @classmethod
    def getenv(self, key, default=None):
        if key in self.work_env:
            return self.work_env[key]
        elif key in self.home_env:
            return self.home_env[key]
        else:
            return os.getenv(key, default)

config = Config()
