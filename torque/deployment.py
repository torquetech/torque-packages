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
from torque import v1


Configuration = namedtuple("Configuration", [
    "providers",
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

        self._name = name
        self._profile = profile
        self._dag = dag
        self._config = config
        self._repo = repo

        self._components: dict[str, v1.component.Component] = {}
        self._links: dict[str, v1.link.Link] = {}
        self._providers: dict[str, v1.provider.Provider] = {}

        self._lock = threading.Lock()

    def _path(self) -> str:
        """TODO"""

        return f"{v1.utils.torque_dir()}/local/deployments/{self._name}"

    def _component(self, name: str) -> v1.component.Component:
        """TODO"""

        if name in self._components:
            return self._components[name]

        config = self._config.components[name]
        component = self._dag.components[name]

        component = self._repo.component(component.type)(component.name,
                                                         component.labels,
                                                         component.parameters,
                                                         config)

        self._components[component.name] = component
        return component

    def _link(self, name: str) -> v1.link.Link:
        """TODO"""

        if name in self._links:
            return self._links[name]

        config = self._config.links[name]
        link = self._dag.links[name]

        source = self._component(link.source)
        destination = self._component(link.destination)

        link = self._repo.link(link.type)(link.name,
                                          link.parameters,
                                          config,
                                          source,
                                          destination)

        self._links[link.name] = link
        return link

    def _provider(self, meta: v1.metadata.Deployment, name: str) -> v1.provider.Provider:
        """TODO"""

        if name in self._providers:
            return self._providers[name]

        config = self._config.providers[name]
        provider = self._repo.provider(name)(meta, config)

        self._providers[name] = provider
        return provider

    def _execute(self, workers: int, callback: Callable[[object], bool]):
        """TODO"""

        def _callback_helper(name: str) -> bool:
            type = name[:name.index("/")]
            name = name[len(type) + 1:]

            return callback(type, name)

        _jobs = []

        for component in self._dag.components.values():
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

    def build(self, workers: int):
        """TODO"""

        meta = v1.metadata.Deployment(self._name, self._profile, False, self._path())
        deployment = v1.deployment.create(meta, [])

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

            return instance.on_build(deployment)

        self._execute(workers, _on_build)

    def apply(self, workers: int, dry_run: bool):
        """TODO"""

        meta = v1.metadata.Deployment(self._name, self._profile, dry_run, self._path())
        providers = [self._provider(meta, provider) for provider in self._config.providers.keys()]
        deployment = v1.deployment.create(meta, providers)

        def _on_apply(type: str, name: str) -> bool:
            """TODO"""

            with self._lock:
                if type == "component":
                    instance = self._component(name)

                elif type == "link":
                    instance = self._link(name)

                else:
                    assert False

            print(f"applying {name}...", file=sys.stderr)

            return instance.on_apply(deployment)

        self._execute(workers, _on_apply)

        for provider in providers:
            provider.on_apply()

    def delete(self, dry_run: bool):
        """TODO"""

    def dot(self) -> str:
        """TODO"""

        return self._dag.dot(self._name)


def _provider_config(provider: str,
                     profile: profile.Profile,
                     repo: repository.Repository) -> object:
    """TODO"""

    config = profile.provider(provider)

    try:
        return repo.provider(provider).validate_configuration(config or {})

    except RuntimeError as exc:
        raise RuntimeError(f"provider: {provider}: {exc}") from exc


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

    providers = {
        provider: _provider_config(provider, profile, repo)
        for provider in profile.providers()
    }

    components = {
        component.name: _component_config(component, profile, repo)
        for component in dag.components.values()
    }

    links = {
        link.name: _link_config(link, profile, repo)
        for link in dag.links.values()
    }

    config = Configuration(providers, components, links)

    return Deployment(name, profile.name, dag, config, repo)
