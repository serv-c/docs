from subprocess import Popen, PIPE, STDOUT
import time
import os


def get_root_path():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def launch_app(environment: None | dict = None):
    current_env = os.environ
    if environment is not None:
        for key, value in environment.items():
            current_env[key] = str(value)

    process = Popen(os.environ.get("START_SCRIPT"),
                    env=current_env, stdout=PIPE, stderr=STDOUT)
    time.sleep(10)
    return process


def get_logs(process: Popen):
    return process.stdout.read().decode("utf-8")


def is_running(process: Popen):
    return process.poll() is None


def get_exit_status(process: Popen):
    if process.poll() is None:
        stop(process)
        return True

    if process.returncode:
        print(get_logs(process))
        return False
    return True


def stop(process: Popen | None):
    if process:
        process.terminate()
        process.kill()
        time.sleep(1)
