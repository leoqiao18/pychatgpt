from typing import Optional
import typer
from typing_extensions import Annotated
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import subprocess
import time

from pychatgpt import __app_name__, __version__
from pychatgpt.chatgpt_controller import ChatGPTController


app = typer.Typer()


def version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show the version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    debug: Annotated[
        Optional[bool],
        typer.Option(
            "--debug",
            "-d",
            help="Enable debug mode for more detailed tracing.",
        ),
    ] = None,
) -> None:
    """
    IaC analysis tool.
    """
    logging_level = logging.INFO
    if debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level)


@app.command()
def run1():
    """
    Go to chatgpt in Firefox
    """
    # os.system(
    #     '"~/opt/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"'
    # )
    subprocess.run(["/Users/lqiao/sandbox/test space.sh"])


@app.command()
def prompt(
    chrome_driver_path: Annotated[str, typer.Argument(help="Path to chromedriver")],
    chrome_path: Annotated[str, typer.Argument(help="Path to chrome")],
    prompt: Annotated[str, typer.Argument(help="Prompt for ChatGPT")],
    need_verification: Annotated[
        bool, typer.Option("--verify", help="Prompt for ChatGPT")
    ] = False,
    response_timeout: Annotated[
        int, typer.Option(help="Timeout for ChatGPT response")
    ] = 20,
):
    """
    Automate chatting with ChatGPT in Chrome
    """

    chatgpt = ChatGPTController(
        chrome_path,
        chrome_driver_path,
        need_verification=need_verification,
        response_timeout=response_timeout,
    )

    # Define a prompt and send it to chatgpt
    chatgpt.send_prompt_to_chatgpt(prompt)

    # Retrieve the last response from ChatGPT
    response = chatgpt.return_last_response()
    print(response)

    # Save the conversation to a text file
    # file_name = "conversation.txt"
    # chatgpt.save_conversation(file_name)

    # Close the browser and terminate the WebDriver session
    chatgpt.quit()
