# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import hashlib
import ssl

from torque import v1
from torque import do
from torque import dolib


class _V2Certificates:
    """TODO"""

    @classmethod
    def create(cls, client: dolib.Client, new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        res = client.post("v2/certificates", new_obj["params"])
        data = res.json()

        if res.status_code not in (201, 202):
            raise v1.exceptions.RuntimeError(f"{new_obj['name']}: {data['message']}")

        data = data["certificate"]

        return new_obj | {
            "metadata": {
                "id": data["id"]
            }
        }

    @classmethod
    def update(cls,
               client: dolib.Client,
               old_obj: dict[str, object],
               new_obj: dict[str, object]) -> dict[str, object]:
        """TODO"""

        raise v1.exceptions.RuntimeError(f"{old_obj['name']}: cannot update certificates")

    @classmethod
    def delete(cls, client: dolib.Client, old_obj: dict[str, object]):
        """TODO"""

        client.delete(f"v2/certificates/{old_obj['metadata']['id']}")

    @classmethod
    def wait(cls, client: dolib.Client, obj: dict[str, object]):
        """TODO"""


class V1Provider(v1.provider.Provider):
    """TODO"""

    @classmethod
    def on_requirements(cls) -> dict[str, object]:
        """TODO"""

        return {
            "do": {
                "interface": do.V1Provider,
                "required": True
            }
        }

    def create_external(self, cert: str, key: str) -> v1.utils.Future[str]:
        """TODO"""

        cert = v1.utils.resolve_path(cert)
        key = v1.utils.resolve_path(key)

        with open(cert, encoding="utf-8") as f:
            cert = f.read()

        with open(key, encoding="utf-8") as f:
            key = f.read()

        der = ssl.PEM_cert_to_DER_cert(cert)
        sha1 = hashlib.sha1(der).hexdigest()

        return self.interfaces.do.add_object({
            "kind": "v2/certificates",
            "name": sha1,
            "params": {
                "name": sha1,
                "type": "custom",
                "private_key": key,
                "leaf_certificate": cert
            }
        })

    def create_managed(self, domain: str) -> v1.utils.Future[str]:
        """TODO"""

        return self.interfaces.do.add_object({
            "kind": "v2/certificates",
            "name": domain,
            "params": {
                "name": domain,
                "type": "lets_encrypt",
                "dns_names": [
                    f"*.{domain}"
                ]
            }
        })


dolib.HANDLERS.update({
    "v2/certificates": _V2Certificates
})

repository = {
    "v1": {
        "providers": [
            V1Provider
        ]
    }
}
