import os
import json
import time
from redis import Redis


def get_route_message(channel, route, deleteRoute=True):
    time.sleep(5)
    queue = channel.queue_declare(
        queue=route,
        passive=True,
        durable=True,
        exclusive=False,
        auto_delete=False,
    )
    count = queue.method.message_count
    body = None

    if count:
        _m, _h, body = channel.basic_get(route)
    if deleteRoute:
        channel.queue_delete(queue=route)
    if body:
        body = json.loads(body.decode("utf-8"))
    return body, count


def set_key_value(key, value):
    redis = Redis.from_url(os.environ["CACHE_URL"])
    redis.set(key, json.dumps(value))
    redis.close()


def get_key_value(key):
    redis = Redis.from_url(os.environ["CACHE_URL"])
    value = redis.get(key)
    if value:
        value = json.loads(value)
    redis.close()
    return value


def get_message_body(message):
    return get_key_value(message["argumentId"])
