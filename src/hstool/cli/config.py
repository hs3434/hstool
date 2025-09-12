import click
import os
from pathlib import Path
from hstool.tool.common import add_options_from_dict
from hstool.config import config as cfg


@click.group()
def config():
    """config tool"""
    
@config.command()
@add_options_from_dict(vars(cfg))
@click.pass_context
def set(ctx, **kwargs):
    """set config value"""
    k_dic = {k.lower():k for k in vars(cfg)}
    res = {}
    for k, v in kwargs.items():
        if v is None:
            continue
        res.update({k_dic.get(k.lower()):v})
    if not res:
        click.echo(ctx.get_help())
    else:
        cfg.set_config(**res)
    
@config.command()
@click.argument('key')
def get(key):
    """get config value"""
    if key not in vars(cfg):
        raise click.echo(f"{key} not found", color='red')
    else:
        click.echo(vars(cfg).get(key))

@config.command()
def list():
    """list all config"""
    for key in vars(cfg):
        click.echo(f"{key}: {vars(cfg).get(key)}")