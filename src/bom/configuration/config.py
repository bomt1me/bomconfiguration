""" config.py """


import pyhocon

from . import environment  # pylint: disable=import-error


class Config(pyhocon.ConfigTree):
    """ Config """

    @property
    def env(self) -> environment.Environment:
        """ env """

        env_found = self.get_string("env")
        return environment.get_env(env_found)

    @property
    def app_name(self) -> str:
        """ app_name """

        return str(self.get_string("app_name"))

    @property
    def app_version(self) -> str:
        """ app_version """

        return str(self.get_string("app_version"))
