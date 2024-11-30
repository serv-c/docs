import json
import os
import unittest
import uuid

import pika
import requests

from tests import get_route_message
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
        self.port = 3000

    def tearDown(self):
        stop(self.container)
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

        _m, count = get_route_message(self.channel, queue)
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

            _m, count = get_route_message(self.channel, newRoute)
            self.assertEqual(count, 1)
