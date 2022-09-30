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


class Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._futures = []
        self._targets = {}
        self._lock = threading.Lock()

        self._setup_aws_provider()

        with self.context as ctx:
            ctx.add_hook("apply", self._apply)
            ctx.add_hook("delete", self._delete)

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

    def _apply(self):
        """TODO"""

        with open(f"{self.context.path()}/main.tf", "w", encoding="utf8") as file:
            file.write(_to_tf(self._targets, 0))

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

    def _delete(self):
        """TODO"""

        cmd = [
            "terraform", "apply",
            "-auto-approve", "-destroy"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd, env=os.environ, cwd=self.context.path(), check=False)

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


class PersistentVolumesProvider(v1.bond.Bond):
    """TODO"""

    PROVIDER = Provider
    IMPLEMENTS = providers.PersistentVolumesProvider

    CONFIGURATION = {
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
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "tf": {
                "interface": Provider,
                "required": True
            }
        }

    def create(self, name: str, size: int) -> utils.Future[str]:
        """TODO"""

        name = f"{self.context.deployment_name}.{name}"
        name = name.replace(".", "-")

        self.interfaces.tf.add_target(_Block("resource", "aws_ebs_volume", name), {
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

        return self.interfaces.tf.add_future(resolve_future)
