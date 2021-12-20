# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


install_requirements = [i.strip() for i in open("requirements.txt").readlines()]

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="s4l_scripts",
    version="0.1.0",
    description="Collection of Sim4Life scripts",
    long_description=readme,
    author="Bryn Lloyd",
    author_email="lloyd@itis.swiss",
    url="https://github.com/dyollb/s4l-scripts.git",
    license=license,
    install_requires=install_requirements,
    packages=find_packages(where="src"),
    package_dir={
        "": "src",
    },
)
