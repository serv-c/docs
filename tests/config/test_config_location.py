import unittest

from tests.docker import (ENVIRONMENT, LINKS, get_container_success,
                          get_root_path, launch_container, stop_container)


class TestConfig(unittest.TestCase):
    def test_misconfigured_config_file_location(self):
        with open(f"{get_root_path()}/config/config.test.yaml", "w+") as f:
            f.write(
                """
conf:
  file: /config/config.yaml
            """
            )

        container = launch_container(
            environment={
                "CONF__FILE": "/config/config.test.yaml",
                **ENVIRONMENT
            },
            links=LINKS
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
            environment={
                "CONF__FILE": "/config/config.test.yaml",
                **ENVIRONMENT
            },
            links=LINKS
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
  url: {ENVIRONMENT["CACHE_URL"]}
bus:
  url: {ENVIRONMENT["BUS_URL"]}
            """
            )

        container = launch_container(
            environment={
                "CONF__FILE": "/config/config.yaml",
            },
            links=LINKS
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
            environment={
                "CONF__FILE": "/config/config.test.yaml",
                **ENVIRONMENT
            },
            links=LINKS
        )
        self.assertTrue(get_container_success(container))
        stop_container(container)


if __name__ == "__main__":
    unittest.main()
