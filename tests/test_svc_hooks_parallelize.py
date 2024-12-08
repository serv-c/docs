import os
import time
import unittest
import uuid

import pika
import requests

from tests import get_message_body, get_route_message, simple_start
from tests.launch import stop


class TestServiceHooksParallelize(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = str(uuid.uuid4())
        cls.port = 3000
        cls.container = simple_start(
            {
                "CONF__BUS__ROUTE": cls.route,
                "CONF__HTTP__PORT": cls.port,
            }
        )
        params = pika.URLParameters(os.environ["BUS_URL"])
        cls.conn = pika.BlockingConnection(params)

    @classmethod
    def tearDownClass(cls):
        stop(cls.container)
        channel = cls.conn.channel()
        channel.queue_delete(queue=cls.route)
        channel.close()
        cls.conn.close()

    def setUp(self):
        self.channel = self.conn.channel()

    def tearDown(self):
        if self.channel.is_open:
            self.channel.close()

    def test_part_blocks_complete_hook(self):
        routes = []
        for route in range(2):
            route = str(uuid.uuid4())
            routes.append(route)
            self.channel.queue_declare(
                queue=route,
                durable=True,
                exclusive=False,
                auto_delete=False,
            )
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "test",
                    "inputs": {
                        "test-key": "test-value",
                    },
                    "hooks": {
                        "part": {
                            "part_id": 3,
                            "total_parts": 10,
                            "part_queue": routes[0],
                        },
                        "on_complete": [
                            {
                                "type": "sendmessage",
                                "route": routes[1],
                                "method": "test-method",
                            }
                        ],
                    },
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)

        _m, count = get_route_message(
            self.channel, self.route, deleteRoute=False)
        self.assertEqual(count, 0)

        _m, count = get_route_message(self.channel, routes[0])
        self.assertEqual(count, 1)

        _m, count = get_route_message(self.channel, routes[1])
        self.assertEqual(count, 0)

    def test_part_continue_complete_hook(self):
        routes = []
        for route in range(2):
            route = str(uuid.uuid4())
            routes.append(route)
            self.channel.queue_declare(
                queue=route,
                durable=True,
                exclusive=False,
                auto_delete=False,
            )
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "test",
                    "inputs": {
                        "test-key": "test-value",
                    },
                    "hooks": {
                        "part": {
                            "part_id": 1,
                            "total_parts": 1,
                            "part_queue": routes[0],
                        },
                        "on_complete": [
                            {
                                "type": "sendmessage",
                                "route": routes[1],
                                "method": "test-method",
                            }
                        ],
                    },
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)

        _m, count = get_route_message(
            self.channel, self.route, deleteRoute=False)
        self.assertEqual(count, 0)

        # the on_complete hook should be executed
        _m, count = get_route_message(self.channel, routes[1])
        self.assertEqual(count, 1)

        # the part queue should be empty and deleted
        try:
            get_route_message(self.channel, routes[0])
            self.fail("The part queue should be empty and deleted")
        except:
            pass

    def test_full_job(self):
        route = str(uuid.uuid4())
        self.channel.queue_declare(
            queue=route,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "hook",
                    "inputs": ["a", "b", "c"],
                    "hooks": {
                        "on_complete": [
                            {
                                "type": "sendmessage",
                                "route": route,
                                "method": "test-method",
                            }
                        ]
                    },
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)

        # the message should be consumed by the route
        _m, count = get_route_message(
            self.channel, self.route, deleteRoute=False)
        self.assertEqual(count, 0)

        # the on_complete hook should be executed
        time.sleep(20)
        message, count = get_route_message(self.channel, route)
        self.assertEqual(count, 1)
        self.assertEqual(message["type"], "input")
        self.assertEqual(message["route"], route)
        self.assertIn("argumentId", message)

        # the caller should not know that the underlying method
        # was parallelized
        payload = get_message_body(message)
        inputs = payload["inputs"]
        self.assertEqual(payload["method"], "test-method")
        self.assertEqual(inputs["id"], response.text)
        self.assertEqual(inputs["method"], "hook")
        self.assertEqual(inputs["inputs"], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
