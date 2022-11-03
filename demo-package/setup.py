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


def package_files(module: str, pattern: str) -> [str]:
    files = glob.glob(f"{module}/{pattern}", recursive=True)
    files = filter(lambda x: os.path.isfile(x), files)

    return map(lambda x: x.removeprefix(f"{module}/"), files)


def package_data(module: str, patterns: [str]) -> [str]:
    files = []

    for pattern in patterns:
        files += package_files(module, pattern)

    return files


setup(name="demo-package",
      version=load_file("VERSION"),
      author="Torque Team",
      author_email="team@torquetech.io",
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
          "demo": package_data("demo", ["templates/**"])
      },
      include_package_data=True,
      python_requires=">=3.10",
      install_requires=[
          "jinja2",
          "pyyaml",
      ],
      entry_points={
          "torque": [
              "demo=demo.demo:repository"
          ]
      }
)
