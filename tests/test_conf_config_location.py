import os
import unittest

from tests.launch import get_exit_status, get_root_path, launch_app


class TestConfig(unittest.TestCase):
    def test_misconfigured_config_file_location(self):
        configPath = f"{get_root_path()}/config/config.test.yaml"
        with open(configPath, "w+") as f:
            f.write(
                """
    conf:
      file: /config/config.yaml
                """
            )

        container = launch_app(
            environment={"CONF__FILE": configPath},
        )
        self.assertFalse(get_exit_status(container))

    def test_config_file_location(self):
        configPath = f"{get_root_path()}/config/config.test.yaml"
        with open(configPath, "w+") as f:
            f.write(
                f"""
conf:
  file: {configPath}
            """
            )

        container = launch_app(
            environment={"CONF__FILE": configPath},
        )
        self.assertTrue(get_exit_status(container))

    def test_only_config_file_location(self):
        configPath = f"{get_root_path()}/config/config.test.yaml"
        with open(configPath, "w+") as f:
            f.write(
                f"""
conf:
  file: {configPath}

  cache:
    url: {os.environ["CACHE_URL"]}
  bus:
    url: {os.environ["BUS_URL"]}
            """
            )

        container = launch_app(
            environment={"CONF__FILE": configPath},
        )
        self.assertTrue(get_exit_status(container))

    def test_config_environment_variable(self):
        configPath = f"{get_root_path()}/config/config.test.yaml"
        with open(configPath, "w+") as f:
            f.write(
                f"""
conf:
  file: {configPath}

  cache:
    url: asasds
            """
            )

        container = launch_app(
            environment={
                "CONF__CACHE__URL": os.environ["CACHE_URL"],
                "CONF__FILE": configPath,
            },
        )
        self.assertTrue(get_exit_status(container))


if __name__ == "__main__":
    unittest.main()
