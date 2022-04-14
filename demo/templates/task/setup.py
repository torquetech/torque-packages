import os
import subprocess

from setuptools import setup, find_packages


CWD = os.path.abspath(os.path.dirname(__file__))


def version() -> str:
    p = subprocess.run(["./version.sh"],
                       cwd=CWD,
                       env=os.environ,
                       shell=True,
                       check=True,
                       capture_output=True)

    return p.stdout.decode("utf8").strip()


setup(
    name="task",
    version=version(),
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "task=task.__main__:main"
        ]
    },
)
