# WildBerries Parser

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview
The WildBerries Parser is a Python script that allows you to collect information on items from the [Wildberries](https://wildberries.ru) website and save it into an xlsx file. The parser provides two modes: scanning items in a specific directory of the marketplace or parsing all items in the search results based on a given keyword. It collects various data from each item, including the link, ID, name, brand name, regular price, discounted price, rating, number of reviews, and total sales.

## Features
- Retrieve item data from Wildberries based on categories or search keywords
- Extract information such as link, ID, name, brand, pricing, rating, reviews, and sales
- Save the collected data in xlsx format for further analysis

## Installation
1. Clone this repository to your local machine.
2. Navigate to the project directory.

## Prerequisites
- Python 3.x
- Requests library (`pip install requests`)
- Pandas library (`pip install pandas`)

## Usage
1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Run the script using the following command:
`python wbparser.py`
4. Follow the on-screen instructions to choose the desired parsing mode and provide the necessary input.

## Examples
To parse a specific category:
- Choose the parsing mode for a category.
- Enter the category name or URL.
- The script will retrieve all products in the category, collect sales data, and save the parsed data to an xlsx file.

To parse by keywords:
- Choose the parsing mode for keywords.
- Enter the search query.
- The script will retrieve all products in the search results, collect sales data, and save the parsed data to an xlsx file.

## Contributing
Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements
Special thanks to [Timerlan Nalimov](https://github.com/Timur1991) for inspiring this project with his [initial parser](https://github.com/Timur1991/project_wildberries). I appreciate his work and its contribution to the development of this parser.
