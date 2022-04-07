import os

from setuptools import setup, find_packages


CURDIR = os.path.abspath(os.path.dirname(__file__))


def load_file(name: str) -> str:
    with open(f"{CURDIR}/{name}", encoding="utf8") as file:
        return file.read().strip()


setup(
    name="task",
    version=load_file("VERSION"),
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console-scripts": [
            "taks=task.__main__:main"
        ]
    },
)
