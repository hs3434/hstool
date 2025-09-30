
import click
import os
import shutil
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict
from inspect import cleandoc
from ..tool.common import is_vscode_installed, command
from ..config import config


@click.group()
def blog():
    """blog tool"""
    
    
@blog.command()
@click.argument("slug")
@click.argument("title", required=False, default=None)
def new(slug: str, title: str):
    """Generate a blog post with slug and title."""
    slugs = os.listdir(config.BLOGPATH)
    if slug in slugs:
        raise click.ClickException("Blog with slug %s already exists." % slug)
    if not title:
        title = slug
    path = Path(config.BLOGPATH, slug, slug+".md").resolve()
    metadata: Dict[str, object]={
        "title": title,
        "author": config.AUTHOR,
        "tags": [],
        "category": "Unclassified",
        "create": datetime.now(ZoneInfo(config.ZONE)).strftime("%d-%m-%Y %H:%M"),
        "update": datetime.now(ZoneInfo(config.ZONE)).strftime("%d-%m-%Y %H:%M")
    }
    from ..tool.frontmatter import add_frontmatter
    add_frontmatter(path, metadata)
    if is_vscode_installed():
        command(["code", str(path)])


@blog.command()
@click.argument("path", required=False, default=None)
def init(path: str):
    """
    导入本地目录的博客到数据库
    
    \b
    目录结构如下所示:
        posts/
        ├── 240619
        │   └── 240619.md
        ├── 240620
        │   └── 240620.md
        ├── 2406202
        │   └── 2406202.md
    """
    if not path:
        path = config.BLOGPATH
    from ..tool.blog import init_blog
    init_blog(path)

@blog.command()
@click.argument("path", required=False, default=None)
def fun1(path: str):
    if not path:
        path2 = Path(config.BLOGPATH)
    else:
        path2 = Path(path)
    for file in path2.glob("*.md"):
        name = file.name[:-3]
        dir = Path(path, name)
        if dir.exists():
            if dir.is_dir():
                shutil.move(file, dir)
            else:
                print(f"{dir} is not a directory")
        else:
            os.mkdir(dir)
            shutil.move(file, dir)

@blog.group()
def front():
    """Modify frontmatter information"""


@front.command()
@click.argument("name")
@click.argument("value")
def rename(name: str, value: str):
    from ..tool.frontmatter import rename_frontmatter
    for file in Path(config.BLOGPATH).glob("*/*.md"):
        rename_frontmatter(file, **{name: value})