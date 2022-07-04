"""
Command line interface for MC.
"""
from pathlib import Path
from typing import Tuple
import click
import logging
from mc.autostep import autostep_config
from mc.build import Config, BuildConfig, BaseConfig, CONFIG_MAP
from mc.fill import match_replace
from mc.fill import param_replace
from mc.step import step_config


@click.group()
def cli():
    """
    Command line interface for MC.
    """


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('write_path', type=click.Path(writable=True))
@click.argument('overrides', nargs=-1)
def step(
        read_path: Path,
        write_path: Path,
        overrides
) -> None:
    """
    Read config, apply overrides and write out.
    """
    step_config(read_path, write_path, overrides)


@cli.command()
@click.argument('sim_root', type=click.Path(exists=False))
@click.argument('seed_matsim_config_path', type=click.Path(exists=True))
@click.argument('start_index', type=str)
@click.argument('total_iterations', type=str)
@click.argument('step', type=str)
@click.argument('biteration_matsim_config_path', type=click.Path(writable=True))
@click.argument('overrides', nargs=-1)
def autostep(
        sim_root: Path,
        seed_matsim_config_path: Path,
        start_index: str,
        total_iterations: str,
        step: str,
        biteration_matsim_config_path: Path,
        overrides: tuple
) -> None:
    """
    Read config, apply overrides and write out.
    """
    autostep_config(
        sim_root=sim_root,
        seed_matsim_config_path=seed_matsim_config_path,
        start_index=start_index,
        total_iterations=total_iterations,
        step=step,
        biteration_matsim_config_path=biteration_matsim_config_path,
        overrides=overrides
    )


# For backwards compat - deprecated by `match_replace` below
@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('write_path', type=click.Path(writable=True))
@click.argument('overrides', nargs=-1)
def fill(
        read_path: Path,
        write_path: Path,
        overrides
) -> None:
    """
    Read a wildcarded config, apply overrides and write.
    """
    logging.warning("`fill` is deprecated, use `matchreplace` instead")
    match_replace(read_path, write_path, overrides)


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('write_path', type=click.Path(writable=True))
@click.argument('overrides', nargs=-1)
def matchreplace(
        read_path: Path,
        write_path: Path,
        overrides
) -> None:
    """
    Read wildcarded config, apply overrides and write.
    """
    match_replace(read_path, write_path, overrides)


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('write_path', type=click.Path(writable=True))
@click.argument('overrides', nargs=-1)
def paramreplace(
        read_path: Path,
        write_path: Path,
        overrides
) -> None:
    """
    Read config, apply overrides and write out.
    E.g.
    ```
    mc paramreplace ./qux.xml ./quxo.xml 'inputPlansFile' '/my/path/to/plans.xml'
    'inputNetworkFile' '/my/path/to/network.xml' 'randomSeed' '31415926'
    ```
    reads input file `qux.xml` updates the fields `inputPlansFile`, `inputNetworkFile',
     and `randomSeed` and writes to the file `quxo.xml`.
    Note: All instances or the parameter will be updated.
    """
    param_replace(read_path, write_path, overrides)


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('write_path', type=click.Path(writable=True))
@click.option('--debugger', '-d', is_flag=True, default=False, show_default=True)
@click.option('--show', '-p', is_flag=True, default=False, show_default=True)
def convert(
        read_path: Path,
        write_path: Path,
        debugger: bool,
        show: bool
) -> None:
    """
    Read an existing config and write as xml or json.
    """
    config = Config(path=Path(read_path))
    if show:
        config.summary()
    if debugger:
        config.debug()
    careful_write(config, write_path)


@cli.command(name='gen')
@click.argument('config', type=click.Choice(list(CONFIG_MAP)))
@click.argument('write_path', type=click.Path(writable=True))
@click.option('--debugger', '-d', is_flag=True, default=False, show_default=True)
@click.option('--show', '-p', is_flag=True, default=False, show_default=True)
def generate_config(
        config: str,
        write_path: Path,
        debugger: bool,
        show: bool
) -> None:
    """
    Generate a template config: empty|default|test.
    """
    config = CONFIG_MAP[config]()
    if show:
        config.summary()
    if debugger:
        config.debug()
    careful_write(config, write_path)


