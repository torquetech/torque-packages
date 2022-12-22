# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import os
import subprocess
import tempfile

import yaml

from torque import k8s
from torque import v1


class V1Provider(v1.provider.Provider):
    """TODO"""

    CONFIGURATION = {
        "defaults": {
            "debug": False,
            "instances": {}
        },
        "schema": {
            "debug": bool,
            "instances": {
                v1.schema.Optional(str): {
                    "chart": str,
                    "repo": {
                        "name": str,
                        "url": str
                    },
                    "namespace": str,
                    "values": dict[str, object]
                }
            }
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "k8s": {
                "interface": k8s.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._kubeconfig = None

        self._current_state = {}
        self._new_state = {}

        self._load_state()

        with self as p:
            p.add_hook("apply", self._apply)
            p.add_hook("delete", self._delete)

    def _load_state(self):
        """TODO"""

        with self.context as ctx:
            self._current_state = ctx.get_data("state", v1.utils.fqcn(self)) or {}

    def _store_state(self):
        """TODO"""

        with self.context as ctx:
            ctx.set_data("state", v1.utils.fqcn(self), self._current_state)

    def _generate_kubeconfig(self):
        """TODO"""

        kubeconfig = self.interfaces.k8s.kubeconfig()

        fd, self._kubeconfig = tempfile.mkstemp(prefix="kubeconfig-", suffix=".yaml")

        with os.fdopen(fd, "w") as file:
            yaml.safe_dump(kubeconfig,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

    def _update_object(self, name: str):
        """TODO"""

        old_obj = self._current_state.get(name)
        obj = v1.utils.resolve_futures(self._new_state.get(name))

        cmd = [
            "helm", "repo", "add",
            obj["repo"]["name"],
            obj["repo"]["url"]
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       check=True)

        cmd = [
            "helm", "install" if old_obj is None else "upgrade",
            "--kubeconfig", self._kubeconfig,
            "--create-namespace",
            "--namespace", obj["namespace"],
            "--values", obj["values_file"],
            name,
            f"{obj['repo']['name']}/{obj['chart']}"
        ]

        if self.configuration["debug"]:
            cmd.append("--debug")

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       check=True)

        self._current_state[name] = {
            "namespace": obj["namespace"]
        }

    def _delete_object(self, name: str):
        """TODO"""

        obj = self._current_state.get(name)

        cmd = [
            "helm", "uninstall",
            "--namespace", obj["namespace"],
            "--kubeconfig", self._kubeconfig,
            name
        ]

        if self.configuration["debug"]:
            cmd.append("--debug")

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       check=True)

        self._current_state.pop(name)

    def _apply(self):
        """TODO"""

        for name, obj in self.configuration["instances"].items():
            self.add(name,
                     obj["chart"],
                     obj["repo"]["name"],
                     obj["repo"]["url"],
                     obj["namespace"],
                     obj["values"])

        try:
            self._generate_kubeconfig()

            v1.utils.apply_objects(self._current_state,
                                   self._new_state,
                                   self._update_object,
                                   self._delete_object)

        finally:
            os.unlink(self._kubeconfig)
            self._store_state()

    def _delete(self):
        """TODO"""

        try:
            self._generate_kubeconfig()

            v1.utils.apply_objects(self._current_state,
                                   {},
                                   self._update_object,
                                   self._delete_object)

        except k8s.ClusterNotInitialized:
            pass

        finally:
            os.unlink(self._kubeconfig)
            self._store_state()

    def add(self,
            name: str,
            chart: str,
            repo_name: str,
            repo_url: str,
            namespace: str,
            values: dict[str, object]):
        """TODO"""

        fd, values_file = tempfile.mkstemp(prefix=f"{name}-values-", suffix=".yaml")

        with os.fdopen(fd, "w") as file:
            yaml.safe_dump(values,
                           stream=file,
                           default_flow_style=False,
                           sort_keys=False)

        self._new_state[name] = {
            "chart": chart,
            "repo": {
                "name": repo_name,
                "url": repo_url
            },
            "namespace": namespace,
            "values_file": values_file
        }


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
