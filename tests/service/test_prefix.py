import json
import unittest
import uuid

import pika
import requests

from tests.docker import ENVIRONMENT, stop_container
from tests.service.test_config_http import simple_start


class TestServicePrefixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.container = None

    @classmethod
    def tearDownClass(cls):
        if cls.container is not None:
            stop_container(cls.container)
            cls.container = None

    def setUp(self):
        self.route = str(uuid.uuid4())

    def tearDown(self):
        if self.container is not None:
            stop_container(self.container)
            self.container = None

    def test_simple_bind_prefix(self):
        self.container = simple_start(
            env={"CONF__BUS__QUEUE": self.route, "CONF__BUS__PREFIX": "test-prefix"}
        )

        params = pika.URLParameters(ENVIRONMENT["BUS_URL"])
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        try:
            channel.queue_declare(
                queue="test-prefix" + self.route,
                passive=True,
                durable=True,
                exclusive=False,
            )
        except Exception as e:
            print(e)
            raise Exception("Queue not found")
        finally:
            connection.close()

    def test_send_w_prefix(self):
        prefix = "test_prefix"
        queue = prefix + self.route

        params = pika.URLParameters(ENVIRONMENT["BUS_URL"])
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True, exclusive=False)

        self.container = simple_start(env={"CONF__BUS__SENDPREFIX": prefix})

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

        queue = channel.queue_declare(
            queue=queue, passive=True, durable=True, exclusive=False
        )
        self.assertEqual(queue.method.message_count, 1)
        connection.close()

    def test_send_many_prefix(self):
        routePrefix = {
            "route1": "prefix1",
            "route2": "prefix2",
        }

        params = pika.URLParameters(ENVIRONMENT["BUS_URL"])
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        for route, prefix in routePrefix.items():
            channel.queue_declare(queue=prefix + route, durable=True, exclusive=False)
            channel.queue_declare(queue=route, durable=True, exclusive=False)
        self.container = simple_start(
            env={
                "CONF__BUS__ROUTEPREFIX": json.dumps(routePrefix),
            }
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

            queue = channel.queue_declare(
                queue=newRoute, passive=True, durable=True, exclusive=False
            )
            self.assertEqual(queue.method.message_count, 1)
        connection.close()
