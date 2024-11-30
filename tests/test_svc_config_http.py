import unittest

import requests

from tests.launch import get_root_path, is_running, launch_app, stop


class TestConfigHTTP(unittest.TestCase):
    def test_port(self):
        configPath = f"{get_root_path()}/config/config.test.yaml"
        with open(configPath, "w+") as f:
            f.write(
                f"""
conf:
  file: {configPath}
  http:
    port: 8000
            """
            )

        container = launch_app(
            environment={"CONF__FILE": configPath},
        )
        self.assertTrue(is_running(container))

        self.assertEqual(
            requests.get("http://localhost:8000", timeout=2.5).status_code, 200
        )
        stop(container)


if __name__ == "__main__":
    unittest.main()
