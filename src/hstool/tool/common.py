import subprocess
import click 
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from typing import Union, Optional
from hstool.config import config


def is_vscode_installed() -> bool:
    """检查VS Code是否安装并已添加到系统PATH"""
    try:
        # 尝试运行 'code --version' 命令，成功则说明已安装
        subprocess.run(
            ['code', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 命令不存在或执行失败，说明未安装或未添加到PATH
        return False
    
def command(cmd, start_new_session=True) -> subprocess.CompletedProcess:
    """命令子进程"""
    # 尝试运行 'code --version' 命令，成功则说明已安装
    return subprocess.run(
        cmd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        start_new_session=start_new_session
    )

def add_options_from_dict(params_dict):
    """根据字典动态生成Click选项装饰器"""
    def decorator(func):
        # 遍历字典的key，为每个key创建一个--key选项
        for key in params_dict.keys():
            # 选项名格式：--key，帮助信息使用字典中的默认值
            func = click.option(
                f'--{key}',
                help=f'Dafault: {params_dict[key]}',
                default=None
            )(func)
        return func
    return decorator

def parse_date(date_input: Union[str, datetime, date, time]) -> Optional[datetime]:
    """
    增强型日期解析函数：
    - 若输入是datetime对象，直接返回
    - 若输入是date对象，转换为datetime（时间部分为00:00:00）
    - 若输入是time对象，返回None（无法单独转换为datetime）
    - 若输入是字符串，尝试多种格式自动解析
    
    Args:
        date_input: 待处理的输入（字符串、datetime、date或time对象）
    
    Returns:
        解析成功返回datetime对象，失败返回None
    """
    # 1. 处理已有的datetime对象
    if isinstance(date_input, datetime):
        return date_input
    
    # 2. 处理date对象（转换为datetime，时间部分为00:00:00）
    if isinstance(date_input, date):
        return datetime.combine(date_input, time.min)  # time.min 表示 00:00:00
    
    # 3. 处理time对象（单独的时间无法转换为datetime，返回None）
    if isinstance(date_input, time):
        return None
    
    # 4. 处理字符串类型（自动尝试多种格式）
    if isinstance(date_input, str):
        # 常见日期格式列表（可根据需求扩展）
        date_formats = [
            # 日期+时间格式
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
            "%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M",
            "%m-%d-%Y %H:%M:%S", "%m-%d-%Y %H:%M",
            "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M",
            "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
            # 仅日期格式
            "%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y",
            "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y",
            # 带文字的格式
            "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y"
        ]
        
        # 尝试每种格式解析
        for fmt in date_formats:
            try:
                return datetime.strptime(date_input, fmt).replace(tzinfo=ZoneInfo(config.ZONE))
            except ValueError:
                continue
    
    # 所有情况都不匹配
    return None
