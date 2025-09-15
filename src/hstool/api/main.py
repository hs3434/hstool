import os
import importlib
import logging
from fastapi import FastAPI

logger = logging.getLogger("uvicorn")
# 只创建一个 app 实例
app = FastAPI(title="Welcome to my API!")

for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and file not in ("__init__.py", "main.py"):
        module_name = file.split('.')[0]
        module_path = f"hstool.api.{module_name}"
        try:
            module_obj = importlib.import_module(module_path)
            if hasattr(module_obj, "router"):
                app.include_router(module_obj.router)
                print(f"已加载路由模块：{module_path}")
            else:
                print(f"模块 {module_path} 不含 router，已跳过")
        except Exception as e:
            print(f"加载模块 {module_path} 失败：{e}")

logger.info(f"已注册的路由: {[route.path for route in app.routes]}")  # 打印所有注册的路由
# 主页面路由（可选）
@app.get("/")
async def root():
    return {"message": "Welcome to my API!"}