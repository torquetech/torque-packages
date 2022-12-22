# This file contains code from https://github.com/kubernetes-client/python modified
# to suit torque's k8s provider. Original code is released under Apache 2.0 license.
# While torque-k8s-provider package is released under Mozilla Public License version
# 2.0, this file is an exception and is released under Apache 2.0 license. Apache 2.0
# license text can be found at https://www.apache.org/licenses/LICENSE-2.0.html

"""DOCSTRING"""

import re

import kubernetes


UPPER_FOLLOWED_BY_LOWER_RE = re.compile("(.)([A-Z][a-z]+)")
LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE = re.compile("([a-z0-9])([A-Z])")


def _get_api_for(client: kubernetes.client.ApiClient, obj: dict[str, object]):
    # pylint: disable=C0209

    group, _, version = obj["apiVersion"].partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    # Only replace the last instance
    group = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group = "".join(word.capitalize() for word in group.split("."))
    fcn_to_call = "{0}{1}Api".format(group, version.capitalize())
    api = getattr(kubernetes.client, fcn_to_call)(client)
    # Replace CamelCased action_type into snake_case
    kind = obj["kind"]
    kind = UPPER_FOLLOWED_BY_LOWER_RE.sub(r"\1_\2", kind)
    kind = LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE.sub(r"\1_\2", kind).lower()
    # Expect the user to create namespaced objects more often
    if hasattr(api, "create_namespaced_{0}".format(kind)):
        create = getattr(api, "create_namespaced_{0}".format(kind))
        get = getattr(api, "read_namespaced_{0}".format(kind))
        delete = getattr(api, "delete_namespaced_{0}".format(kind))
        replace = getattr(api, "replace_namespaced_{0}".format(kind))
        namespaced = True
    else:
        create = getattr(api, "create_{0}".format(kind))
        get = getattr(api, "read_{0}".format(kind))
        delete = getattr(api, "delete_{0}".format(kind))
        replace = getattr(api, "replace_{0}".format(kind))
        namespaced = False

    return create, get, delete, replace, namespaced


def update_object(client: kubernetes.client.ApiClient,
                  obj: dict[str, object]) -> dict[str, object]:
    """DOCSTRING"""

    api = _get_api_for(client, obj)
    create, get, _, replace, namespaced = api

    do_replace = False

    try:
        if namespaced:
            get(obj["metadata"]["name"], obj["metadata"]["namespace"]).to_dict()

        else:
            get(obj["metadata"]["name"]).to_dict()

        do_replace = True

    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            raise

    if do_replace:
        if namespaced:
            replace(obj["metadata"]["name"], obj["metadata"]["namespace"], obj)

        else:
            replace(obj["metadata"]["name"], obj)

    else:
        if namespaced:
            create(obj["metadata"]["namespace"], obj)

        else:
            create(obj)

    return obj


def delete_object(client: kubernetes.client.ApiClient,
                  obj: dict[str, object]):
    """DOCSTRING"""

    api = _get_api_for(client, obj)
    _, _, delete, _, namespaced = api

    try:
        if namespaced:
            delete(obj["metadata"]["name"], obj["metadata"]["namespace"])

        else:
            delete(obj["metadata"]["name"])

    except kubernetes.client.exceptions.ApiException as e:
        if e.status != 404:
            raise
