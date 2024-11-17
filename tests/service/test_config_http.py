import unittest

import requests

from tests.docker import (
    get_container_success,
    get_root_path,
    launch_container,
    launch_services,
    stop_container,
)
from tests.service import simple_start


class TestConfigHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment, cls.network, cls.services = launch_services()

    @classmethod
    def tearDownClass(cls):
        stop_container(cls.network, cls.services)

    def test_port(self):
        with open(f"{get_root_path()}/config/config.yaml", "w+") as f:
            f.write(
                """
conf:
  file: /config/config.yaml
  http:
    port: 8000
            """
            )

        container = launch_container(
            environment=self.environment,
            ports={"8000/tcp": 8000},
            network=self.network,
        )
        self.assertTrue(get_container_success(container))

        self.assertEqual(
            requests.get("http://localhost:8000", timeout=2.5).status_code, 200
        )
        stop_container(self.network, container)


if __name__ == "__main__":
    unittest.main()
