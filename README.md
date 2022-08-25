# Torque

## Custom DevOps Setups

Torque gives you a turn-key custom DevOps Setup designed by you to match your needs. No buildout costs. No vendor lock-in. 

Torque professionals help you design the system, pick components, links, and providers you need, and then guide you step-by-step to set it all up with accounts, credentials, passwords, tokens, and permissions. And finally, Torque provides ongoing code upgrades with bug fixes, security patches, and new functionality, so you do not need to worry about it.

To get your own custom-built Torque's package with DevOps Setup, visit [Torque's website](https://torquetech.io).

## Torque's workspace tool

**Note:** This README file represents a high-level overview of what Torque is when you need it, and what to expect from Torque. All the details of how to install and use Torque are in the [documentation](https://docs.torquetech.io).

End-to-end automated components for all your development and deployment tools. From local development environment to production resources. Customizable, any way you like.

For the first time, cloud systems exhibit a feature they had never before: plasticity.

[Torque documentation](https://docs.torquetech.io/) provides step-by-step guides on how Torque converts lengthy complex initiatives to build and maintain software systems into single-command-line executions.

## How to manage your software systems with Torque?

### 1. Install a Torque package

```
$ torque package install git+https://github.com/torquetech/demo-package
```

Torque packages contain system components and links, together with infrastructure providers.
Now components can be backend services, frontend applications, databases, message queues, background workers and so. While infrastructure providers are usually `docker-compose`, `k8s`, and `terraform`.

You can install as many packages as you need.

### 2. Define cloud system design

Now, developers define cloud system design through Torque system components like frontends, backends, databases, message queues, and workers.

For example,

```
$ torque component create events_db demo/postgres
```

adds Postgres as a system component. And

```
$ torque component create events_service demo/python-service -p path=events-service
```

adds a Python service system component.

Finally, we simply create a link between these two components. Links take care of providing code and configuration.

```
$ torque link create events_db events_service --type demo/psycopg
```

### 3. Code, test, run locally, build and deploy the entire system

Since Torque automation packages contain all they need to execute the components and links using different infrastructure providers, all you need to do is run `build` and `apply` commands for the desired provider. Of course, the provider for a local environment is usually `docker-compose`

```
$ torque deployment build docker-compose
$ torque deployment apply docker-compose
```

And deploying to the cloud is as easy as using a different provider.

```
$ torque deployment build kubernetes
$ torque deployment apply kubernetes
```

### 4. Visualize your cloud system

This is what the example from the documentation looks like when you run

```
$ torque deployment dot docker-compose | dot -Tpng -o docker-compose.png
```

and open the generated `docker-compose.png` file.

<img src="https://docs.torquetech.io/_images/dag.png" alt="System design diagram" width="70%"/>

## Torque packages are extensible and customizable

Torque packages are Python PyPI packages that implement the Torque Execution Framework. You can make your packages, or extend existing packages. Python offers a lot of ways to accomplish extensibility. And a dynamic nature of language enables you to do that on the fly by re-running the tool after a change.

You can automate all your tools, any way you like.

## Find out more about Torque

There is much more fun stuff to learn about Torque.
Use the following resources to learn how to use the Torque tool and connect with the Torque community.

- [Installation instructions](https://docs.torquetech.io/1-installation/index.html)
- [Torque Documentation](https://docs.torquetech.io)
- [Discussions](/discussions)
- [Issues](/issues)

You can also:

- ⭐ Star this repo to show your interest/support.
- 📫 Stay updated by subscribing to our [email list](https://torquetech.io/#comp-l3afcozr).

If you would like to start using Torque for your project(s), we would love to hear how you plan to use it. Email us at team@torquetech.io

## LICENSE note

While this package is distributed under [Mozilla Public License 2.0](https://www.mozilla.org/en-US/MPL/2.0/), it includes a modified version of [schema.py](https://github.com/keleshev/schema/blob/09c00eda9599e53f7e6b84d7c91ecd3b42f71772/schema.py) which is distributed under [MIT license](https://mit-license.org/license.txt).
