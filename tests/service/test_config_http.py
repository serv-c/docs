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
        cls.container = simple_start(cls.environment, cls.network)

    @classmethod
    def tearDownClass(cls):
        stop_container(cls.network, (*cls.services, cls.container))
        cls.container = None

    def test_send_payload_no_id(self):
        response = requests.post(
            "http://localhost:3000",
            json={
                "type": "input",
                "route": "api-service",
                "argument": {
                    "method": "test-method",
                    "inputs": {
                        "test-key": "test-value",
                    },
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.text, "")
        self.assertNotEqual(response.text, "0")

    def test_port(self):
        if self.container is not None:
            stop_container(self.network, self.container)
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
        self.container = None
        simple_start(self.environment, self.network)


if __name__ == "__main__":
    unittest.main()
