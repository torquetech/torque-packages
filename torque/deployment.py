# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import multiprocessing
import threading

from collections import namedtuple

from torque import exceptions
from torque import execute
from torque import extensions
from torque import model
from torque import options
from torque import profile

from torque.v1 import component as component_v1
from torque.v1 import link as link_v1


Configuration = namedtuple("Configuration", ["provider", "components", "links"])


class Deployment:
    """TODO"""

    def __init__(self,
                 dag: model.DAG,
                 config: dict[str, options.Options],
                 exts: extensions.Extensions):
        self.dag = dag
        self.config = config
        self.exts = exts
        self.artifacts = {}

    def _component(self, name: str) -> component_v1.Component:
        """TODO"""

        component = self.dag.components[name]
        config = self.config.components[name]

        return self.exts.component(component.type)(component.name,
                                                   component.group,
                                                   component.params,
                                                   config)

    def _link(self, name: str) -> link_v1.Link:
        """TODO"""

        link = self.dag.links[name]
        config = self.config.links[name]

        source = self._component(link.source)
        destination = self._component(link.destination)

        return self.exts.link(link.type)(link.name,
                                         link.params,
                                         config,
                                         source,
                                         destination)

    def _on_build(self, type: str, name: str) -> list[str]:
        """TODO"""

        artifacts = None

        if type == "component":
            instance = self._component(name)
            artifacts = instance.on_build()

        elif type == "link":
            instance = self._link(name)
            source_artifacts = self.artifacts[f"component/{instance.source.name}"]

            artifacts = instance.on_build(source_artifacts)

        else:
            assert False

        return artifacts

    def build(self, workers: int):
        """TODO"""

        lock = threading.Lock()

        with multiprocessing.Pool(workers) as pool:
            def _on_build(type: str, name: str):
                artifacts = pool.apply(self._on_build, (type, name))

                if artifacts is None:
                    return False

                with lock:
                    self.artifacts[f"{type}/{name}"] = artifacts

                return True

            execute.from_roots(workers, self.dag, _on_build)


def _load_provider(profile: profile.Profile,
                   exts: extensions.Extensions) -> (str, options.Options):
    """TODO"""

    name, config = profile.provider()
    provider = exts.provider(name)

    config = options.process(provider.configuration(), config)

    for default in config.defaults:
        print(f"WARNING: {name}: {default}: used default value")

    for unused in config.unused:
        print(f"WARNING: {name}: {unused}: unused parameter")

    return name, config


def _load_components(dag: model.DAG,
                     profile: profile.Profile,
                     exts: extensions.Extensions) -> dict[str, options.Options]:
    """TODO"""

    components = {}

    for component in dag.components.values():
        req_config = exts.component(component.type).configuration()
        _, raw_config = profile.component(component.name)

        config = options.process(req_config, raw_config)

        for default in config.defaults:
            print(f"WARNING: {component.name}: {default}: used default value")

        for unused in config.unused:
            print(f"WARNING: {component.name}: {unused}: unused parameter")

        components[component.name] = config

    return components


def _load_links(dag: model.DAG,
                profile: profile.Profile,
                exts: extensions.Extensions) -> dict[str, options.Options]:
    """TODO"""

    links = {}

    for link in dag.links.values():
        req_config = exts.link(link.type).configuration()
        _, raw_config = profile.link(link.name)

        config = options.process(req_config, raw_config)

        for default in config.defaults:
            print(f"WARNING: {link.name}: {default}: used default value")

        for unused in config.unused:
            print(f"WARNING: {link.name}: {unused}: unused parameter")

        links[link.name] = config

    return links


def _load_config(dag: model.DAG,
                 profile: profile.Profile,
                 exts: extensions.Extensions) -> Configuration:
    """TODO"""

    if dag.revision != profile.revision():
        print("WARNING: profile out of date")

    provider = _load_provider(profile, exts)
    components = _load_components(dag, profile, exts)
    links = _load_links(dag, profile, exts)

    return Configuration(provider, components, links)


def load(components: list[str],
         profile: profile.Profile,
         dag: model.DAG,
         exts: extensions.Extensions) -> Deployment:
    """TODO"""

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)
    config = _load_config(dag, profile, exts)

    return Deployment(dag, config, exts)
