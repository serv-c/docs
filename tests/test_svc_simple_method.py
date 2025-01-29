import os
import time
import unittest
import uuid

import pika
import requests

from tests import get_message_body, get_route_message, simple_start
from tests.launch import is_running, stop


class TestExitOn5xx(unittest.TestCase):
    def test_server_error(self):
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "force": True,
                "argument": {
                    "method": "fail",
                    "inputs": ["a", "b", 1],
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        id = response.text
        time.sleep(10)

        response = requests.get(f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json())

    @classmethod
    def tearDownClass(cls):
        stop(cls.container)

        channel = cls.conn.channel()
        channel.queue_delete(queue=cls.route)
        channel.queue_delete(queue=cls.sendroute)
        channel.close()
        cls.conn.close()

    @classmethod
    def setUpClass(cls):
        cls.route = str(uuid.uuid4())
        cls.sendroute = str(uuid.uuid4())
        cls.port = 3000
        cls.instanceid = str(uuid.uuid4())
        cls.event = "my-event"
        cls.env = {
            "EVENT": cls.event,
            "SEND_ROUTE": cls.sendroute,
            "CONF__BUS__ROUTE": cls.route,
            "CONF__HTTP__PORT": cls.port,
            "CONF__INSTANCEID": cls.instanceid,
        }
        cls.container = simple_start(cls.env)

        params = pika.URLParameters(os.environ["BUS_URL"])
        cls.conn = pika.BlockingConnection(params)


class TestSimpleMethod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = str(uuid.uuid4())
        cls.sendroute = str(uuid.uuid4())
        cls.port = 3000
        cls.instanceid = str(uuid.uuid4())
        cls.event = "my-event"
        cls.env = {
            "EVENT": cls.event,
            "SEND_ROUTE": cls.sendroute,
            "CONF__BUS__ROUTE": cls.route,
            "CONF__HTTP__PORT": cls.port,
            "CONF__INSTANCEID": cls.instanceid,
            "CONF__WORKER__EXITON5XX": "false",
        }
        cls.container = simple_start(cls.env)

        params = pika.URLParameters(os.environ["BUS_URL"])
        cls.conn = pika.BlockingConnection(params)

    @classmethod
    def tearDownClass(cls):
        stop(cls.container)

        channel = cls.conn.channel()
        channel.queue_delete(queue=cls.route)
        channel.queue_delete(queue=cls.sendroute)
        channel.close()
        cls.conn.close()

    def setUp(self):
        self.channel = self.conn.channel()
        if not is_running(self.container):
            self.container = simple_start(self.env)

    def tearDown(self):
        if self.channel.is_open:
            self.channel.close()
        # if is_running(self.container):
        #     stop(self.container)

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
        time.sleep(10)

        response = requests.get(f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)

        value = response.json()
        self.assertEqual(value["progress"], 100)
        self.assertEqual(value["responseBody"], True)
        self.assertEqual(value["statusCode"], 200)
        self.assertEqual(value["isError"], False)

        # message, count = get_route_message(self.channel, self.route)
        # payload = get_message_body(message)["inputs"]

    def test_send_invalid_payload(self):
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
        time.sleep(10)

        response = requests.get(f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)

        value = response.json()
        self.assertEqual(value["progress"], 100)
        self.assertEqual(value["responseBody"], True)
        self.assertEqual(value["statusCode"], 200)
        self.assertEqual(value["isError"], False)

    def test_non_existend_payload(self):
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "test-non-existent-method",
                    "inputs": ["a", "b", 1],
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        id = response.text
        time.sleep(10)

        response = requests.get(f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)

        value = response.json()
        self.assertEqual(value["id"], id)
        self.assertEqual(value["progress"], 100)
        self.assertEqual(value["statusCode"], 404)
        self.assertEqual(value["isError"], True)

    def test_server_error(self):
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "argument": {
                    "method": "fail",
                    "inputs": ["a", "b", 1],
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        id = response.text
        time.sleep(10)

        response = requests.get(f"http://localhost:{self.port}/id/{id}", timeout=2.5)
        self.assertEqual(response.status_code, 200)

        value = response.json()
        self.assertEqual(value["id"], id)
        self.assertEqual(value["progress"], 100)
        self.assertEqual(value["statusCode"], 500)
        self.assertEqual(value["isError"], True)

    def test_send_event(self):
        self.channel.queue_delete(queue=self.sendroute)
        self.channel.queue_declare(
            queue=self.sendroute,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        self.channel.queue_bind(exchange="amq.fanout", queue=self.sendroute)

        inputs = ["a", "b"]
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "force": True,
                "argument": {
                    "method": "test",
                    "inputs": inputs,
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)

        message, count = get_route_message(self.channel, self.sendroute)
        self.assertGreater(count, 0)

        self.assertEqual(message["type"], "event")
        self.assertEqual(message["instanceId"], self.instanceid)
        self.assertEqual(message["event"], self.event)
        self.assertEqual(message["details"], inputs)

    def test_send_message(self):
        self.channel.queue_delete(queue=self.sendroute)
        self.channel.queue_declare(
            queue=self.sendroute,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )

        inputs = 3
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "force": True,
                "argument": {
                    "method": "test",
                    "inputs": inputs,
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)

        message, count = get_route_message(self.channel, self.sendroute)
        self.assertGreater(count, 0)
        payload = get_message_body(message)

        self.assertEqual(message["type"], "input")
        self.assertEqual(message["route"], self.sendroute)

        self.assertEqual(payload["inputs"], inputs)
        self.assertIn("method", payload)

    def test_instanceid_check(self):
        inputs = 3
        instanceId = self.instanceid.upper()
        response = requests.post(
            f"http://localhost:{self.port}",
            json={
                "type": "input",
                "route": self.route,
                "force": True,
                "instanceId": instanceId,
                "argument": {
                    "method": "test",
                    "inputs": inputs,
                },
            },
            timeout=2.5,
        )
        self.assertEqual(response.status_code, 200)
        time.sleep(5)
        stop(self.container)

        message, count = get_route_message(self.channel, self.route)
        self.assertEqual(count, 1)
        self.assertEqual(message["instanceId"], instanceId)


if __name__ == "__main__":
    unittest.main()
