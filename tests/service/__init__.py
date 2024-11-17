from tests.launch import launch_app, get_root_path


def simple_start(env):
    configPath = f"{get_root_path()}/config/config.test.yaml"
    with open(configPath, "w+") as f:
        f.write("")
    container = launch_app(
        environment={
            **env,
            "CONF__FILE": configPath,
        }
    )
    return container
