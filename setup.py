"""Packaging settings."""

from setuptools import find_packages, setup
import os

from mc import __version__


requirements_path = "requirements.txt"
install_requires = []
if os.path.isfile(requirements_path):
    with open(requirements_path) as f:
        install_requires = f.read().splitlines()
setup(
    name="mc",
    version=__version__,
    description="A command line tool for using MATSim config files.",
    packages=find_packages(exclude="tests*"),
    install_requires=install_requires,
    entry_points={"console_scripts": ["mc = mc.cli:cli"]},
)
