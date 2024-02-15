"""pychatgpt entry point script"""

# pychatgpt/__main__.py

from pychatgpt import cli, __app_name__


def main() -> None:
    cli.app(prog_name=__app_name__)
