# pychatgpt

Automation for prompting ChatGPT in Chrome.

## Prerequisites

1. The project is built with `poetry`. You need to install it, and run `poetry install` in the project root once.
2. You need the `chromedriver` and corresponding version of Chrome. As of the latest version, the Chrome will need to be some version of `Google Chrome for Testing`.

## Usage

```shell
poetry run pychatgpt prompt [--verify] CHROME_DRIVER_PATH CHROME_PATH PROMPT
```