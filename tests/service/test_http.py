import unittest
import uuid

import pika
import requests

from tests.docker import launch_services, stop_container
from tests.service import simple_start


class TestServiceHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue_name = str(uuid.uuid4())
        cls.route = str(uuid.uuid4())
        cls.environment, cls.network, cls.services = launch_services(True)

        env = {**cls.environment, "CONF__BUS__ROUTE": cls.route}
        cls.container = simple_start(env, cls.network)

        params = pika.URLParameters(cls.environment["BUS_URL_LOCAL"])
        cls.conn = pika.BlockingConnection(params)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        stop_container(cls.network, (*cls.services, cls.container))

    def setUp(self):
        self.channel = self.conn.channel()

    def tearDown(self):
        self.channel.close()

    def test_send_payload_to_queue(self):
        self.channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False)

        response = requests.post(
            "http://localhost:3000",
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

        queue = self.channel.queue_declare(
            queue=self.queue_name, passive=True, durable=True, exclusive=False
        )
        self.assertEqual(queue.method.message_count, 1)

    def test_send_payload_w_id(self):
        id = str(uuid.uuid4())
        response = requests.post(
            "http://localhost:3000",
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
        response = requests.get("http://localhost:3000/id/fake-key", timeout=2.5)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())

