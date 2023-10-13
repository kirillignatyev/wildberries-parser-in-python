#!/usr/bin/env python3
"""Collect info on items from wildberries.ru and save it into an xlsx file.

This script is designed to extract data from the wildberries.ru website
using two main modes:
1. Scanning items in a specific directory of the marketplace (e.g., books).
2. Parsing all items in the search results based on a given keyword.

The script collects the following data from each item in the directory
or search results, which is then saved in xlsx format:
- Link
- ID
- Name
- Brand name
- Brand ID
- Regular price
- Discounted price
- Rating
- Number of reviews
- Total sales

The parser is under active development, and new features may be added
in the future.
It was inspired by a parser by Timerlan Nalimov (https://github.com/Timur1991).

The script is distributed under the MIT license.

---

Class: WildBerriesParser

Methods:
- __init__: Initialize the parser object.
- download_current_catalogue: Download the current catalogue in JSON format.
- traverse_json: Recursively traverse the JSON catalogue
    and flatten it to a list.
- process_catalogue: Process the locally saved JSON catalogue
    into a list of dictionaries.
- extract_category_data: Extract category data from the processed catalogue.
- get_products_on_page: Parse one page of category or search results
    and return a list with product data.
- add_data_from_page: Add data on products from a page to the class's list.
- get_all_products_in_category: Retrieve all products in a category
    by going through all pages.
- get_sales_data: Parse additional sales data for the product cards.
- save_to_excel: Save the parsed data in xlsx format and return its path.
- get_all_products_in_search_result: Retrieve all products in the search
    result by going through all pages.
- run_parser: Run the whole script for parsing and data processing.

---

Note: This script utilizes the requests library
and requires an active internet connection to function properly.

"""

__author__ = "Kirill Ignatyev"
__copyright__ = "Copyright (c) 2023, Kirill Ignatyev"
__license__ = "MIT"
__status__ = "Development"
__version__ = "1.3"

import json
from datetime import date
from os import path


import pandas as pd
import requests


