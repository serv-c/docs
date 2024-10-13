import json
import unittest
import uuid

import pika
import requests

from tests.docker import launch_services, stop_container
from tests.service import simple_start


class TestServicePrefixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.environment, cls.network, cls.services = launch_services(True)
        cls.container = None

        params = pika.URLParameters(cls.environment["BUS_URL_LOCAL"])
        cls.conn = pika.BlockingConnection(params)

    @classmethod
    def tearDownClass(cls):
        stop_container(cls.network, (*cls.services, cls.container))
        cls.conn.close()

    def setUp(self):
        self.route = str(uuid.uuid4())
        self.channel = self.conn.channel()

    def tearDown(self):
        stop_container(self.network, self.container)
        self.container = None
        self.channel.close()

    def test_simple_bind_prefix(self):
        self.container = simple_start(
            {
                **self.environment,
                "CONF__BUS__QUEUE": self.route,
                "CONF__BUS__PREFIX": "test-prefix",
            },
            self.network,
        )

        try:
            self.channel.queue_declare(
                queue="test-prefix" + self.route,
                passive=True,
                durable=True,
                exclusive=False,
            )
        except Exception as e:
            print(e)
            raise Exception("Queue not found")

    def test_send_w_prefix(self):
        prefix = "test_prefix"
        queue = prefix + self.route

        self.channel.queue_declare(queue=queue, durable=True, exclusive=False)

        self.container = simple_start(
            {**self.environment, "CONF__BUS__SENDPREFIX": prefix},
            self.network,
        )

        response = requests.post(
            "http://localhost:3000",
            json={
                "type": "input",
                "route": self.route,
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

        queue = self.channel.queue_declare(
            queue=queue, passive=True, durable=True, exclusive=False
        )
        self.assertEqual(queue.method.message_count, 1)

    def test_send_many_prefix(self):
        routePrefix = {
            "route1": "prefix1",
            "route2": "prefix2",
        }

        for route, prefix in routePrefix.items():
            self.channel.queue_declare(
                queue=prefix + route, durable=True, exclusive=False
            )
            self.channel.queue_declare(queue=route, durable=True, exclusive=False)
        self.container = simple_start(
            {
                **self.environment,
                "CONF__BUS__ROUTEPREFIX": json.dumps(routePrefix),
            },
            self.network,
        )

        for route, prefix in routePrefix.items():
            newRoute = prefix + route
            response = requests.post(
                "http://localhost:3000",
                json={
                    "type": "input",
                    "route": route,
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

            queue = self.channel.queue_declare(
                queue=newRoute, passive=True, durable=True, exclusive=False
            )
            self.assertEqual(queue.method.message_count, 1)
