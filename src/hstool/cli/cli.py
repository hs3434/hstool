from pathlib import Path

import os
import click
import importlib
from ..tool.common import command

@click.group()
def cli():
    """Command-line toolset for hstool.\n
    To get tap completion:
    
    hstool init-completion
    """
    pass 


@cli.command()
@click.option("--host", "-h", default="127.0.0.1")
@click.option("--port", "-p", default=8000)
@click.option("--reload", is_flag=True)
def api(host: str, port: int, reload: bool):
    """启动api服务"""
    import uvicorn
    uvicorn.run(
        app='hstool.api.main:app',
        host=host ,
        port=port,
        reload=reload
    )
    
    
@cli.command()
def init_sql():
    """初始化数据库"""
    from ..sql.db import engine, Base
    Base.metadata.create_all(engine)

@cli.command()
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"]),
    help="指定终端类型"
)
def init_completion(shell: str):
    """配置自动补全"""
    if not shell:
        # 自动检测终端类型（简单实现）
        shell = os.path.basename(os.environ.get("SHELL", ""))
        if shell not in ["bash", "zsh", "fish"]:
            click.echo("暂时只支持 bash, zsh, fish")
    
    p = command([f'_HSTOOL_COMPLETE={shell}_source hstool'])
    sh = str(p.stdout.strip())
    if shell == "fish":
        path = Path("~/.config/fish/completions/hstool.fish")
        with open(path, "w") as f:
            f.write(sh)
    else:
        path = os.path.join(os.path.expanduser("~"), ".hstool-complete.sh")
        with open(path, "w") as f:
            f.write(sh)
        with open(os.path.join(os.path.expanduser("~"), f".{shell}rc"), "a+") as f:
            ss = f.read()
            cmd = f"source {path}"
            if cmd not in ss:
                f.write(cmd+"\n")
        print(f"自动补全已配置，重启终端生效，或者运行：\n {cmd}")

def auto_load_commands():
    """自动遍历当前目录下的所有模块，导入子命令并注册到主cli"""
    current_dir = Path(__file__).parent
    for file in current_dir.glob('*.py'):
        name = file.name[:-3]
        if name == '__init__' or name == "cli":
            continue
        module_name = f'hstool.cli.{name}'
        
        try:
            module = importlib.import_module(module_name)
            cmd_obj = getattr(module, name)
            cli.add_command(cmd_obj)
        
        except ImportError as e:
            click.secho(f"警告：导入模块 {module_name} 失败: {e}", fg='yellow')
        except Exception as e:
            click.secho(f"处理模块 {module_name} 时出错: {e}", fg='red')

auto_load_commands()

if __name__ == "__main__":
    cli()