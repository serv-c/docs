import os
import unittest
import uuid
import random

import pika
import requests

from tests import get_route_message, get_message_body
from tests.launch import stop
from tests.service import simple_start


class TestServiceHooksOnComplete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = str(uuid.uuid4())
        cls.port = random.randint(3000, 4000)
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

    def test_simple_push(self):
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
                    "method": "test",
                    "inputs": {
                        "test-key": "test-value",
                    },
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

        message, count = get_route_message(self.channel, route)
        self.assertEqual(count, 1)

        self.assertEqual(message["type"], "input")
        self.assertEqual(message["route"], self.queue_name)
        self.assertEqual(message["id"], response.text)
        self.assertIn("argumentId", message)

        payload = get_message_body(message)
        self.assertEqual(payload["method"], "test-method")
        self.assertEqual(payload["inputs"], self.queue_name)

        inputs = payload["inputs"]
        self.assertEqual(inputs["id"], response.text)
        self.assertEqual(inputs["method"], "test")
        self.assertEqual(inputs["inputs"], {"test-key": "test-value"})
