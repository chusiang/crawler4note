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


def parse_book_data(soup):

    """
    提取所有書籍資訊並回傳一個字典，並使用正則表達式進行清理。
    """

    # 1. 標題
    # 提取 <title> 標籤的文字，並移除 "天瓏網路書店-"
    title_elem = soup.title
    title = title_elem.get_text(strip=True) if title_elem else 'Not Found'
    # 使用 regex 移除 "天瓏網路書店-"
    title = re.sub(r'天瓏網路書店-', '', title).strip()

    # 2. 書籍資訊區塊 (item-info)
    # 提取 class="item-info" 的 div 內容
    info_elem = soup.find('div', class_='item-info')
    info = str(info_elem) if info_elem else 'Not Found'

    # 使用 regex 移除預覽內頁按鈕的整個 <a> 標籤，包括其內容
    # 模式解釋:
    # <a\s+class="item-preview\s+btn\s+btn-plain"[^>]*?>: 匹配開頭的 <a 標籤及所有其屬性
    # .*?: 非貪婪匹配任何內容 (包括 <i> 標籤和文字)
    # 預覽內頁</a>: 匹配 "預覽內頁" 文字和結束的 </a> 標籤
    info = re.sub(
        r'<a\s+class="item-preview\s+btn\s+btn-plain"[^>]*?>.*?預覽內頁</a>',
        '', info, flags=re.DOTALL)

    # 使用 regex 移除 <i class="fa fa-eye fa-before"></i> 標籤
    # 模式解釋:
    # <i\s+class="fa\s+fa-eye\s+fa-before"[^>]*?>: 匹配開頭的 <i 標籤及所有其屬性
    # .*?: 非貪婪匹配任何內容 (如果 <i> 標籤內有內容的話)
    # </i>: 匹配結束的 </i> 標籤
    info = re.sub(
        r'<i\s+class="fa\s+fa-eye\s+fa-before"[^>]*?>.*?</i>',
        '', info, flags=re.DOTALL)

    # 3. 商品描述、作者簡介、目錄大綱
    # 這些內容都在 class="item-desc" 的 div 中，按順序排列
    item_desc_elements = soup.find_all('div', class_='item-desc')

    # 商品描述 (第一個 item-desc)
    if len(item_desc_elements) > 0:
        desc = str(item_desc_elements[0])
    else:
        desc = 'Not Found'

    # 作者簡介 (第二個 item-desc)
    if len(item_desc_elements) > 1:
        author = str(item_desc_elements[1])
    else:
        author = 'Not Found.'

    # 目錄大綱 (第三個 item-desc)
    if len(item_desc_elements) > 2:
        outline = str(item_desc_elements[2])
    else:
        outline = 'Not Found.'

    return {
        "title": title,
        "info": info,
        "desc": desc,
        "author": author,
        "outline": outline
    }


def main():
    try:
        # Get data.
        soup, book_url = get_data()

        # Parser.
        book_data = parse_book_data(soup)

        # Rendering with Jinja2 template.
        template = Template(HTML_TEMPLATE)
        result = template.render(**book_data, url=book_url)

        # Save to HTML file, and fix layout by pangu.
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(pangu.spacing_text(result))

        print("Generated index.html !")

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