class WildBerriesParser:
    """
    A parser object for extracting data from wildberries.ru.

    Attributes:
        headers (dict): HTTP headers for the parser.
        run_date (datetime.date): The date when the parser is run.
        product_cards (list): A list to store the parsed product cards.
        directory (str): The directory path where the script is located.
    """

    def __init__(self):
        """
        Initialize a new instance of the WildBerriesParser class.

        This constructor sets up the parser object with default values
        for its attributes.

        Args:
            None

        Returns:
            None
        """
        self.headers = {'Accept': "*/*",
                        'User-Agent': "Chrome/51.0.2704.103 Safari/537.36"}
        self.run_date = date.today()
        self.product_cards = []
        self.directory = path.dirname(__file__)

    def download_current_catalogue(self) -> str:
        """
        Download the  catalogue from wildberries.ru and save it in JSON format.

        If an up-to-date catalogue already exists in the script's directory,
        it uses that instead.

        Returns:
            str: The path to the downloaded catalogue file.
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
        """
        Recursively traverse the JSON catalogue and flatten it to a list.

        This function runs recursively through the locally saved JSON
        catalogue and appends relevant information to the flattened_catalogue
        list.
        It handles KeyError exceptions that might occur due to inconsistencies
        in the keys of the JSON catalogue.

        Args:
            parent_category (list): A list containing the current category
              to traverse.
            flattened_catalogue (list): A list to store the flattened
              catalogue.

        Returns:
            None
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
        """
        Process the locally saved JSON catalogue into a list of dictionaries.

        This function reads the locally saved JSON catalogue file,
        invokes the traverse_json method to flatten the catalogue,
        and returns the resulting catalogue as a list of dictionaries.

        Args:
            local_catalogue_path (str): The path to the locally saved
              JSON catalogue file.

        Returns:
            list: A list of dictionaries representing the processed catalogue.
        """
        catalogue = []
        with open(local_catalogue_path, 'r') as my_file:
            self.traverse_json(json.load(my_file), catalogue)
        return catalogue

    def extract_category_data(self, catalogue: list, user_input: str) -> tuple:
        """
        Extract category data from the processed catalogue.

        This function searches for a matching category based
        on the user input, which can be either a URL or a category name.
        If a match is found, it returns a tuple containing the category name,
        shard, and query.

        Args:
            catalogue (list): The processed catalogue as a list
              of dictionaries.
            user_input (str): The user input, which can be a URL
              or a category name.

        Returns:
            tuple: A tuple containing the category name, shard, and query.
        """
        for category in catalogue:
            if (user_input.split("https://www.wildberries.ru")[-1]
                    == category['url'] or user_input == category['name']):
                return category['name'], category['shard'], category['query']

    def get_products_on_page(self, page_data: dict) -> list:
        """
        Parse one page of results and return a list with product data.

        This function takes a dictionary containing the data of a page from
        wildberries.ru, specifically the 'data' key with a list of 'products'.
        It iterates over each item in the 'products' list and extracts
        relevant information to create a dictionary representing a product.
        The dictionaries are then appended to the 'products_on_page' list.

        Args:
            page_data (dict): A dictionary containing the data
              of a page from wildberries.ru.

        Returns:
            list: A list of dictionaries representing the products
              on the page, where each dictionary contains information
              such as the link, article number, name, brand, price, discounted
              price, rating, and number of reviews.

        """
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
        """
        Add data on products from a page to the class's list.

        This function makes a GET request to the specified URL using
        the provided headers, expecting a JSON response. The page data is then
        passed to the get_products_on_page method to extract the relevant
        product information. If there are products on the page,
        they are appended to the product_cards list in the class,
        and the number of added products is printed. If there are no products
        on the page, it prints a message and returns True to indicate the end
        of product loading.

        Args:
            url (str): The URL of the page to retrieve the product data from.

        Returns:
            bool or None: Returns True if there are no products on the page,
              indicating the end of product loading. Otherwise, returns None.
        """
        response = requests.get(url, headers=self.headers).json()
        page_data = self.get_products_on_page(response)
        if len(page_data) > 0:
            self.product_cards.extend(page_data)
            print(f"Добавлено товаров: {len(page_data)}")
        else:
            print('Загрузка товаров завершена')
            return True

    def get_all_products_in_category(self, category_data: tuple):
        """
        Retrieve all products in a category by going through all pages.

        This function iterates over page numbers from 1 to 100, constructing
        the URL for each page in the specified category. It then calls the
        add_data_from_page method to retrieve and add the product data from
        each page to the class's product_cards list. If the add_data_from_page
        method returns True, indicating the end of product loading,
        the loop breaks.

        Note:
            The wildberries.ru website currently limits the maximum number of
            pages that can be parsed to 100.

        Args:
            category_data (tuple): A tuple containing the category name,
              shard, and query.

        Returns:
            None
        """
        for page in range(1, 101):
            print(f"Загружаю товары со страницы {page}")
            url = (f"https://catalog.wb.ru/catalog/{category_data[1]}/"
                   f"catalog?appType=1&{category_data[2]}&curr=rub"
                   f"&dest=-1257786&page={page}&sort=popular&spp=24")
            if self.add_data_from_page(url):
                break

    def get_sales_data(self):
        """
        Parse additional sales data for the product cards.

        This function iterates over each product card in the product_cards
        list and makes a request to retrieve the sales data for the
        corresponding product. The sales data is then added to the product
        card dictionary with the key 'Продано'. If an exception occurs during
        the request, indicating a connection timeout, the sales data is set to
        'нет данных'. Progress information is printed during the iteration.

        Returns:
            None
        """
        for card in self.product_cards:
            url = (f"https://product-order-qnt.wildberries.ru/by-nm/"
                   f"?nm={card['Артикул']}")
            try:
                response = requests.get(url, headers=self.headers).json()
                if response == []:
                    card['Продано'] = 'неизвестно'
                else:
                    card['Продано'] = response[0]['qnt']
            except requests.ConnectTimeout:
                card['Продано'] = 'нет данных'
            print(f"Собрано карточек: {self.product_cards.index(card) + 1}"
                  f" из {len(self.product_cards)}")

    def save_to_excel(self, file_name: str) -> str:
        """
        Save the parsed data in xlsx format and return its path.

        This function takes the parsed data stored in the product_cards list
        and converts it into a Pandas DataFrame. It then saves the DataFrame
        as an xlsx file with the specified file name and the current run date
        appended to it. The resulting file path is returned.

        Args:
            file_name (str): The desired file name for the saved xlsx file.

        Returns:
            str: The path of the saved xlsx file.
        """
        data = pd.DataFrame(self.product_cards)
        result_path = (f"{path.join(self.directory, file_name)}_"
                       f"{self.run_date.strftime('%Y-%m-%d')}.xlsx")
        writer = pd.ExcelWriter(result_path)
        data.to_excel(writer, 'data', index=False)
        writer.close()
        return result_path

    def get_all_products_in_search_result(self, key_word: str):
        """
        Retrieve all products in the search result by going through all pages.

        This function iterates over page numbers from 1 to 100, constructing
        the URL for each page in the search result based on the provided
        keyword. It then calls the add_data_from_page method to retrieve and
        add the product data from each page to the class's product_cards list.
        If the add_data_from_page method returns True, indicating the end of
        product loading, the loop breaks.

        Args:
            key_word (str): The keyword to search for in the
              wildberries.ru search.

        Returns:
            None
        """
        for page in range(1, 101):
            print(f"Загружаю товары со страницы {page}")
            url = (f"https://search.wb.ru/exactmatch/ru/common/v4/search?"
                   f"appType=1&curr=rub&dest=-1257786&page={page}"
                   f"&query={'%20'.join(key_word.split())}&resultset=catalog"
                   f"&sort=popular&spp=24&suppressSpellcheck=false")
            if self.add_data_from_page(url):
                break

    def run_parser(self):
        """
        Run the whole script for parsing and data processing.

        This function runs the entire script by prompting the user to choose
        a parsing mode: either parsing a category entirely or parsing by
        keywords. Based on the user's choice, it executes the corresponding
        sequence of steps. For parsing a category, it downloads the current
        catalogue, processes it, extracts the category data, retrieves all
        products in the category, collects sales data, and saves the parsed
        data to an Excel file. For parsing by keywords, it prompts for
        a search query, retrieves all products in the search result, collects
        sales data, and saves the parsed data to an Excel file.

        Returns:
            None
        """
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
