# About

bom-configuration is a simple, opinionated python configuration library.

# Usage

This library is useful in the form of an `application` and `library` relationship. That is, your application consumes various libraries and a base configuration is built from the libraries.

In each library, create a `Config`.

```py
# storage library

from bom.configuration import Config

specs = {
  "host": "localhost",
  "port": 5432,
  "password": "password",
}
config = Config.from_dict(specs)

print(config.get("host"))
# prints 'localhost'
```

In the application, create an `AppConfig`.

```py
# application

from bom.configuration import load, AppConfig

specs = {
  "ENV": "prod",
  "app_name": "cool application",
  "app_version": "1.0.0",
}

config: AppConfig = load(specs)

print(config.get("host"))
# prints 'localhost'

print(config.env)
# prints 'prod'
```
