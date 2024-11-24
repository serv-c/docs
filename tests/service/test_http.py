import os
import unittest
import uuid
import random

import pika
import requests

from tests import get_route_message, get_message_body, set_key_value
from tests.launch import stop
from tests.service import simple_start


class TestServiceHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue_name = str(uuid.uuid4())
        cls.route = str(uuid.uuid4())
        cls.port = random.randint(3000, 4000)
        env = {"CONF__BUS__ROUTE": cls.route, "CONF__HTTP__PORT": cls.port}
        cls.container = simple_start(env)

        params = pika.URLParameters(os.environ["BUS_URL"])
        cls.conn = pika.BlockingConnection(params)

    @classmethod
    def tearDownClass(cls):
        channel = cls.conn.channel()
        channel.queue_delete(queue=cls.route)
        cls.conn.close()
        stop(cls.container)

    def setUp(self):
        self.channel = self.conn.channel()

    def tearDown(self):
        self.channel.close()

    def test_send_payload_to_queue(self):
        self.channel.queue_declare(
            queue=self.queue_name, durable=True, exclusive=False)

        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.queue_name,
                "argument": {
                    "method": "test-method",
                    "inputs": self.queue_name,
                },
            },
            timeout=2.5,
        )

        self.assertEqual(response.status_code, 200)

        message, count = get_route_message(self.channel, self.queue_name)
        self.assertEqual(count, 1)

        self.assertEqual(message["type"], "input")
        self.assertEqual(message["route"], self.queue_name)
        self.assertEqual(message["id"], response.text)
        self.assertIn("argumentId", message)

        payload = get_message_body(message)
        self.assertEqual(payload["method"], "test-method")
        self.assertEqual(payload["inputs"], self.queue_name)

    def test_caching(self):
        id = str(uuid.uuid4())
        route = str(uuid.uuid4())
        self.channel.queue_declare(
            queue=route, durable=True, exclusive=False, auto_delete=False
        )
        set_key_value(
            id,
            {
                "id": id,
                "progress": 30,
                "statusCode": 200,
                "isError": True,
                "reponseBody": "test-response",
            }
        )
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": route,
                "id": id,
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
        self.assertEqual(response.text, id)

        _m, count = get_route_message(
            self.channel, self.route, deleteRoute=False)
        self.assertEqual(count, 0)

        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": route,
                "id": id,
                "force": True,
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
        self.assertEqual(response.text, id)

        _m, count = get_route_message(self.channel, self.route)
        self.assertEqual(count, 1)

    def test_send_payload_w_id(self):
        id = str(uuid.uuid4())
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": "api-service",
                "id": id,
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
        self.assertEqual(response.text, id)

    def test_retrieving_fake_key(self):
        response = requests.get(
            f"http://localhost:{self.port}/id/fake-key", timeout=2.5)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())
