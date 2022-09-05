import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from config import USER_AGENT, HEADERS
from aiogram.dispatcher.filters.state import State, StatesGroup
from typing import Union


options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={USER_AGENT}")


def create_browser(text: str) -> Union[str, bool]:
    try:
        service: Service = Service("chromedriver.exe")
        driver: webdriver = webdriver.Chrome(service=service, options=options)
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


class Medicament:

    def __init__(self):
        self.soup = None
        self.table_headers_text = []

    def set_soup(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def instructions(self) -> list[str]:
        """Returns drug annotations"""

        if len(self.table_headers_text) == 0:
            table_headers = self.soup.find("div", class_="noprint").find_all("li")
            for i in table_headers:
                self.table_headers_text.append(i.text)
                if 'Условия хранения' in i.text:
                    break
        return self.table_headers_text

    @staticmethod
    def numeric_instruction(arr: list[str]) -> list[str]:
        """Returns numeric annotations for the remedy"""

        return [f'{i} : {arr[i]}' for i in range(len(arr))]

    def update_tags(self, all_tags_h2: list[str]):
        one_idx, two_idx = 0, 0
        for idx in all_tags_h2:
            if idx.text == self.table_headers_text[0]:
                one_idx = all_tags_h2.index(idx)
            if idx.text == self.table_headers_text[-1]:
                two_idx = all_tags_h2.index(idx)
        update_tags_h2: list = all_tags_h2[one_idx: two_idx+1]
        for bag in update_tags_h2:
            if bag.text == 'Дата последнего изменения':
                update_tags_h2.remove(bag)
        return update_tags_h2

    def get_annotation(self, setting_num: int) -> str:
        """Returns from annotations on a specified number"""

        all_tags_h2 = self.soup.find_all("h2")
        update_tags_h2 = self.update_tags(all_tags_h2)

        lines_html = []
        with open("medikoment776630117.html", "r", encoding="utf-8") as file:
            for line in file:
                if line == '':
                    continue

                lines_html.append(' '.join(line.split()))
        dictionary_response = {}
        for h2_idx in range(len(update_tags_h2)+1):
            if update_tags_h2[h2_idx] == update_tags_h2[-1]:
                break

            index = lines_html.index(str(update_tags_h2[h2_idx]))
            lines_index = lines_html.index(str(update_tags_h2[h2_idx + 1]))
            dictionary_response[update_tags_h2[h2_idx].text] = lines_html[index:lines_index]
        return BeautifulSoup(" ".join(
            dictionary_response[self.table_headers_text[setting_num]]), features="lxml").text


class Condition(StatesGroup):
    waiting_to_find_drugs = State()
    waiting_to_find_digit = State()
