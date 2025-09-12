import frontmatter
from pathlib import Path
from typing import Dict, Optional


def add_frontmatter(
    file_path: str,
    metadata: Dict[str, str],
    overwrite: bool = False
) -> bool:
    """
    向 Markdown 文件添加 Frontmatter 元数据
    
    参数:
        md_file_path: Markdown 文件路径
        metadata: 要添加的元数据（键值对）
        overwrite: 若已存在 Frontmatter，是否覆盖（False 则合并）
    
    返回:
        是否成功添加/更新
    """
    Path(file_path).parent.mkdir(parents=True)
    
    with open(file_path, 'w+', encoding='utf-8') as f:
        post = frontmatter.load(f)
        if overwrite:
            post.metadata = metadata 
        else:
            post.metadata.update(metadata) 
        f.write(frontmatter.dumps(post))
        f.write(post.content)
    return True

def get_frontmatter(md_file_path: str) -> Optional[Dict]:
    """解析 Markdown 文件的 Frontmatter 元数据"""
    file_path = Path(md_file_path)
    if not file_path.exists():
        print(f"错误：文件 {md_file_path} 不存在")
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    return dict(post.metadata)  # 返回元数据字典

def update_frontmatter(
    md_file_path: str,
    new_metadata: Dict[str, str]
) -> bool:
    """更新 Frontmatter 中的部分元数据（不覆盖现有其他字段）"""
    return add_frontmatter(md_file_path, new_metadata, overwrite=False)

def rename_frontmatter(file_path, **kwargs):
    """重命名 Frontmatter 中的字段"""
    if not Path(file_path).exists():
        print(f"错误：文件 {file_path} 不存在")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        new_metadata = {}
        for key in post.metadata:
            if key in kwargs:
                new_metadata[kwargs[key]] = post.metadata[key]
            else:
                new_metadata[key] = post.metadata[key]
        post.metadata = new_metadata
        f.write(frontmatter.dumps(post))
        f.write(post.content)
    return True