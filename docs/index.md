# bom-configuration

![pipeline](https://github.com/bomt1me/bomconfiguration/actions/workflows/dev.yml/badge.svg)

Welcome to bom-configuration. This is an opinionated configuration library that will build a configuration from environment variables, command line arguments, local files, and global files.

## usage

To start, you must define the environment you are using. The available environments are `dev`, `qa`, and `prod`. If you do not define an environment, you will receive an error.

```py
>>> from bom.configuration import load
>>> load()
...
ValueError: `ENV` environment variable must be specified.
```

```sh
$ export ENV=dev
```

```py
>>> from bom.configuration import load
>>> conf = load()
{'bom': {'configuration': {'version': '1.0.0'}}}
```

To modify the configuration, create a `bom.conf.json` file in the python library or create it inside the working directory of the application.
