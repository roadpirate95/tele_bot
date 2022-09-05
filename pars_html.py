from bs4 import BeautifulSoup


class Parser:

    def __init__(self):
        self.soup = None
        self.table_headers_text = []

    def set_soup(self, soup: BeautifulSoup) -> None:
        self.soup = soup

    def parser_headers_table(self):
        if len(self.table_headers_text) == 0:
            table_headers = self.soup.find("div", class_="noprint").find_all("li")
            for i in table_headers:
                self.table_headers_text.append(i.text)
                if 'Условия хранения' in i.text:
                    break
        return self.table_headers_text

    def get_tags_h2(self):
        return self.soup.find_all("h2")

    def update_tags_h2(self, all_tags_h2: list[str]):
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

    @staticmethod
    def arr_lines_html(message):
        lines_html = []
        with open(f"medikoment{message.chat.id}.html", "r", encoding="utf-8") as file:
            for line in file:
                # if line == '/n' o:
                #     continue

                lines_html.append(' '.join(line.split()))

        return lines_html

    def resp_annotation(self, update_tags_h2, lines_html, setting_num):
        dictionary_response = {}
        for h2_idx in range(len(update_tags_h2) + 1):
            if update_tags_h2[h2_idx] == update_tags_h2[-1]:
                break

            index = lines_html.index(str(update_tags_h2[h2_idx]))
            lines_index = lines_html.index(str(update_tags_h2[h2_idx + 1]))
            dictionary_response[update_tags_h2[h2_idx].text] = lines_html[index:lines_index]
        return BeautifulSoup(" ".join(
            dictionary_response[self.table_headers_text[setting_num]]), features="lxml").text
