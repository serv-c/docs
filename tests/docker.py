import os
import random
import time

import docker


def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def launch_container(
    image="servc",
    ports=None,
    config_mount=None,
    environment=None,
    volumes=[],
):
    if ports is None:
        ports = {}
    if environment is None:
        environment = {}
    if config_mount is None:
        config_mount = f"{get_root_path()}/config:/config"
    if volumes is None:
        volumes = []
    volumes = [config_mount, *volumes]

    client = docker.from_env()
    container = client.containers.run(
        image,
        environment=environment,
        detach=True,
        ports=ports,
        volumes=volumes,
    )
    time.sleep(5)
    return container


def get_container_logs(container):
    container.reload()
    return container.logs().decode("utf-8")


def get_container_success(container):
    container.reload()
    if container.status == "exited":
        print(get_container_logs(container))
        return False
    return True


def stop_container(container):
    if container is not None:
        container.stop()
        container.remove()


def launch_services():
    client = docker.from_env()
    client.images.pull("rabbitmq:3")
    client.images.pull("redis")

    rabbitmq_port = random.randint(5000, 8000)
    rabbitmq = launch_container(
        image="rabbitmq:3",
        environment={
            "RABBITMQ_DEFAULT_USER": "rabbitmq",
            "RABBITMQ_DEFAULT_PASS": "rabbitmq",
        },
        ports={"5672/tcp": rabbitmq_port},
    )

    redis_port = random.randint(9000, 11000)
    redis = launch_container(image="redis", ports={"6379/tcp": redis_port})

    environment = {
        "CACHE_URL": f"redis://{redis.name}:6379/0",
        "BUS_URL": f"amqp://rabbitmq:rabbitmq@{rabbitmq.name}",
        "CACHE_URL_LOCAL": f"redis://localhost:{redis_port}/0",
        "BUS_URL_LOCAL": f"amqp://rabbitmq:rabbitmq@localhost:{rabbitmq_port}",
    }

    return environment, (rabbitmq, redis)
