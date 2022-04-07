# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os

from setuptools import find_packages
from setuptools import glob
from setuptools import setup


CURDIR = os.path.abspath(os.path.dirname(__file__))


def load_file(name: str) -> str:
    with open(f"{CURDIR}/{name}", encoding="utf8") as file:
        return file.read().strip()


def package_data(module: str, pattern: str) -> [str]:
    data = glob.glob(f"{module}/{pattern}", recursive=True)
    data = filter(lambda x: os.path.isfile(x), data)
    data = map(lambda x: x.lstrip(f"{module}/"), data)

    return list(data)


setup(
    name="demo-package",
    version="0.1",
    author="Torque Team",
    author_email="team@torquetech.dev",
    description="",
    long_description=load_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/torquetech/demo-package",
    license="MPL v2.0",
    classifiers=[
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)"
    ],
    packages=find_packages(),
    package_data={
        'demo': package_data("demo", "templates/**")
    },
    include_package_data=True,
    python_requires=">=3.9",
    entry_points={
        "torque": [
            "demo=demo.demo:entry_points"
        ]
    },
)
