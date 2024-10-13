from tests.docker import get_root_path, launch_container


def simple_start(env, network):
    with open(f"{get_root_path()}/config/config.yaml", "w+") as f:
        f.write("")
    container = launch_container(
        environment=env,
        ports={"3000/tcp": 3000},
        network=network,
    )
    return container
