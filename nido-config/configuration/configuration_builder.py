import os
import json


class Configuration(object):
    def __init__(self, config_builder, separator=':'):
        self.config = config_builder.GetConfig()
        self.separator = separator

    # To refactor. Must precalculate in builder
    def Get(self, key: str, default=None):
        if key in self.config:
            return self.config[key]

        else:
            if self.separator in key:
                keys = key.split(self.separator)

                try:
                    temp = self.config
                    for k in keys:
                        temp = temp[k]
                    return temp
                except:
                    if default:
                        self.config[key] = default
                        return self.config[key]
                    else:
                        return None
            else:
                if default:
                    self.config[key] = default
                    return self.config[key]
                else:
                    return None


class ConfigurationBuilder(object):
    def __init__(self, logger):
        self.config: dict = {}
        self.logger = logger
        self.base_path = self._current_dir()

    def _current_dir(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return dir_path

    # precalculate
    def _add_to_config(self, new_config: dict):
        for key in new_config:
            if key in self.config:
                if self.config[key] == new_config[key]:
                    self.logger.warning(
                        "Config {0} has been set twice in config with same value {1}".format(key, self.config[key]))
                else:
                    self.logger.error(
                        "Config {0} with value {1} has been set already with different value {2}. Will not be set again".format(key, new_config[key], self.config[key]))

            else:
                self.config[key] = new_config[key]

    def AddEnvironmentVariables(self):
        self._add_to_config(os.environ)

        return self

    def AddJsonFile(self, path: str, optional: bool = False):
        file_abs_path = self.base_path + '/' + path
        if not os.path.exists(file_abs_path):
            if not optional:
                raise Exception(
                    "Required {0} config file does not exist".format(file_abs_path))
        else:
            try:
                file = open(file_abs_path)
                config_data = json.load(file)
            except:
                raise Exception(
                    "Unable to open and decode config file {0}".format(file_abs_path))

            self._add_to_config(config_data)
            file.close()

        return self

    def GetConfig(self):
        return self.config

    def Build(self, separator=":"):
        return Configuration(self, separator)

    def SetBasePath(self, path: str):
        if not os.path.exists(path):
            raise Exception("Base path does not exist")
        else:
            self.base_path = path

        return self