@cli.command(name='build')
@click.argument('write_path', type=click.Path(writable=True))
@click.option('--input_dir', '-i', type=click.Path(), default=Path('inputs'), show_default=True)
@click.option('--output_dir', '-o', type=click.Path(), default=Path('outputs'), show_default=True)
@click.option('--sample', '-%', type=float, default=0.1, show_default=True)
@click.option('--epsg', '-e', type=int, default=27700, show_default=True)
@click.option('--subpops', '-s', type=str, default='high_income,medium_income,low_income,freight', show_default=True)
@click.option('--modes', '-m', type=str, default='car,pt,walk,bike', show_default=True)
@click.option('--activities', '-a', type=str, default='home,work,education,other', show_default=True)
@click.option('--debugger', '-d', is_flag=True, default=False, show_default=True)
@click.option('--show', '-p', is_flag=True, default=False, show_default=True)
def build_config(
        write_path: Path,
        input_dir: Path,
        output_dir: Path,
        sample: float,
        epsg: int,
        subpops: str,
        modes: str,
        activities: str,
        debugger: bool,
        show: bool
) -> None:
    """
    Build a config with defined sub-pops, modes & activities.
    """
    if isinstance(write_path, str):
        write_path = Path(write_path)
    if isinstance(input_dir, str):
        input_dir = Path(input_dir)
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    subpops = string_to_tuple(subpops)
    modes = string_to_tuple(modes)
    activities = string_to_tuple(activities)
    config = BuildConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        sample=sample,
        epsg=epsg,
        subpops=subpops,
        modes=modes,
        acts=activities
    )
    if show:
        config.summary()
    if debugger:
        config.debug()
    careful_write(config, write_path)


@cli.command(name='diff')
@click.argument('read_path_a', type=click.Path(exists=True))
@click.argument('read_path_b', type=click.Path(exists=True))
def difference(
        read_path_a: Path,
        read_path_b: Path,
) -> None:
    """
    Simple diff two configs.
    """
    config_a = Config(path=Path(read_path_a))
    config_b = Config(path=Path(read_path_b))
    diffs = config_b.diff(config_a)
    for diff in diffs:
        print(diff)


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.option('--debug', '-d', is_flag=True, default=False, show_default=True)
def summary(
        read_path: Path,
        debug: bool
) -> None:
    """
    Summarise a config.
    """
    config = Config(path=Path(read_path))
    config.summary()
    if debug:
        config.debug()


@cli.command()
@click.argument('read_path', type=click.Path(exists=True))
@click.option('--summary', '-s', is_flag=True, default=False, show_default=True)
def debug(
        read_path: Path,
        summary: bool
) -> None:
    """
    Debug a config.
    """
    config = Config(path=Path(read_path))
    if summary:
        config.summary()
    config.debug()


@cli.command(name='print')
@click.argument('read_path', type=click.Path(exists=True))
def print_config(
        read_path: Path,
) -> None:
    """
    Print a config to terminal.
    """
    config = Config(path=Path(read_path))
    config.print()


@cli.command(name='find')
@click.argument('read_path', type=click.Path(exists=True))
@click.argument('address', type=str)
def find(
        read_path: Path,
        address: str
) -> None:
    """
    Find and print config components to terminal.
    """
    config = Config(path=Path(read_path))
    for found in config.find(address):
        found.print()


def careful_write(config: BaseConfig, write_path: Path) -> None:
    """
    Write config to path, check overwrite and get user confirmation.
    :param config: Config
    :param write_path: Path
    """
    if Path(write_path).exists():
        value = click.prompt(f'Are you sure you want to overwrite {write_path}? y/n', default='n')
        if value.lower() == 'y':
            config.write(Path(write_path))
        else:
            print('aborted.')
    else:
        config.write(Path(write_path))


def string_to_tuple(string: str) -> Tuple[str]:
    """
    Parse argument/option comma separated string into tuples.
    :param string: str
    :return: tuple[str]
    """
    if string and isinstance(string, str):
        return tuple(string.split(','))
    raise TypeError('Function expects str')
