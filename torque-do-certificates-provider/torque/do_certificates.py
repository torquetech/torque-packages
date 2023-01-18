# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""DOCSTRING"""

import hashlib
import ssl

from torque import v1
from torque import do
from torque import dolib
from torque import do_domains


class V1Interface(v1.bond.Interface):
    """DOCSTRING"""

    def domain(self) -> str:
        """DOCSTRING"""

    def certificate_id(self) -> v1.utils.Future[str]:
        """DOCSTRING"""


class _V2Certificates(dolib.Resource):
    """DOCSTRING"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._do_name = self._object["name"]

        self._current_params = None
        self._cert_id = None

        if "metadata" in self._object:
            self._cert_id = self._object["metadata"]["id"]

    def _get(self) -> bool:
        """DOCSTRING"""

        page = 1

        while True:
            res = self._client.get(f"v2/certificates?page={page}&per_page=20")
            data = res.json()

            if res.status_code != 200:
                raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

            certs = data["certificates"]

            for cert in certs:
                if self._do_name == cert["name"]:
                    self._current_params = {
                        "name": cert["name"],
                        "type": cert["type"]
                    }

                    self._cert_id = cert["id"]

                    return True

            if len(certs) != 20:
                break

            page += 1

        return False

    def _create(self):
        """DOCSTRING"""

        res = self._client.post("v2/certificates", self._object["params"])
        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{self._name}: {data['message']}")

        self._cert_id = data["certificate"]["id"]

    def _update(self):
        """DOCSTRING"""

        params = self._object["params"]
        params = {
            "name": params["name"],
            "type": params["type"]
        }

        if params == self._current_params:
            return

        raise v1.exceptions.RuntimeError(f"{self._name}: cannot modify certificate")

    def update(self) -> dict[str, object]:
        """DOCSTRING"""

        if not self._get():
            self._create()

        else:
            self._update()

        return self._object | {
            "metadata": {
                "id": self._cert_id
            }
        }

    def delete(self):
        """DOCSTRING"""

        def cond():
            res = self._client.delete(f"v2/certificates/{self._cert_id}")

            if res.status_code == 204:
                return True

            if res.status_code != 403:
                raise v1.exceptions.RuntimeError(f"{self._name}: {res.json()['message']}")

            return False

        v1.utils.wait_for(cond, f"waiting for {self._name} to be released")


class V1Provider(v1.provider.Provider):
    """DOCSTRING"""


class V1External(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = V1Interface

    CONFIGURATION = {
        "defaults": {
            "domain": "example.com",
            "key_file": "key.pem",
            "certificate_file": "cert.pem"
        },
        "schema": {
            "domain": str,
            "key_file": str,
            "certificate_file": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            },
            "domains": {
                "interface": do_domains.V1Provider,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._domain = self.configuration["domain"]
        self._cert_id = None

        with self.interfaces.do as p:
            p.add_hook("apply-objects", self._apply)

    def _apply(self):
        """DOCSTRING"""

        if self.interfaces.domains:
            self.interfaces.domains.create(self._domain)

        cert = v1.utils.resolve_path(self.configuration["certificate_file"])
        key = v1.utils.resolve_path(self.configuration["key_file"])

        with open(cert, encoding="utf-8") as f:
            cert = f.read()

        with open(key, encoding="utf-8") as f:
            key = f.read()

        der = ssl.PEM_cert_to_DER_cert(cert)
        sha1 = hashlib.sha1(der).hexdigest()

        self._cert_id = self.interfaces.do.object_id(self.interfaces.do.add_object({
            "kind": "v2/certificate",
            "name": sha1,
            "params": {
                "name": sha1,
                "type": "custom",
                "private_key": key,
                "leaf_certificate": cert
            }
        }))

    def domain(self) -> str:
        """DOCSTRING"""

        return self._domain

    def certificate_id(self) -> v1.utils.Future[str]:
        """DOCSTRING"""

        return self._cert_id


class V1LetsEncrypt(v1.bond.Bond):
    """DOCSTRING"""

    PROVIDER = V1Provider
    IMPLEMENTS = V1Interface

    CONFIGURATION = {
        "defaults": {
            "domain": "my-domain.com"
        },
        "schema": {
            "domain": str
        }
    }

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """DOCSTRING"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            },
            "domains": {
                "interface": do_domains.V1Provider,
                "required": False
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._domain = self.configuration["domain"]
        self._cert_id = None

        with self.interfaces.do as p:
            p.add_hook("apply", self._apply)

    def _apply(self):
        """DOCSTRING"""

        if self.interfaces.domains:
            self.interfaces.domains.create(self._domain)

        self._cert_id = self.interfaces.do.object_id(self.interfaces.do.add_object({
            "kind": "v2/certificate",
            "name": self._domain,
            "params": {
                "name": self._domain,
                "type": "lets_encrypt",
                "dns_names": [
                    f"*.{self._domain}"
                ]
            }
        }))

    def domain(self) -> str:
        """DOCSTRING"""

        return self._domain

    def certificate_id(self) -> v1.utils.Future[str]:
        """DOCSTRING"""

        return self._cert_id


dolib.HANDLERS.update({
    "v2/certificate": _V2Certificates
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ],
        "bonds": [
            V1External,
            V1LetsEncrypt
        ]
    }
}
