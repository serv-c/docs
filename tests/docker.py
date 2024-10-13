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
    network=None,
):
    if network is None:
        raise Exception("Network is required")
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
    network.connect(container)
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


def stop_container(network, container):
    if container is not None:
        if isinstance(container, list):
            for c in container:
                stop_container(network, c)
            network.remove()
            return
        network.disconnect(container)
        container.stop()
        container.remove()


def launch_services(expose_ports=False):
    client = docker.from_env()
    client.images.pull("rabbitmq:3")
    client.images.pull("redis")

    network_name = f"servc-{random.randint(1000, 9999)}"
    network = client.networks.create(network_name, driver="bridge")

    rabbitmq_port = random.randint(5000, 8000)
    rabbitmq_ports = {"5672/tcp": rabbitmq_port} if expose_ports else None
    rabbitmq = launch_container(
        image="rabbitmq:3",
        environment={
            "RABBITMQ_DEFAULT_USER": "rabbitmq",
            "RABBITMQ_DEFAULT_PASS": "rabbitmq",
        },
        ports=rabbitmq_ports,
        network=network,
    )

    redis_port = random.randint(9000, 11000)
    redis_ports = {"6379/tcp": redis_port} if expose_ports else None
    redis = launch_container(image="redis", ports=redis_ports, network=network)

    environment = {
        "CACHE_URL": "redis://redis:6379/0",
        "BUS_URL": "amqp://rabbitmq:rabbitmq@rabbitmq",
        "CACHE_URL_LOCAL": f"redis://localhost:{redis_port}/0",
        "BUS_URL_LOCAL": f"amqp://rabbitmq:rabbitmq@localhost:{rabbitmq_port}",
    }
    time.sleep(30)

    network.disconnect(rabbitmq)
    network.disconnect(redis)
    network.connect(rabbitmq, aliases=["rabbitmq"])
    network.connect(redis, aliases=["redis"])

    return environment, network, (rabbitmq, redis)
