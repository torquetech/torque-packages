# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os

from setuptools import find_packages
from setuptools import setup


CURDIR = os.path.abspath(os.path.dirname(__file__))


def load_file(name: str) -> str:
    with open(f"{CURDIR}/{name}", encoding="utf8") as file:
        return file.read().strip()


setup(name="torque-workspace-cli",
      version=load_file("VERSION"),
      author="Torque Team",
      author_email="team@torquetech.io",
      description="",
      long_description=load_file("README.md"),
      long_description_content_type="text/markdown",
      url="https://github.com/torquetech/workspace",
      license="MPL v2.0",
      classifiers=[
          "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)"
      ],
      packages=find_packages(),
      python_requires=">=3.9",
      install_requires=[
          "pyyaml",
          "wheel",
          "setuptools"
      ],
      entry_points={
          "console_scripts": [
              "torque=torque.__main__:main"
          ],
      })
