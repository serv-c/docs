import unittest

from tests.docker import (
    get_container_success,
    get_root_path,
    launch_container,
    launch_services,
    stop_container,
)


class TestConfig(unittest.TestCase):
    def setUpClass(cls):
        cls.environment, cls.services = launch_services()

    @classmethod
    def tearDownClass(cls):
        for service in cls.services:
            stop_container(service)

    def test_misconfigured_config_file_location(self):
        with open(f"{get_root_path()}/config/config.test.yaml", "w+") as f:
            f.write(
                """
conf:
  file: /config/config.yaml
            """
            )

        container = launch_container(
            environment={"CONF__FILE": "/config/config.test.yaml", **self.environment},
        )
        self.assertFalse(get_container_success(container))
        stop_container(container)

    def test_config_file_location(self):
        with open(f"{get_root_path()}/config/config.test.yaml", "w+") as f:
            f.write(
                """
conf:
  file: /config/config.test.yaml
            """
            )

        container = launch_container(
            environment={"CONF__FILE": "/config/config.test.yaml", **self.environment},
        )
        self.assertTrue(get_container_success(container))
        stop_container(container)

    def test_only_config_file_location(self):
        with open(f"{get_root_path()}/config/config.yaml", "w+") as f:
            f.write(
                f"""
conf:
  file: /config/config.test.yaml

cache:
  url: {self.environment["CACHE_URL"]}
bus:
  url: {self.environment["BUS_URL"]}
            """
            )

        container = launch_container(
            environment={
                "CONF__FILE": "/config/config.yaml",
            },
        )
        self.assertTrue(get_container_success(container))
        stop_container(container)

    def test_config_environment_variable(self):
        with open(f"{get_root_path()}/config/config.yaml", "w+") as f:
            f.write(
                """
conf:
  file: /config/config.yaml

cache:
  url: asasds
            """
            )

        container = launch_container(
            environment={"CONF__FILE": "/config/config.test.yaml", **self.environment},
        )
        self.assertTrue(get_container_success(container))
        stop_container(container)


if __name__ == "__main__":
    unittest.main()
