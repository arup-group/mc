"""Packaging settings."""

from setuptools import find_packages, setup

from mc import __version__


setup(
    name="mc",
    version=__version__,
    description="A command line tool for building MATSim config files.",
    packages=find_packages(exclude="tests*"),
    entry_points={"console_scripts": ["mc = mc.main:cli"]},
)
