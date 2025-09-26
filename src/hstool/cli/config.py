import click
from ..tool.common import add_options_from_dict
from ..config import config as cfg


@click.group()
def config():
    """config tool"""
    
@config.command()
@add_options_from_dict(vars(cfg))
@click.pass_context
def set(ctx: click.Context, **kwargs: str| None):
    """set config value"""
    k_dic = {k.lower():k for k in vars(cfg)}
    res: dict[str, str] = {}
    for k, v in kwargs.items():
        if v is not None and k in k_dic:
            res[k_dic[k]] = v
    if not res:
        click.echo(ctx.get_help())
    else:
        cfg.set_config(**res)
    
@config.command()
@click.argument('key')
def get(key: str):
    """get config value"""
    if key not in vars(cfg):
        raise click.BadParameter(f"{key} not found", param_hint="key")
    else:
        click.echo(vars(cfg).get(key))

@config.command()
def list():
    """list all config"""
    for key in vars(cfg):
        click.echo(f"{key}: {vars(cfg).get(key)}")