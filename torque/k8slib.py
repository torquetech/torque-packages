# This file contains code from https://github.com/kubernetes-client/python modified
# to suit torque's k8s provider. Original code is released under Apache 2.0 license.
# While torque-k8s-provider package is released under Mozilla Public License version
# 2.0, this file is an exception and is released under Apache 2.0 license. Apache 2.0
# license text can be found at https://www.apache.org/licenses/LICENSE-2.0.html

import difflib
import re
import sys

import kubernetes
import yaml

from torque import v1


UPPER_FOLLOWED_BY_LOWER_RE = re.compile('(.)([A-Z][a-z]+)')
LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE = re.compile('([a-z0-9])([A-Z])')


def _get_api_for(client: kubernetes.client.ApiClient, obj: dict[str, object]):
    group, _, version = obj["apiVersion"].partition("/")
    if version == "":
        version = group
        group = "core"
    # Take care for the case e.g. api_type is "apiextensions.k8s.io"
    # Only replace the last instance
    group = "".join(group.rsplit(".k8s.io", 1))
    # convert group name from DNS subdomain format to
    # python class name convention
    group = "".join(word.capitalize() for word in group.split('.'))
    fcn_to_call = "{0}{1}Api".format(group, version.capitalize())
    api = getattr(kubernetes.client, fcn_to_call)(client)
    # Replace CamelCased action_type into snake_case
    kind = obj["kind"]
    kind = UPPER_FOLLOWED_BY_LOWER_RE.sub(r'\1_\2', kind)
    kind = LOWER_OR_NUM_FOLLOWED_BY_UPPER_RE.sub(r'\1_\2', kind).lower()
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


def _diff(name: str, obj1: dict[str, object], obj2: dict[str, object]):
    """TODO"""

    obj1 = yaml.safe_dump(obj1) if obj1 else ""
    obj2 = yaml.safe_dump(obj2) if obj2 else ""

    diff = difflib.unified_diff(obj1.split("\n"),
                                obj2.split("\n"),
                                fromfile=f"a/{name}",
                                tofile=f"b/{name}",
                                lineterm="")

    diff = "\n".join(diff)

    return obj1 != obj2, diff


def _update_object(client: kubernetes.client.ApiClient,
                   obj: dict[str, object]) -> dict[str, object]:
    """TODO"""

    api = _get_api_for(client, obj)
    create, get, _, replace, namespaced = api

    do_replace = False

    try:
        if namespaced:
            get(obj["metadata"]["name"], obj["metadata"]["namespace"]).to_dict()

        else:
            get(obj["name"]).to_dict()

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


def _delete_object(client: kubernetes.client.ApiClient, obj: dict[str, object]):
    """TODO"""

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


def apply_objects(client: kubernetes.client.ApiClient,
                  objects: dict[str, object],
                  new_objects: dict[str, object],
                  quiet: bool):
    """TODO"""

    for name, obj in new_objects.items():
        old_obj = objects.get(name, None)
        new_obj = v1.utils.resolve_futures(obj)

        changed, diff = _diff(name, old_obj, new_obj)

        if not changed:
            if not quiet:
                print(f"{name}: no change", file=sys.stdout)

            continue

        if not quiet:
            print(f"{name}: updating...", file=sys.stdout)

        if not quiet:
            print(diff, file=sys.stdout)

        objects[name] = _update_object(client, new_obj)

    for name, obj in list(objects.items()):
        if name in new_objects:
            continue

        if not quiet:
            print(f"{name}: deleting...", file=sys.stdout)

        _, diff = _diff(name, obj, None)

        if not quiet:
            print(diff, file=sys.stdout)

        _delete_object(client, obj)
        objects.pop(name)
