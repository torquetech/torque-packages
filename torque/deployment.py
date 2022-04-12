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
from torque import profile
from torque import repository

from torque.v1 import component as component_v1
from torque.v1 import link as link_v1
from torque.v1 import provider as provider_v1


Configuration = namedtuple("Configuration", [
    "provider",
    "components",
    "links"
])


class Deployment:
    # pylint: disable=R0902

    """TODO"""

    def __init__(self,
                 name: str,
                 profile: str,
                 dag: model.DAG,
                 config: Configuration,
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
        component = self.repo.component(component.type)(component.name,
                                                        component.labels,
                                                        component.parameters)

        config = self.config.components[component.name]
        component.on_initialize(config)

        self.components[component.name] = component
        return component

    def _link(self, name: str) -> link_v1.Link:
        """TODO"""

        if name in self.links:
            return self.links[name]

        link = self.dag.links[name]

        source = self._component(link.source)
        destination = self._component(link.destination)

        link = self.repo.link(link.type)(link.name,
                                         link.parameters,
                                         source,
                                         destination)

        config = self.config.links[link.name]
        link.on_initialize(config)

        self.links[link.name] = link
        return link

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


def _provider_config(profile: profile.Profile,
                     repo: repository.Repository) -> object:
    """TODO"""

    name, config = profile.provider()

    try:
        return name, repo.provider(name).validate_configuration(config or {})

    except RuntimeError as exc:
        raise RuntimeError(f"provider: {name}: {exc}") from exc


def _component_config(component: model.Component,
                      profile: profile.Profile,
                      repo: repository.Repository) -> object:
    """TODO"""
    config = profile.component(component.name)

    try:
        return repo.component(component.type).validate_configuration(config or {})

    except RuntimeError as exc:
        raise RuntimeError(f"component: {component.name}: {exc}") from exc


def _link_config(link: model.Link,
                 profile: profile.Profile,
                 repo: repository.Repository) -> object:
    """TODO"""
    config = profile.link(link.name)

    try:
        return repo.link(link.type).validate_configuration(config or {})

    except RuntimeError as exc:
        raise RuntimeError(f"link: {link.name}: {exc}") from exc


def load(name: str,
         components: [str],
         profile: profile.Profile,
         dag: model.DAG,
         repo: repository.Repository) -> Deployment:
    # pylint: disable=R0913

    """TODO"""

    if dag.revision != profile.revision():
        print("WARNING: profile out of date", file=sys.stderr)

    if components is not None and len(components) == 0:
        raise exceptions.NoComponentsSelected()

    dag = dag.subset(components)
    provider = _provider_config(profile, repo)

    components = {
        component.name: _component_config(component, profile, repo)
        for component in dag.components.values()
    }

    links = {
        link.name: _link_config(link, profile, repo)
        for link in dag.links.values()
    }

    config = Configuration(provider, components, links)

    return Deployment(name, profile.name, dag, config, repo)
