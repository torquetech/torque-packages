# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import base64
import functools
import json
import os
import subprocess
import threading

from torque import v1


class V1Interface(v1.bond.Interface):
    """DOCSTRING"""

    def auth(self) -> dict[str, dict]:
        """DOCSTRING"""


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "impl": {
                "interface": V1Interface,
                "required": True
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._tags = {}
        self._auth = None

        self._lock = threading.Lock()

    def _resolve_tag(self, image: str) -> str:
        """DOCSTRING"""

        return "/".join([self._auth["server"],
                         self._auth["prefix"],
                         image])

    def _dockerconfig(self) -> str:
        """DOCSTRING"""

        server = self._auth["server"]
        username = self._auth["username"]
        password = self._auth["password"]

        auth = f"{username}:{password}"

        auth = auth.encode()
        auth = base64.b64encode(auth)
        auth = auth.decode()

        dockerconfig = json.dumps({
            "auths": {
                server: {
                    "auth": auth
                }
            }
        })

        dockerconfig = dockerconfig.encode()
        dockerconfig = base64.b64encode(dockerconfig)

        return dockerconfig.decode()

    def login(self) -> str:
        """DOCSTRING"""

        self._auth = self.interfaces.impl.auth()

        cmd = [
            "docker", "login",
            "--username", self._auth["username"],
            "--password-stdin",
            self._auth["server"]
        ]

        print(f"+ {' '.join(cmd[:3] + ['****'] + cmd[4:])}")
        subprocess.run(cmd,
                       env=os.environ,
                       input=bytes(self._auth["password"], encoding="utf-8"),
                       check=True)

        return self._dockerconfig()

    def push_images(self):
        """DOCSTRING"""

        for image, tag in self._tags.items():
            tag = v1.utils.resolve_futures(tag)

            cmd = [
                "docker", "tag",
                image, tag
            ]

            print(f"+ {' '.join(cmd)}")
            subprocess.run(cmd,
                           env=os.environ,
                           check=True)

            cmd = [
                "docker", "push",
                tag
            ]

            print(f"+ {' '.join(cmd)}")
            subprocess.run(cmd,
                           env=os.environ,
                           check=True)

    def register_image(self, image: str) -> v1.utils.Future[str]:
        """DOCSTRING"""

        with self._lock:
            if image not in self._tags:
                self._tags[image] = v1.utils.Future(functools.partial(self._resolve_tag, image))

            return self._tags[image]


repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
