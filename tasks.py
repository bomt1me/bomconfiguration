""" tasks.py """


import os
from pathlib import Path
import sys
import invoke


@invoke.task
def build(ctx):
    """ build """
    ctx.run("rm -rf ./dist")
    ctx.run("pipenv run python setup.py bdist_wheel", echo=True, pty=True)


@invoke.task
def test(ctx):
    """ test """
    pytest_ret = ctx.run(
        "pipenv run pytest --cov-report=xml --cov={0}".format(
            Path(__file__).parent / "src" / "bom_configuration"
        ),
        echo=True,
        warn=True,
        pty=True,
    ).exited
    if pytest_ret and pytest_ret not in (0, 5):
        sys.exit(pytest_ret)
    ctx.run("pipenv run coverage report --fail-under=80 -m", echo=True, pty=True)


@invoke.task
def fmt(ctx):
    """ fmt """
    ctx.run("black . --verbose --exclude='.pyi'", echo=True, pty=True)


@invoke.task
def lint(ctx):
    """ lint """
    ctx.run("pipenv run pyflakes ./src", echo=True)
    ctx.run("pipenv run pyflakes ./tests", echo=True)
    pylint_ret = ctx.run(
        "pipenv run pylint ./src", warn=True, echo=True, pty=True
    ).exited
    if pylint_ret and (1 & pylint_ret or 2 & pylint_ret or 32 & pylint_ret):
        sys.exit(pylint_ret)
    pylint_ret = ctx.run("pipenv run pylint ./tests", warn=True, echo=True).exited
    if pylint_ret and (1 & pylint_ret or 2 & pylint_ret or 32 & pylint_ret):
        sys.exit(pylint_ret)
    ctx.run("pipenv run mypy ./src/bom/configuration", echo=True)
    ctx.run("pipenv run mypy ./tests", echo=True)
    ctx.run("pipenv run black --check --verbose  --exclude='.pyi' ./src", echo=True)
    ctx.run("pipenv run black --check --verbose  --exclude='.pyi' ./tests", echo=True)


@invoke.task(pre=[build])
def publish(ctx):
    """ publish """
    user = os.getenv("PYPI_USERNAME")
    password = os.getenv("PYPI_PASSWORD")
    ctx.run(
        f"pipenv run twine upload dist/* -u {user} -p {password}", echo=True, pty=True
    )
