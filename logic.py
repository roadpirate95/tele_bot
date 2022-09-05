import requests
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import USER_AGENT, HEADERS
from aiogram.dispatcher.filters.state import State, StatesGroup
from typing import Union

import pars_html

OPTIONS = webdriver.ChromeOptions().add_argument(f"user-agent={USER_AGENT}")


class Condition(StatesGroup):
    """Object for changing state"""
    waiting_to_find_drugs = State()
    waiting_to_find_digit = State()


class Medicament:
    def __init__(self):
        self.__parser = pars_html.Parser()

    def instructions(self, soup) -> list[str]:
        """Returns drug annotations"""

        self.__parser.set_soup(soup)
        return self.__parser.parser_headers_table()

    @staticmethod
    def numeric_instruction(arr: list[str]) -> list[str]:
        """Returns numeric annotations for the remedy"""

        return [f'{i} : {arr[i]}' for i in range(len(arr))]

    def get_annotation(self, setting_num: int, message) -> str:
        """Returns from annotations on a specified number"""

        all_tags_h2 = self.__parser.get_tags_h2()
        update_tags = self.__parser.update_tags_h2(all_tags_h2)
        list_html_string = self.__parser.arr_lines_html(message)
        resp = self.__parser.resp_annotation(update_tags, list_html_string, setting_num)
        return resp


def create_browser(text: str) -> Union[str, bool]:
    try:
        service: Service = Service("chromedriver.exe")
        driver: webdriver = webdriver.Chrome(service=service, options=OPTIONS)
        driver.get("https://www.rlsnet.ru")
        medicament_input = driver\
            .find_element(by=By.ID, value="search-bar")\
            .find_element(by=By.NAME, value="word")
        medicament_input.send_keys(text)
        medicament_input.send_keys(Keys.ENTER)
        name = driver.find_element(by=By.TAG_NAME, value='div')\
            .find_element(by=By.CLASS_NAME, value="block")\
            .find_element(by=By.TAG_NAME, value='a').text
        link = driver.find_element(by=By.LINK_TEXT, value=name)
        link.send_keys(Keys.ENTER)

        response = requests.get(url=driver.current_url, headers=HEADERS).text

        return response

    except Exception:
        return False
    finally:
        driver.close()
        driver.quit()






