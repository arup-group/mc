"""
Command line interface for MC.
"""
from pathlib import Path
import click
from typing import Tuple
from mc import build


def careful_write(config, write_path):
    if Path(write_path).exists():
        value = click.prompt(f'Are you sure you want to overwrite {write_path}? y/n', default='n')
        if value.lower() == 'y':
            config.write(Path(write_path))
    else:
        config.write(Path(write_path))


def string_to_tuple(string: str) -> Tuple[str]:
    if string:
        return tuple(string.split(','))


@click.group()
def cli():
    """
    Command line interface for MC.
    """
    pass


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('write_path', type=click.Path(writable=True))
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--show', '-p', is_flag=True, default=False)
def convert(
        read_path: Path,
        write_path: Path,
        debug: bool,
        show: bool
) -> None:
    """
    Read an existing config and write as xml or json.
    """
    config = build.Config(path=Path(read_path))
    if show:
        config.print()
    if debug:
        config.debug()
    careful_write(config, write_path)


@cli.command(name='gen')
@click.argument('config', type=click.Choice(list(build.config_map)))
@click.argument('write_path', type=click.Path(writable=True))
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--show', '-p', is_flag=True, default=False)
def generate_config(
        config: str,
        write_path: Path,
        debug: bool,
        show: bool
) -> None:
    """
    Generate a template config: empty|default|test.
    """
    config = build.config_map[config]()
    if show:
        config.print()
    if debug:
        config.debug()
    careful_write(config, write_path)


@cli.command(name='build')
@click.argument('write_path', type=click.Path(writable=True))
@click.option('--input_dir', '-i', type=click.Path(), default=Path('inputs'))
@click.option('--output_dir', '-o', type=click.Path(), default=Path('outputs'))
@click.option('--sample', '-%', type=float, default=0.1)
@click.option('--subpops', '-s', type=str, default='high_income,medium_income,low_income,freight')
@click.option('--modes', '-m', type=str, default='car,pt,walk,bike')
@click.option('--activities', '-a', type=str, default='home,work,education,other')
@click.option('--debug', '-d', is_flag=True, default=False)
@click.option('--show', '-p', is_flag=True, default=False)
def build_config(
        write_path: Path,
        input_dir: Path,
        output_dir: Path,
        sample: float,
        subpops: str,
        modes: str,
        activities: str,
        debug: bool,
        show: bool
) -> None:
    """
    Build a config with defined sub-pops, modes & activities.
    """
    print(write_path, input_dir, output_dir, sample, subpops, modes, activities)
    subpops = string_to_tuple(subpops)
    modes = string_to_tuple(modes)
    activities = string_to_tuple(activities)
    config = build.BuildConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        sample=sample,
        subpops=subpops,
        modes=modes,
        acts=activities
    )
    if show:
        config.print()
    if debug:
        config.debug()
    careful_write(config, write_path)


@cli.command()
@click.argument('read_path_a', type=click.Path(exists=True))
@click.argument('read_path_b', type=click.Path(exists=True))
def diff(
        read_path_a: Path,
        read_path_b: Path,
) -> None:
    """
    Simple diff two configs.
    """
    config_a = build.Config(path=Path(read_path_a))
    config_b = build.Config(path=Path(read_path_b))
    diffs = config_b.diff(config_a)
    for d in diffs:
        print(d)


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.option('--show', '-p', is_flag=True, default=False)
def debug(
        read_path: Path,
        show: bool
) -> None:
    """
    Debug a config.
    """
    config = build.Config(path=Path(read_path))
    if show:
        config.print()
    config.debug()


@cli.command(name='print')
@click.argument('read_path', type=click.Path(exists=True))
def print_config(
        read_path: Path,
) -> None:
    """
    Print a config to terminal.
    """
    config = build.Config(path=Path(read_path))
    config.print()
