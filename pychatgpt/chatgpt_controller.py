import os
import socket
import threading
import time
import subprocess
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)


class ChatGPTController:

    def __init__(
        self,
        chrome_path,
        chrome_driver_path,
        need_verification=True,
        response_timeout=20,
    ):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path
        self.need_verification = need_verification
        self.response_timeout = response_timeout

        url = r"https://chat.openai.com"
        free_port = self.find_available_port()
        self.launch_chrome_with_remote_debugging(free_port, url)
        if self.need_verification:
            self.wait_for_human_verification()
        else:
            time.sleep(2)
        self.driver = self.setup_webdriver(free_port)

    @staticmethod
    def find_available_port():
        """This function finds and returns an available port number on the local machine by creating a temporary
        socket, binding it to an ephemeral port, and then closing the socket."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_with_remote_debugging(self, port, url):
        """Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
        provided url"""

        def open_chrome():
            # chrome_cmd = f"{self.chrome_path} --remote-debugging-port={port} --user-data-dir=remote-profile {url}"
            # os.system(chrome_cmd)
            chrome_cmd = [
                self.chrome_path,
                f"--remote-debugging-port={port}",
                "--user-data-dir=remote-profile",
                url,
            ]
            subprocess.run(chrome_cmd)

        self.chrome_thread = threading.Thread(target=open_chrome)
        self.chrome_thread.start()

    def setup_webdriver(self, port):
        """Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
        with remote debugging enabled on the specified port"""

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = self.chrome_driver_path
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def send_prompt_to_chatgpt(self, prompt):
        """Sends a message to ChatGPT and waits for [response_timeout] seconds for the response"""

        input_box = self.driver.find_element(
            by=By.XPATH, value='//textarea[contains(@id, "prompt-textarea")]'
        )
        self.driver.execute_script(f"arguments[0].value = '{prompt}';", input_box)
        input_box.send_keys(Keys.RETURN)
        input_box.submit()
        time.sleep(self.response_timeout)

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """

        return self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text-base")

    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        delimiter = "|^_^|"
        chatgpt_conversation = self.return_chatgpt_conversation()
        with open(os.path.join(directory_name, file_name), "a") as file:
            for i in range(0, len(chatgpt_conversation), 2):
                file.write(
                    f"prompt: {chatgpt_conversation[i].text}\nresponse: {chatgpt_conversation[i + 1].text}\n\n{delimiter}\n\n"
                )

    def return_last_response(self):
        """:return: the text of the last chatgpt response"""

        response_elements = self.driver.find_elements(
            by=By.CSS_SELECTOR, value="div.text-base"
        )
        return response_elements[-1].text.split("\n", 1)[1]

    @staticmethod
    def wait_for_human_verification():
        logger.info(
            "You need to manually complete the log-in or the human verification if required."
        )

        while True:
            logger.info(
                "Enter 'y' if you have completed the log-in or the human verification: "
            )
            user_input = input().lower()

            if user_input == "y":
                logger.info("Continuing with the automation process...")
                break
            else:
                logger.info(
                    "Invalid input. Please enter 'y' if you have completed the log-in or the human verification."
                )

    def quit(self):
        """Closes the browser and terminates the WebDriver session."""
        logger.info("Closing the browser...")
        self.driver.close()
        self.driver.quit()
