# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import os
import subprocess

from torque import docker_compose
from torque import docker_compose_load_balancer
from torque import v1


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        return {
            "dc": {
                "interface": docker_compose.V1Provider,
                "required": True
            },
            "lb": {
                "interface": docker_compose_load_balancer.V1Provider,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_services = []
        self._new_entries = []

        self._hosts = []

        self._load_state()

        with self as p:
            p.add_hook("apply", self._apply)
            p.add_hook("delete", self._delete)

    def _load_state(self) -> dict[str, object]:
        """DOCSTRING"""

        with self.context as ctx:
            self._current_services = ctx.get_data("state", v1.utils.fqcn(self)) or []

    def _store_state(self):
        """DOCSTRING"""

        with self.context as ctx:
            ctx.set_data("state", v1.utils.fqcn(self), self._current_services)

    def _get_ip(self, service: str) -> str:
        """DOCSTRING"""

        network = self.context.deployment_name

        cmd = [
            "docker", "inspect",
            "--format",
            f"{{{{(index .NetworkSettings.Networks \"{network}\").IPAddress}}}}",
            f"{network}-{service}-1",
        ]

        print(f"+ {' '.join(cmd)}")
        p = subprocess.run(cmd,
                           env=os.environ,
                           cwd=self.context.path(),
                           check=True,
                           capture_output=True)

        return p.stdout.decode("utf8").strip()

    def _load_hosts(self):
        """DOCSTRING"""

        self._hosts = [
            "#!/bin/bash",
            "cat > /etc/hosts <<EOF"
        ]

        try:
            with open("/etc/hosts", "r", encoding="utf-8") as f:
                self._hosts.extend(f.read().splitlines())

        except FileNotFoundError:
            pass

    def _clear_hosts(self):
        """DOCSTRING"""

        for service in self._current_services:
            entry_id = f"### {service}"

            self._hosts = [
                i for i in self._hosts if not i.endswith(entry_id)
            ]

        for e in self._new_entries:
            entry_id = f"### {self.context.deployment_name}-{e.service}"

            self._hosts = [
                i for i in self._hosts if not i.endswith(entry_id)
            ]

        self._current_services = []

    def _store_hosts(self):
        """DOCSTRING"""

        self._hosts += ["EOF", ""]

        update_hosts = f"{self.context.path()}/update_etc_hosts.sh"

        with open(update_hosts, "w", encoding="utf-8") as f:
            f.write("\n".join(self._hosts))

        os.chmod(update_hosts, 0o755)

        cmd = [
            "sudo", "./update_etc_hosts.sh"
        ]

        print(f"+ {' '.join(cmd)}")
        subprocess.run(cmd,
                       env=os.environ,
                       cwd=self.context.path(),
                       check=True)

    def _apply(self):
        """DOCSTRING"""

        self._new_entries = self.interfaces.lb.get_entries()

        self._load_hosts()
        self._clear_hosts()

        for e in self._new_entries:
            service = f"{self.context.deployment_name}-{e.service}"
            ip = self._get_ip(e.service)

            for host in e.hosts:
                self._hosts.append(f"{ip}\t{host}.{e.domain} ### {service}")

            self._current_services.append(service)

        self._store_hosts()
        self._store_state()

    def _delete(self):
        """DOCSTRING"""

        self._load_hosts()
        self._clear_hosts()

        self._store_hosts()
        self._store_state()


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
