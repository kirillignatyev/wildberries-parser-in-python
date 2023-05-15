#!/usr/bin/env python3
"""Collect info on items from https://wildberries.ru and save into xslx.

This parser can get data from https://wildberries.ru in a couple of ways:
1. scan items in a certain directory of the marketplace (i. e. books);
2. take in a key word and parse all the items in the search results.

The parser collects the following data from all items in a directory
or search results, which is then saved in xlsx format:
• link,
• id,
• name,
• brand name,
• brand id,
• regular price,
• currently discounted price,
• rating,
• number of reviews,
• total sales.
The parser is under development and new features might be added in the future.

The script was inspired by a parser by Timerlan Nalimov
(https://github.com/Timur1991).

The program is distrubted under MIT license.
"""

__author__ = "Kirill Ignatyev"
__copyright__ = "Copyright (c) 2023, Kirill Ignatyev"
__license__ = "MIT"
__status__ = "Development"
__version__ = "1.2"

import json
from datetime import date
from os import path


import pandas as pd
import requests


class WildBerriesParser:
    """An object containing parsed data and some auxiliary info."""

    def __init__(self):
        """Create an instance of the parser object."""
        self.headers = {'Accept': "*/*",
                        'User-Agent': "Chrome/51.0.2704.103 Safari/537.36"}
        self.run_date = date.today()
        self.product_cards = []
        self.directory = path.dirname(__file__)

    def download_current_catalogue(self) -> str:
        """Download current catalogue and return path to json file.

        Download marketplace's current catalogue structure and save it
        in json format in the script's directory.
        If there is already an up-to-date catalogue, use the existing one.
        """
        local_catalogue_path = path.join(self.directory, 'wb_catalogue.json')
        if (not path.exists(local_catalogue_path)
                or date.fromtimestamp(int(path.getmtime(local_catalogue_path)))
                > self.run_date):
            url = ('https://static-basket-01.wb.ru/vol0/data/'
                   'main-menu-ru-ru-v2.json')
            response = requests.get(url, headers=self.headers).json()
            with open(local_catalogue_path, 'w', encoding='UTF-8') as my_file:
                json.dump(response, my_file, indent=2, ensure_ascii=False)
        return local_catalogue_path

    def traverse_json(self, parent_category: list, flattened_catalogue: list):
        """Flatten recursively the locally saved json catalogue.

        This is an auxiliary function used in
        process_catalogue(local_catalogue_path). The json catalogue from WB
        is slightly inconsistent in keys, so this function handles KeyError.
        """
        for category in parent_category:
            try:
                flattened_catalogue.append({
                    'name': category['name'],
                    'url': category['url'],
                    'shard': category['shard'],
                    'query': category['query']
                })
            except KeyError:
                continue
            if 'childs' in category:
                self.traverse_json(category['childs'], flattened_catalogue)

    def process_catalogue(self, local_catalogue_path: str) -> list:
        """Process the saved json catalogue into a list of dictionaries."""
        catalogue = []
        with open(local_catalogue_path, 'r') as my_file:
            self.traverse_json(json.load(my_file), catalogue)
        return catalogue

    def extract_category_data(self, catalogue: list, user_input: str) -> tuple:
        """Get category name, shard, and query for parsing."""
        for category in catalogue:
            if (user_input.split("https://www.wildberries.ru")[-1]
                    == category['url'] or user_input == category['name']):
                return category['name'], category['shard'], category['query']

    def get_products_on_page(self, page_data: dict) -> list:
        """Parse one page of category or search results and return a list."""
        products_on_page = []
        for item in page_data['data']['products']:
            products_on_page.append({
                'Ссылка': f"https://www.wildberries.ru/catalog/"
                          f"{item['id']}/detail.aspx",
                'Артикул': item['id'],
                'Наименование': item['name'],
                'Бренд': item['brand'],
                'ID бренда': item['brandId'],
                'Цена': int(item['priceU'] / 100),
                'Цена со скидкой': int(item['salePriceU'] / 100),
                'Рейтинг': item['rating'],
                'Отзывы': item['feedbacks']
            })
        return products_on_page

    def add_data_from_page(self, url: str):
        """Add data on products from page to class list."""
        response = requests.get(url, headers=self.headers).json()
        page_data = self.get_products_on_page(response)
        if len(page_data) > 0:
            self.product_cards.extend(page_data)
            print(f"Добавлено товаров: {len(page_data)}")
        else:
            print('Загрузка товаров завершена')
            return True

    def get_all_products_in_category(self, category_data: tuple):
        """Go through all pages in a category.

        Currently, the site limits max number of pages that can be
        parsed to 100.
        """
        for page in range(1, 101):
            print(f"Загружаю товары со страницы {page}")
            url = (f"https://catalog.wb.ru/catalog/{category_data[1]}/"
                   f"catalog?appType=1&curr=rub"
                   f"&dest=-1075831,-77677,-398551,12358499&page={page}"
                   f"&reg=0&sort=popular&spp=0&{category_data[2]}")
            if self.add_data_from_page(url):
                break

    def get_sales_data(self):
        """Parse sales data additionally."""
        for card in self.product_cards:
            url = (f"https://product-order-qnt.wildberries.ru/by-nm/"
                   f"?nm={card['Артикул']}")
            try:
                response = requests.get(url, headers=self.headers).json()
                card['Продано'] = response[0]['qnt']
            except requests.ConnectTimeout:
                card['Продано'] = 'нет данных'
            print(f"Собрано карточек: {self.product_cards.index(card) + 1}"
                  f" из {len(self.product_cards)}")

    def save_to_excel(self, file_name: str) -> str:
        """Save the parsed data in xlsx and return its path."""
        data = pd.DataFrame(self.product_cards)
        result_path = (f"{path.join(self.directory, file_name)}_"
                       f"{self.run_date.strftime('%Y-%m-%d')}.xlsx")
        writer = pd.ExcelWriter(result_path)
        data.to_excel(writer, 'data', index=False)
        writer.close()
        return result_path

    def get_all_products_in_search_result(self, key_word: str):
        """Parse all pages of search result."""
        for page in range(1, 101):
            print(f"Загружаю товары со страницы {page}")
            url = (f"https://search.wb.ru/exactmatch/ru/common/v4/search?"
                   f"appType=1&curr=rub"
                   f"&dest=-1029256,-102269,-2162196,-1257786"
                   f"&page={page}&pricemarginCoeff=1.0"
                   f"&query={'%20'.join(key_word.split())}]&reg=0"
                   f"&resultset=catalog&sort=popular&spp=0")
            if self.add_data_from_page(url):
                break

    def run_parser(self):
        """Run the whole script."""
        instructons = """Введите 1 для парсинга категории целиком,
        2 — по ключевым словам: """
        mode = input(instructons)
        if mode == '1':
            local_catalogue_path = self.download_current_catalogue()
            print(f"Каталог сохранен: {local_catalogue_path}")
            processed_catalogue = self.process_catalogue(local_catalogue_path)
            input_category = input("Введите название категории или ссылку: ")
            category_data = self.extract_category_data(processed_catalogue,
                                                       input_category)
            if category_data is None:
                print("Категория не найдена")
            else:
                print(f"Найдена категория: {category_data[0]}")
            self.get_all_products_in_category(category_data)
            self.get_sales_data()
            print(f"Данные сохранены в {self.save_to_excel(category_data[0])}")
        if mode == '2':
            key_word = input("Введите запрос для поиска: ")
            self.get_all_products_in_search_result(key_word)
            self.get_sales_data()
            print(f"Данные сохранены в {self.save_to_excel(key_word)}")


if __name__ == '__main__':
    app = WildBerriesParser()
    app.run_parser()
