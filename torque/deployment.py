# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import multiprocessing
import multiprocessing.pool
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
from torque.v1 import provider as provider_v1
from torque.v1 import tao as tao_v1
from torque.v1 import utils as utils_v1


Configuration = namedtuple("Configuration", ["provider", "components", "links"])


class Deployment:
    """TODO"""

    def __init__(self,
                 name: str,
                 dag: model.DAG,
                 config: dict[str, options.Options],
                 exts: extensions.Extensions):
        self.name = name
        self.dag = dag
        self.config = config
        self.exts = exts
        self.artifacts = {}
        self.manifest = {}

    def _component(self, name: str) -> component_v1.Component:
        """TODO"""

        component = self.dag.components[name]
        config = self.config.components[name]
        artifacts = None

        if f"component/{name}" in self.artifacts:
            artifacts = self.artifacts[f"component/{name}"]

        return self.exts.component(component.type)(component.name,
                                                   component.group,
                                                   component.params,
                                                   config,
                                                   artifacts)

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

    def _provider(self) -> provider_v1.Provider:
        """TODO"""

        name, config = self.config.provider
        return self.exts.provider(name)(config)

    def _on_build(self, type: str, name: str) -> list[str]:
        """TODO"""

        if type == "component":
            instance = self._component(name)

        elif type == "link":
            instance = self._link(name)

        else:
            assert False

        return instance.on_build()

    def _on_generate(self, type: str, name: str) -> list[object]:
        """TODO"""

        if type == "component":
            instance = self._component(name)

        elif type == "link":
            instance = self._link(name)

        else:
            assert False

        return instance.on_generate()

    def _generate(self):
        """TODO"""

        lock = threading.Lock()

        with multiprocessing.pool.ThreadPool(1) as pool:
            def _on_generate(type: str, name: str):
                manifest = pool.apply(self._on_generate, (type, name))

                if manifest is None:
                    return False

                with lock:
                    self.manifest[f"{type}/{name}"] = manifest

                return True

            execute.from_roots(1, self.dag, _on_generate)

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

    def push(self):
        """TODO"""

        self._provider().push(self.artifacts)

    def apply(self, dry_run: bool, show_manifest: bool):
        """TODO"""

        self._generate()

        if show_manifest:
            for name, statements in self.manifest.items():
                print(f"{name}:")

                for statement in statements:
                    print(f"  {utils_v1.fqcn(statement)}")

        self._provider().apply(self.name, self.manifest, dry_run)

    def delete(self, dry_run: bool):
        """TODO"""

        self._generate()
        self._provider().delete(self.name, dry_run)


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

        try:
            config = options.process(req_config, raw_config)

        except exceptions.OptionRequired as exc:
            raise RuntimeError(f"{component.name}: {exc}: component option required") from exc

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

        try:
            config = options.process(req_config, raw_config)

        except exceptions.OptionRequired as exc:
            raise RuntimeError(f"{link.name}: {exc}: link option required") from exc

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


def load(name: str,
         components: list[str],
         profile: profile.Profile,
         dag: model.DAG,
         exts: extensions.Extensions) -> Deployment:
    """TODO"""

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)
    config = _load_config(dag, profile, exts)

    return Deployment(name, dag, config, exts)
