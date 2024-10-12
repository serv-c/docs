import unittest

import requests

from tests.docker import (
    get_container_success,
    get_root_path,
    launch_container,
    launch_services,
    stop_container,
)


def simple_start(env):
    with open(f"{get_root_path()}/config/config.yaml", "w+") as f:
        f.write("")
    container = launch_container(
        environment=env,
        ports={"3000/tcp": 3000},
    )
    return container


class TestConfigHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment, cls.services = launch_services()
        cls.container = simple_start(cls.environment)

    @classmethod
    def tearDownClass(cls):
        for service in cls.services:
            stop_container(service)
        if cls.container is not None:
            stop_container(cls.container)
            cls.container = None

    # def setUp(self):
    #     cwd = os.getcwd()
    #     os.chdir("sample_data")
    #     call(["python3", "load_existing.py"], stdout=PIPE, stderr=PIPE)
    #     os.chdir(cwd)

    def test_send_payload_no_id(self):
        # params = pika.URLParameters(ENVIRONMENT["BUS_URL"])
        # connection = pika.BlockingConnection(params)
        # channel = connection.channel()
        # connection.close()
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
            stop_container(self.container)
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
        )
        self.assertTrue(get_container_success(container))

        self.assertEqual(
            requests.get("http://localhost:8000", timeout=2.5).status_code, 200
        )
        stop_container(container)
        self.container = None
        simple_start()


if __name__ == "__main__":
    unittest.main()
