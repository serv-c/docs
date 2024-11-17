import unittest
import uuid
import random

import requests

from tests.launch import stop
from tests.service import simple_start


class TestSimpleMethod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = str(uuid.uuid4())
        cls.port = random.randint(3000, 4000)
        env = {"CONF__BUS__ROUTE": cls.route, "CONF__HTTP__PORT": cls.port}
        cls.container = simple_start(env)

    @classmethod
    def tearDownClass(cls):
        stop(cls.container)

    def test_send_valid_payload(self):
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "test",
                    "inputs": ["a", "b"],
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        id = response.text

        response = requests.get(
            f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)

        value = response.json()
        self.assertEqual(value["progress"], 100)
        self.assertEqual(value["responseBody"], True)
        self.assertEqual(value["statusCode"], 200)
        self.assertEqual(value["isError"], False)

    def test_send_invalid_payload(self):
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "test",
                    "inputs": ["a", "b", 1],
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        id = response.text

        response = requests.get(
            f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)

        value = response.json()
        self.assertEqual(value["progress"], 100)
        self.assertEqual(value["responseBody"], False)
        self.assertEqual(value["statusCode"], 200)
        self.assertEqual(value["isError"], False)
