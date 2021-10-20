import logging
import os
import re
from logging.handlers import RotatingFileHandler

import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# from webdriver_manager.firefox import GeckoDriverManager  # pip install webdriver-manager
from selenium.webdriver import Firefox, ActionChains
from webdriver_manager.firefox import GeckoDriverManager


def set_browser(web_driver=None):

    if not web_driver:
        web_driver = GeckoDriverManager().install()

    """set basic browser settings"""
    options = Options()
    options.headless = True
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-extension")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("no-sandbox")
    options.add_argument("--start-maximized")
    try:
        browser = Firefox(executable_path=web_driver, options=options,  # firefox_binary=binary,
                          log_path=os.path.join('geckodriver.log'))
        browser.fullscreen_window()
        ActionChains(browser).send_keys(Keys.F11).perform()
        return browser
    except ValueError:
        print('Please check if you have FireFox installed!')
        return None


def set_logger(file_name=os.path.join('ceneo_crawler.log'), verbose=True, file_verbose=True):
    logger = logging.getLogger(__name__)
    # logger.propagate = False

    formatter = logging.Formatter('%(asctime)s: %(message)s')

    if verbose:
        level = logging.INFO
        handler = logging.StreamHandler()
    else:
        level = logging.NOTSET
        handler = logging.NullHandler()

    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if file_verbose:
        file_handler = RotatingFileHandler(file_name, maxBytes=2000000, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.setLevel(level)

    return logger


logger = set_logger()


def get_logger():
    return logger


def read_csv(file: str) -> pd.DataFrame:
    return pd.read_csv(file, quoting=1, sep=';', encoding='utf-8')


def append_row_to_csv(file: str, row: dict) -> None:
    out = pd.DataFrame([[value for value in row.values()]], columns=[key for key in row.keys()])
    if os.path.exists(file):
        out.to_csv(file, mode='a', header=False, quoting=1, index=False, encoding='UTF-8')
    else:
        out.to_csv(file, mode='w', header=True, quoting=1, index=False, encoding='UTF-8')

