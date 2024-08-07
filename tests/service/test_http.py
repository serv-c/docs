import unittest
import uuid

import pika
import requests

from tests.docker import ENVIRONMENT, stop_container
from tests.service.test_config_http import simple_start


class TestServiceHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue_name = str(uuid.uuid4())
        cls.route = str(uuid.uuid4())
        cls.container = simple_start(env={"CONF__BUS__QUEUE": cls.route})

    @classmethod
    def tearDownClass(cls):
        if cls.container is not None:
            stop_container(cls.container)
            cls.container = None

    def test_send_payload_to_queue(self):
        params = pika.URLParameters(ENVIRONMENT["BUS_URL"])
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name, durable=True, exclusive=False)

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

        queue = channel.queue_declare(
            queue=self.queue_name, passive=True, durable=True, exclusive=False
        )
        self.assertEqual(queue.method.message_count, 1)

        connection.close()

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
        self.assertEqual(response.status_code, 404)

    def test_retrieving_real_key(self):
        id = str(uuid.uuid4())
        job_submit = requests.post(
            "http://localhost:3000",
            json={
                "type": "input",
                "id": id,
                "route": self.route,
                "argument": {
                    "method": "test-method",
                    "inputs": self.route,
                },
            },
            timeout=2.5,
        )
        self.assertEqual(job_submit.status_code, 200)
        self.assertEqual(job_submit.text, id)

        response = requests.get(f"http://localhost:3000/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response["id"], id)
        self.assertEqual(response["isError"], True)
        self.assertTrue("progress" in response)
        self.assertTrue("statusCode" in response)
        self.assertTrue("responseBody" in response)
