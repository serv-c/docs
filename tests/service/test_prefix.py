import os
import json
import unittest
import uuid
import random

import pika
import requests

from tests.launch import stop
from tests.service import simple_start


class TestServicePrefixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.container = None
        params = pika.URLParameters(os.environ["BUS_URL"])
        cls.conn = pika.BlockingConnection(params)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        stop(cls.container)

    def setUp(self):
        self.route = str(uuid.uuid4())
        self.channel = self.conn.channel()
        self.port = random.randint(3000, 4000)

    def tearDown(self):
        stop(self.container)
        self.container = None
        if self.channel.is_open:
            self.channel.close()

    def test_simple_bind_prefix(self):
        self.container = simple_start(
            {
                "CONF__BUS__ROUTE": self.route,
                "CONF__BUS__PREFIX": "test-prefix",
                "CONF__HTTP__PORT": self.port,
            },
        )

        self.channel.queue_declare(
            queue="test-prefix" + self.route,
            passive=True,
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
        self.channel.queue_delete(queue="test-prefix" + self.route)

    def test_send_w_prefix(self):
        prefix = "test_prefix"
        queue = prefix + self.route

        self.channel.queue_declare(
            queue=queue, durable=True, exclusive=False, auto_delete=False
        )

        self.container = simple_start(
            {
                "CONF__BUS__PREFIX": prefix,
                "CONF__HTTP__PORT": self.port,
            },
        )

        response = requests.post(
            f"http://localhost:{self.port}",
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
            queue=queue, passive=True, durable=True, exclusive=False, auto_delete=False
        )
        count = queue.method.message_count
        self.channel.queue_delete(queue=queue.method.queue)
        self.assertEqual(count, 1)

    def test_send_many_prefix(self):
        routePrefix = {
            "route1": "prefix1",
            "route2": "prefix2",
        }

        for route, newRoute in routePrefix.items():
            self.channel.queue_declare(
                queue=newRoute, durable=True, exclusive=False, auto_delete=False
            )
            self.channel.queue_declare(
                queue=route, durable=True, exclusive=False, auto_delete=False
            )
        self.container = simple_start(
            {
                "CONF__BUS__ROUTEMAP": json.dumps(routePrefix),
                "CONF__HTTP__PORT": self.port,
            },
        )

        for route, newRoute in routePrefix.items():
            response = requests.post(
                f"http://localhost:{self.port}",
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
                queue=newRoute,
                passive=True,
                durable=True,
                exclusive=False,
                auto_delete=False,
            )
            count = queue.method.message_count
            self.channel.queue_delete(queue=newRoute)
            self.assertEqual(count, 1)
