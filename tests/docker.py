import os
import time

import docker

ENVIRONMENT = {
    "CACHE_URL": "redis://redis:6379/0",
    "BUS_URL": "amqp://rabbitmq:rabbitmq@rabbitmq",
}
LINKS = {
    "redis": "redis",
    "rabbitmq": "rabbitmq",
}


def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def launch_container(
    ports=None, config_mount=None, environment=None, links=None, volumes=[]
):
    if ports is None:
        ports = {}
    if links is None:
        links = {}
    if environment is None:
        environment = {}
    if config_mount is None:
        config_mount = f"{get_root_path()}/config:/config"
    if volumes is None:
        volumes = []
    volumes = [config_mount, *volumes]

    client = docker.from_env()
    container = client.containers.run(
        "servc",
        environment=environment,
        detach=True,
        links=links,
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
    container.stop()
    container.remove()
