#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from jinja2 import Template
import logging
import requests
import sys
import urllib3
import pangu
import re

# disable ssl warn message.
urllib3.disable_warnings()
logging.captureWarnings(True)


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width" />
  <title> {{ title }} </title>
</head>
<body>
  <p>
    History:
    <ul>
      <li> TBD. </li>
    </ul>
  </p>
  <p>
    Series:
    <ul>
      <li> TBD. </li>
    </ul>
  </p>
  <p>
    Buy:
    <ul>
      <li> <a href="{{ url }}" target="_blank">天瓏書局</a> </li>
    </ul>
  </p>
  <hr>
  {{ info }}

  <h2>商品描述</h2>
  {{ desc }}

  <h2>作者簡介</h2>
  {{ author }}

  <h2>目錄大綱</h2>
  {{ outline }}

  <h2>Memo</h2>

  <h3>我想讀這本書的原因是什麼?</h3>
  <ol>
    <li> TBD. </li>
  </ol>

  <h3>看完書封介紹和目錄大綱後，我覺得我可以從那邊得到什麼?</h3>
  <ol>
    <li> TBD. </li>
  </ol>

  <h3>在買這本新書前，我曾讀過相關的主題的書籍嗎? 當時得到了什麼新知?</h3>
  <ol>
    <li> TBD. </li>
  </ol>

  <footer style="text-align: center;">
    Parser by
      <a href="https://github.com/chusiang/crawler4note" target="_blank">
        chusiang/crawler4note
      </a>
    <hr>
  </footer>
</body>
</html>
"""


def get_data():

    """
    Data Retrieval
    --------------

    1. Get URL or Books ID from cli.
    2. Send requests and return BeautifulSoup.
    """

    try:
        arg = sys.argv[1]

        if arg.isdigit():
            # send get request and get reposoe.
            book_url = f'https://www.tenlong.com.tw/products/{arg}'
        else:
            book_url = arg

        res = requests.get(book_url, verify=False)
        res.raise_for_status()  # 檢查 HTTP 請求是否成功
        soup = BeautifulSoup(res.text, 'html.parser')

        return soup, book_url

    except requests.exceptions.RequestException as e:
        print(f"無法連線到網頁或請求失敗: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"發生錯誤: {e}")
        sys.exit(1)


def parser_book_title(data):
    title = data.title
    title = str(title).replace('<title>天瓏網路書店-', '')
    title = title.replace('</title>', '')
    return title


def parser_book_info(data):
    parser_item_info = data.find_all('div', class_='item-info')
    info = str(parser_item_info[0])
    info = info.replace('<i class="fa fa-eye fa-before"></i>', '')
    info = info.replace('<a class="item-preview btn btn-plain" href="#">', '')
    info = info.replace('預覽內頁</a>', '')
    return info


def parser_book_desc(data):
    parser_item_desc = data.find_all('div', class_='item-desc')
    book_desc = str(parser_item_desc[0])
    return book_desc


def parser_book_author(data):
    parser_item_desc = data.find_all('div', class_='item-desc')
    try:
        author = parser_item_desc[1]
    except IndexError:
        print("'item-desc[1]' is not found.")
        author = "Not found."
    finally:
        return author


def parser_book_outline(data):
    parser_item_desc = data.find_all('div', class_='item-desc')
    try:
        outline = parser_item_desc[2]
    except IndexError:
        print("'item-desc[2]' is not found.")
        outline = "Not found."
    finally:
        return outline


def main():
    try:
        # Get data.
        data = get_data()

        # Parser.
        book_title = parser_book_title(data[0])
        book_url = data[1]
        book_info = parser_book_info(data[0])
        book_desc = parser_book_desc(data[0])
        book_author = parser_book_author(data[0])
        book_outline = parser_book_outline(data[0])

        # Rendering with Jinja2 template.
        template = Template(HTML_TEMPLATE)
        result = template.render(
            title=book_title,
            url=book_url,
            info=book_info,
            desc=book_desc,
            author=book_author,
            outline=book_outline
        )

        # Write to HTML file.
        f = open('index.html', 'w')
        f.write(pangu.spacing_text(result))
        f.close()

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
