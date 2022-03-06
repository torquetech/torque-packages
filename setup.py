# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os

from setuptools import setup, find_packages


CURDIR = os.path.abspath(os.path.dirname(__file__))
README = None

with open(os.path.join(CURDIR, "README.md"), "r", encoding="utf-8") as f:
    README = f.read()

setup(
    name="torque-workspace-cli",
    version="0.1",
    author="Hrvoje Zeba",
    author_email="hrvoje@torquetech.dev",
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/torquetech/workspace",
    license="License :: OSI Approved :: Apache License 2.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pyyaml"
    ],
    entry_points={
        "console_scripts": [
            "torque=torque.__main__:main"
        ],
    }
)
