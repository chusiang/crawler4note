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

# disable ssl warn message and warning logging
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
      <li> <a href="{{ url }}" target="_blank">博客來</a> </li>
    </ul>
  </p>
  <hr>
  {{ full_title }}
  <p>
    <img src="{{ cover }}"/>
  </p>

  {{ info1 }}
  {{ price }}
  {{ info2 }}

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
        if len(sys.argv) < 2:
            print("請輸入博客來書籍 ID 或完整的 URL 作為命令列參數。")
            sys.exit(1)
        arg = sys.argv[1]
        if arg.isdigit():
            book_url = f'https://www.books.com.tw/products/{arg}'
        else:
            book_url = arg

        # Send GET request and get response.
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


def regex_cleaned(html_str):

    """
    Data Parsing
    ------------

    1. Clean HTML element and attribute, like "追蹤按鈕".
    """

    # 移除 `<h4>` 及其相關的追蹤和修改按鈕
    cleaned = re.sub(r'<h4[^>]*>已追蹤作者：.*?</h4>', '', html_str, flags=re.DOTALL)

    # 移除 `<a name="*">`
    cleaned = re.sub(
        r'<a[^>]*?\s+name="[^"]*"[^>]*?>./*?</a>',
        '', cleaned, flags=re.DOTALL)

    # 移除 `<ul class="sort">``
    cleaned = re.sub(r'<ul\s+class="sort">', '', cleaned, flags=re.DOTALL)

    # 移除 `<div class="bd">``
    cleaned = re.sub(r'<div\s+class="bd">', '', cleaned, flags=re.DOTALL)

    # 移除 id="list_trace" 和 id="list_traced" 的 ul 標籤
    cleaned = re.sub(
        r'<ul\s+(?:id="list_trace"|id="list_traced")[^>]*>.*?</ul>',
        '', cleaned, flags=re.DOTALL)

    # 移除 `type02_btn02` 的按鈕
    cleaned = re.sub(
        r'<a[^>]*class="type02_btn02"[^>]*>.*?</a>',
        '', cleaned, flags=re.DOTALL)

    # 移除 <span class="arrow"></span>
    cleaned = cleaned.replace('<span class="arrow"></span>', '')

    # 移除幫助連結 <cite class="help">...</cite>
    cleaned = re.sub(
        r'<a[^>]*title="新功能介紹"[^>]*>.*?</a>',
        '', cleaned, flags=re.DOTALL)

    return cleaned.strip()


def parse_book_data(soup):

    # 標題
    title = soup.title.get_text(strip=True).replace('博客來-', '')

    # 書籍完整標題
    full_title_elem = soup.select_one('h1')
    full_title = str(full_title_elem) if full_title_elem else 'Not Found'

    # 封面圖片 URL
    #
    # 尋找 class_='cover' 的 img 標籤，並取得 'src' 屬性
    cover_img = soup.find('img', class_='cover')
    #
    # 確保 img 標籤存在並取得 src 屬性，同時移除 'amp;'
    if cover_img:
        cover = cover_img.get('src', '').replace('amp;', '')
    else:
        cover = 'Not Found'

    # 書籍資訊區塊 1 (包含作者資訊、追蹤按鈕等)
    info1_elem = soup.find('div', class_='type02_p003 clearfix')
    info1 = str(info1_elem) if info1_elem else ''
    info1 = info1.removesuffix('</ul></div>')
    info1 = regex_cleaned(info1)

    # 書籍價格
    price_elem = soup.find('ul', class_='price')
    price = price_elem.decode_contents() if price_elem else 'Not Found'

    # 書籍資訊區塊 2 (通常是詳細資料)
    info2_elem = soup.find('div', class_='mod_b type02_m058 clearfix')
    if info2_elem:
        info2 = info2_elem.decode_contents().replace(
            '<h3>詳細資料</h3>', '').strip()
        info2 = regex_cleaned(info2)
        info2 = info2.replace("<ul>", '').replace("</ul>", '')
    else:
        info2 = 'Not Found'

    # 商品描述 (第一個 class_='bd' 的 div)
    desc_elem = soup.find_all('div', class_='bd')
    desc = str(desc_elem[0]) if desc_elem else 'Not Found'

    # 作者簡介 (第二個 class_='bd' 的 div)
    author = "Not Found."
    if len(desc_elem) > 1:
        # 獲取第二個 bd 區塊並移除 '作者簡介<br/>'
        author = str(desc_elem[1]).replace(
            '作者簡介<br/>', '').replace(
            '<strong>\n<br/>', '<strong>')

    # 目錄大綱 (第三個 class_='bd' 的 div)
    outline = "Not Found."
    if len(desc_elem) > 2:
        outline = str(desc_elem[2])

    return {
        "title": title,
        "full_title": full_title,
        "cover": cover,
        "info1": info1,
        "price": price,
        "info2": info2,
        "desc": desc,
        "author": author,
        "outline": outline
    }


def main():
    try:
        soup, book_url = get_data()

        book_data = parse_book_data(soup)

        # Rendering with Jinja2 template.
        template = Template(HTML_TEMPLATE)
        result = template.render(**book_data, url=book_url)

        # Save to HTML file, and fix layout by pangu.
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(pangu.spacing_text(result))

        print("Generated index.html !")

    except Exception as e:
        print(f"Runtime error: {e}")


if __name__ == "__main__":
    main()
