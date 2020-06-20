import unittest
import json
import os
import logging

from configuration_builder import ConfigurationBuilder


APP_CONFIG_SAMPLE = {
    "HTTPPort": 8000,
    "Env": 'dev',
    "Logger":
    {
        "Level": "Notice",
        "File": "/tmp/config.out"
    }
}


def get_logger():
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    return logger


def current_dir() -> str:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path


def write_json_to_file(path: str, content: dict):
    with open(path, 'w+') as f:
        json.dump(content, f)


class GetValidConfiguration(unittest.TestCase):
    def setUp(self):
        self.json_file_path = '{0}/settings.json'.format(current_dir())
        write_json_to_file(self.json_file_path, APP_CONFIG_SAMPLE)

        os.environ['API_USER'] = 'Mo'

        self.builder = ConfigurationBuilder(get_logger())

        self.builder.SetBasePath(current_dir()).AddJsonFile(
            'settings.json', optional=False).AddEnvironmentVariables()

        self.config = self.builder.Build()

    def tearDown(self):
        os.remove(self.json_file_path)

    def test_get_from_evironment_variable(self):
        api_user = self.config.Get("API_USER", "G")
        self.assertEqual(api_user, 'Mo')

        for key in os.environ:
            self.assertEqual(os.environ[key], self.config.Get(key))

    def test_get_from_json_file_not_nested(self):
        http_port = self.config.Get("HTTPPort", 9000)
        self.assertEqual(http_port, 8000)

        env = self.config.Get("Env", "prod")
        self.assertEqual(env, "dev")

    def test_get_from_json_file_nested(self):
        logger_level = self.config.Get("Logger:Level", "Info")
        self.assertEqual(logger_level, "Notice")

        logger_file = self.config.Get("Logger:File", ".out")
        self.assertEqual(logger_file, "/tmp/config.out")

    def test_default_config_gets_saved_after_setting_not_nested(self):
        grpc_port = self.config.Get("GrpcPort", 5000)
        self.assertEqual(grpc_port, 5000)

        self.assertEqual(5000, self.config.Get("GrpcPort", 6000))
        self.assertEqual(5000, self.config.Get("GrpcPort"))

    def test_default_config_gets_saved_after_setting_nested(self):
        logger_stream = self.config.Get("Logger:Stream", True)
        self.assertEqual(logger_stream, True)

        self.assertEqual(True, self.config.Get("Logger:Stream", False))
        self.assertEqual(True, self.config.Get("Logger:Stream"))

    def test_get_default_when_none(self):
        test_config = self.config.Get("TEST_CONFIG", "EMPTY")
        self.assertEqual(test_config, "EMPTY")

        api_security = self.config.Get("API_SECURITY", "Test")
        self.assertEqual(api_security, "Test")

        logger_filter = self.config.Get("Logger:Filter")
        self.assertEqual(logger_filter, None)

    def test_get_config_from_env_json_file(self):
        http_port = self.config.Get("HTTPPort", 8080)
        self.assertEqual(http_port, 8000)


class Startup(unittest.TestCase):
    def test_required_json_file_does_not_exist(self):

        builder = ConfigurationBuilder(
            get_logger())

        with self.assertRaises(Exception) as context:
            builder.SetBasePath(current_dir()).AddJsonFile(
                'appsettings.json', optional=False).AddEnvironmentVariables()
        self.assertTrue('config file does not exist' in str(context.exception))

    def test_optional_json_file_does_not_exist(self):

        os.environ['API_USER'] = 'Mo'

        builder = ConfigurationBuilder(
            get_logger())
        config = builder.SetBasePath(current_dir()).AddJsonFile(
            'appsettings.json', optional=True).AddEnvironmentVariables().Build()

        api_user = config.Get('API_USER')
        self.assertEqual(api_user, 'Mo')


class DataError(unittest.TestCase):
    def test_duplicate_key_in_config(self):
        builder = ConfigurationBuilder(
            get_logger())

        # builder.SetBasePath(current_dir()).AddJsonFile(
        #     'appsettings.json', optional=False).AddEnvironmentVariables()


if __name__ == '__main__':
    unittest.main()
