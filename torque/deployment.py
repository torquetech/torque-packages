# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""TODO"""

import threading
import sys

from collections import namedtuple
from collections.abc import Callable

from torque import exceptions
from torque import jobs
from torque import model
from torque import options
from torque import profile
from torque import repository

from torque.v1 import component as component_v1
from torque.v1 import link as link_v1
from torque.v1 import provider as provider_v1


Configuration = namedtuple("Configuration", ["provider", "components", "links"])


class Deployment:
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 name: str,
                 profile: str,
                 dag: model.DAG,
                 config: dict[str, options.Options],
                 repo: repository.Repository):
        # pylint: disable=R0913

        self.name = name
        self.profile = profile
        self.dag = dag
        self.config = config
        self.repo = repo
        self.components: dict[str, component_v1.Component] = {}
        self.links: dict[str, link_v1.Link] = {}

        self._lock = threading.Lock()

    def _component(self, name: str) -> component_v1.Component:
        """TODO"""

        if name in self.components:
            return self.components[name]

        component = self.dag.components[name]
        config = self.config.components[name]

        self.components[name] = self.repo.component(component.type)(component.name,
                                                                    component.labels,
                                                                    component.params.processed,
                                                                    config.processed)

        return self.components[name]

    def _link(self, name: str) -> link_v1.Link:
        """TODO"""

        if name in self.links:
            return self.links[name]

        link = self.dag.links[name]
        config = self.config.links[name]

        source = self._component(link.source)
        destination = self._component(link.destination)

        self.links[name] = self.repo.link(link.type)(link.name,
                                                     link.params.processed,
                                                     config.processed,
                                                     source,
                                                     destination)

        return self.links[name]

    def _provider(self) -> provider_v1.Provider:
        """TODO"""

        name, config = self.config.provider
        return self.repo.provider(name)(config)

    def _execute(self, workers: int, callback: Callable[[object], bool]):
        """TODO"""

        def _callback_helper(name: str) -> bool:
            type = name[:name.index("/")]
            name = name[len(type) + 1:]

            return callback(type, name)

        _jobs = []

        for component in self.dag.components.values():
            depends = []

            for inbound_links in component.inbound_links.values():
                depends += [f"link/{link}" for link in inbound_links]

            job = jobs.Job(f"component/{component.name}", depends, _callback_helper)
            _jobs.append(job)

            for outbound_links in component.outbound_links.values():
                for link in outbound_links:
                    depends = [f"component/{component.name}"]
                    job = jobs.Job(f"link/{link}", depends, _callback_helper)
                    _jobs.append(job)

        jobs.execute(workers, _jobs)

    def _generate(self):
        """TODO"""

        def _on_generate(type: str, name: str) -> bool:
            """TODO"""

            with self._lock:
                if type == "component":
                    instance = self._component(name)

                elif type == "link":
                    instance = self._link(name)

                else:
                    assert False

            print(f"generating {name}...", file=sys.stderr)

            return instance.on_generate(self.name, self.profile)

        self._execute(1, _on_generate)

    def build(self, workers: int):
        """TODO"""

        def _on_build(type: str, name: str) -> bool:
            """TODO"""

            with self._lock:
                if type == "component":
                    instance = self._component(name)

                elif type == "link":
                    instance = self._link(name)

                else:
                    assert False

            print(f"building {name}...", file=sys.stderr)

            return instance.on_build(self.name, self.profile)

        self._execute(workers, _on_build)

    def push(self):
        """TODO"""

        artifacts: [str] = []
        artifacts += [component.artifacts for component in self.components.values()]
        artifacts += [link.artifacts for link in self.links.values()]

        self._provider().push(artifacts)

    def apply(self, dry_run: bool, show_manifests: bool):
        """TODO"""

        self._generate()

        manifests: [provider_v1.Manifest] = []

        for name, component in self.components.items():
            manifests.append(provider_v1.Manifest("component", name, component.labels, component.statements))

        for name, link in self.links.items():
            manifests.append(provider_v1.Manifest("link", name, [], link.statements))

        if show_manifests:
            for manifest in manifests:
                print(f"{manifest}:", file=sys.stdout)

        self._provider().apply(self.name, manifests, dry_run)

    def delete(self, dry_run: bool):
        """TODO"""

        self._provider().delete(self.name, dry_run)

    def dot(self) -> str:
        """TODO"""

        return self.dag.dot(self.name)


def _load_provider(profile: profile.Profile,
                   repo: repository.Repository) -> (str, options.Options):
    """TODO"""

    name, config = profile.provider()
    provider = repo.provider(name)

    try:
        config = options.process(provider.configuration(), config)

        for default in config.defaults:
            print(f"WARNING: {name}: {default}: used default value", file=sys.stderr)

        for unused in config.unused:
            print(f"WARNING: {name}: {unused}: unused configuration", file=sys.stderr)

        return name, config

    except exceptions.OptionRequired as exc:
        raise exceptions.ConfigurationRequired("provider", name, str(exc)) from exc


def _load_components(dag: model.DAG,
                     profile: profile.Profile,
                     repo: repository.Repository) -> dict[str, options.Options]:
    """TODO"""

    components = {}

    for component in dag.components.values():
        req_config = repo.component(component.type).configuration()
        _, raw_config = profile.component(component.name)

        try:
            config = options.process(req_config, raw_config)

        except exceptions.OptionRequired as exc:
            raise exceptions.ConfigurationRequired("component", component.name, str(exc)) from exc

        for default in config.defaults:
            print(f"WARNING: {component.name}: {default}: used default value", file=sys.stderr)

        for unused in config.unused:
            print(f"WARNING: {component.name}: {unused}: unused configuration", file=sys.stderr)

        components[component.name] = config

    return components


def _load_links(dag: model.DAG,
                profile: profile.Profile,
                repo: repository.Repository) -> dict[str, options.Options]:
    """TODO"""

    links = {}

    for link in dag.links.values():
        req_config = repo.link(link.type).configuration()
        _, raw_config = profile.link(link.name)

        try:
            config = options.process(req_config, raw_config)

        except exceptions.OptionRequired as exc:
            raise exceptions.ConfigurationRequired("link", link.name, str(exc)) from exc

        for default in config.defaults:
            print(f"WARNING: {link.name}: {default}: used default value", file=sys.stderr)

        for unused in config.unused:
            print(f"WARNING: {link.name}: {unused}: unused configuration", file=sys.stderr)

        links[link.name] = config

    return links


def _load_config(dag: model.DAG,
                 profile: profile.Profile,
                 repo: repository.Repository) -> Configuration:
    """TODO"""

    if dag.revision != profile.revision():
        print("WARNING: profile out of date", file=sys.stderr)

    provider = _load_provider(profile, repo)
    components = _load_components(dag, profile, repo)
    links = _load_links(dag, profile, repo)

    return Configuration(provider, components, links)


def load(name: str,
         components: [str],
         profile_name: str,
         profile: profile.Profile,
         dag: model.DAG,
         repo: repository.Repository) -> Deployment:
    # pylint: disable=R0913

    """TODO"""

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)
    config = _load_config(dag, profile, repo)

    return Deployment(name, profile_name, dag, config, repo)
