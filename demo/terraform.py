# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import functools
import json
import os
import subprocess
import threading
import typing

from torque import v1

from demo import providers
from demo import utils


class _Block:
    """TODO"""

    def __init__(self, name: str, *args):
        self._name = name
        self._args = args

    def __str__(self) -> str:
        args = [f"\"{i}\"" for i in self._args]
        args = " ".join(args)

        return f"{self._name} {args}"


class _Key:
    """TODO"""

    def __init__(self, name: str):
        self._name = name

    def __str__(self) -> str:
        return self._name


class _Obj:
    """TODO"""

    def __init__(self, v: str):
        self._v = v

    def __str__(self) -> str:
        return self._v


class _Str:
    """TODO"""

    def __init__(self, v: str):
        self._v = v

    def __str__(self) -> str:
        return f"\"{self._v}\""


class _Bool:
    """TODO"""

    def __init__(self, v: bool):
        self._v = v

    def __str__(self) -> str:
        if self._v:
            return "true"

        return "false"


class _Int:
    """TODO"""

    def __init__(self, v: int):
        self._v = v

    def __str__(self) -> str:
        return str(self._v)


def _to_tf(obj: dict, level: int) -> str:
    """TODO"""

    string = ""
    padding = " " * (level * 2)

    for k, v in obj.items():
        if isinstance(k, _Block):
            string += f"{padding}{k} "

        else:
            string += f"{padding}{k} = "

        if isinstance(v, dict):
            string += "{\n"
            string += _to_tf(v, level+1)
            string += f"{padding}" "}"

        elif isinstance(v, list):
            string += "["
            string += ", ".join(v)
            string += "]"

        else:
            string += f"{v}"

        string += "\n"

    return string


class PersistentVolumesProvider(providers.PersistentVolumesProvider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "zone": "us-east-1a",
            "type": "gp2"
        },
        "schema": {
            "zone": str,
            "type": str
        }
    }

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {}

    def create(self, name: str, size: int) -> utils.Future[str]:
        """TODO"""

        name = f"{self.context.deployment_name}.{name}"
        name = name.replace(".", "-")

        self.provider.add_target(_Block("resource", "aws_ebs_volume", name), {
            _Key("availability_zone"): _Str(self.configuration["zone"]),
            _Key("type"): _Str(self.configuration["type"]),
            _Key("size"): _Int(size)
        })

        def resolve_future(future: utils.Future[object], state: dict):
            if state is None:
                future.set(f"<{name}_id>")
                return

            resources = state["values"]["root_module"]["resources"]

            for resource in resources:
                if resource["name"] == name:
                    future.set(resource["values"]["id"])
                    return

            raise RuntimeError("{name}: terraform resource not found")

        return self.provider.add_future(resolve_future)


class Provider(v1.provider.Provider):
    """TODO"""

    _CONFIGURATION = {
        "defaults": {
            "aws": {
                "region": "us-east-1",
                "s3": {
                    "bucket": "terraform-state",
                    "key": "aws/core.tfstate"
                }
            }
        },
        "schema": {
            "aws": {
                "region": str,
                "s3": {
                    "bucket": str,
                    "key": str
                }
            }
        }
    }

    @classmethod
    def on_configuration(cls, configuration: dict) -> dict:
        """TODO"""

        return v1.utils.validate_schema(cls._CONFIGURATION["schema"],
                                        cls._CONFIGURATION["defaults"],
                                        configuration)

    @classmethod
    def on_requirements(cls) -> dict:
        """TODO"""

        return {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._futures = []
        self._targets = {}
        self._lock = threading.Lock()

        self._setup_aws_provider()

    def _setup_aws_provider(self):
        """TODO"""

        config = self.configuration["aws"]

        self._targets[_Block("terraform")] = {
            _Block("required_providers"): {
                _Key("aws"): {
                    _Key("source"): _Str("hashicorp/aws"),
                    _Key("version"): _Str("~> 3.0")
                }
            },
            _Block("backend", "s3"): {
                _Key("bucket"): _Str(config["s3"]["bucket"]),
                _Key("key"): _Str(config["s3"]["key"]),
                _Key("region"): _Str(config["region"])
            }
        }

        self._targets[_Block("provider", "aws")] = {
            _Key("region"): _Str(config["region"])
        }

    def on_apply(self, dry_run: bool):
        """TODO"""

        with open(f"{self.context.path()}/main.tf", "w", encoding="utf8") as file:
            file.write(_to_tf(self._targets, 0))

        if dry_run:
            for future in self._futures:
                future(None)

            return

        cmd = [
            "terraform", "init"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       cwd=self.context.path(),
                       check=True)

        cmd = [
            "terraform", "apply",
            "-auto-approve"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       cwd=self.context.path(),
                       check=True)

        cmd = [
            "terraform", "show",
            "-json"
        ]

        print(f"+ {' '.join(cmd)}")
        p = subprocess.run(cmd,
                           env=os.environ,
                           cwd=self.context.path(),
                           check=True,
                           capture_output=True)

        state = json.loads(p.stdout.decode("utf8"))

        for future in self._futures:
            future(state)

    def on_delete(self, dry_run: bool):
        """TODO"""

        if dry_run:
            return

        cmd = [
            "terraform", "apply",
            "-auto-approve", "-destroy"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=False)

    def on_command(self, argv: [str]):
        """TODO"""

    def add_target(self, key: object, value: object):
        """TODO"""

        with self._lock:
            self._targets[key] = value

    def add_future(self, resolve_future: typing.Callable) -> utils.Future[object]:
        """TODO"""

        future = utils.Future()

        with self._lock:
            self._futures.append(functools.partial(resolve_future, future))

        return future
