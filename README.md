# Crawler Book Info

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg) [![Docker Hub](https://img.shields.io/badge/docker-chusiang%2Fcrawler--book--info-blue.svg)](https://hub.docker.com/r/chusiang/crawler-book-info/) [![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

A sample crawler for quick parse some information (ex. book) for put to my Evernote.

## Initialization

1. Install the [pyenv][pyenv] and [pyenv-virtualenv][py-venv].
1. create virtualenv of `py3`.

   ```console
   [ chusiang@xenial ~/vcs/crawler4note ]
   $ pyenv virtualenv 3.9.6 py3
   ```

1. Use `py3` virtualenv under this directory.

   ```console
   [ chusiang@xenial ~/vcs/crawler4note ]
   $ pyenv local py3
   ```

1. Install packages with pip.

   ```console
   (py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ pip3 install -r requirements.txt
   ```

[pyenv]: https://github.com/pyenv/pyenv-virtualenv
[py-venv]: https://github.com/pyenv/pyenv-virtualenv

## Usage

### tenlong.com.tw

1. Run crawler with **ISBN-13**.

   ```console
   (.py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ python3 tenlong.py 9781491915325
   ```

### books.com.tw

1. Run crawler with **url**.

   ```console
   (py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ python3 books.py https://www.books.com.tw/products/0010810939
   ```

1. Run crawler with **product number**.

   ```console
   (py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ python3 books.py 0010810939
   ```

> Not support the **ISBN-13** args yet on books.com.tw.

### View Result

1. Open html via Firefox on GNU/Linux.

   ```console
   (py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ firefox index.html
   ```

   ![ansiblebook](https://cloud.githubusercontent.com/assets/219066/24584670/8ffb25f2-17a7-11e7-913a-2f570f773a66.png)

1. We can see the <https://www.tenlong.com.tw/products/9781491915325>
   , it is clean, now.

### Run local Nginx for Evernote Web Clipper

The **Evernote Web Clipper** is not support local files, so we can clip it with Nginx.

1. Run Nginx container.

   ```console
   (py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ docker run --name nginx -v "$(pwd)":/usr/share/nginx/html/ -p 80:80 -d nginx
   ```

1. Open html via Firefox on GNU/Linux.

   ```console
   (py3) [ chusiang@xenial ~/vcs/crawler4note ]
   $ firefox http://localhost
   ```

1. Finally, we can clip the information to Evernote with [Evernote Web Clipper](https://evernote.com/intl/zh-tw/webclipper/).

## License

Copyright (c) chusiang from 2017-2025 under the MIT license.
