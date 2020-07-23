import csv

import requests
from bs4 import BeautifulSoup as bs
import lxml
from collections import namedtuple
import re

URL = 'https://www.mvideo.ru'

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 '
                  'Safari/537.36 OPR/69.0.3686.77'}

category = []
sites_cat = []
sites_item = []
Result = namedtuple('Result',
                           ('Category', 'Name', 'Id', 'Cost', 'Price', 'Status')
                           )

HEADERS = (
    'Категория',
    'Наименование',
    'Код товара',
    'Цена',
    'Цена со скидкой',
    'Статус'
)


def main():
    parser = Parser()
    # product_site = []
    url = 'https://www.mvideo.ru/product-list-page?limit=4&offset=0&region_id=1&q=maunfeld&type=grouped'
    param = 'li.search-results-cluster-heading-menu-subcategory__item'
    parser.get_request(url=url, sites=sites_cat, param=param)
    count = 0
    param = 'div.c-product-tile__description-wrapper'
    for block in sites_cat:
        parser.get_request(url=block, param=param, sites=sites_item, flag=2)
    for item in sites_item:
        item = item.replace('/reviews', '')
        parser.parse_block(item, count)
        count += 1
    # for site in sites_item:
    #     # if count == 70:
    #     #     break

    parser.save_result()


class Parser(object):
    def __init__(self):
        self.result = []

    def get_url(self, item):
        url_block = item.select_one('a')
        href = url_block.get('href')
        if href:
            url = URL + href
        else:
            url = None
        return url

    def parse_block(self, site, count):
        print(site)
        soup = self.get_request(url=site, param=None, sites=None, flag=1, fl=0)

        # Category
        block_cat = category[count].strip()

        # Name
        block_name = soup.select_one('div.o-pdp-topic__title').text.strip()
        print(block_name)

        # Id
        block_id = soup.select_one('div.o-pdp-topic__code').text.strip()

        # Price
        try:
            block_price = soup.select_one('div.u-mr-8.c-pdp-price__old').text.strip()
            block_min = soup.select_one('div.c-pdp-price__current.sel-product-tile-price').text.strip()
        except Exception:
            block_price = soup.select_one('div.c-pdp-price__current.sel-product-tile-price').text.strip()
            block_min = ''

        # Status
        try:
            block_stat = soup.select_one('div.c-notifications.u-mt-16').text.strip()
        except Exception:
            block_stat = 'В наличии'

        self.result.append(Result(
            Category=block_cat,
            Name=block_name,
            Id=block_id,
            Cost=block_price,
            Price=block_min,
            Status=block_stat
        ))

    def get_request(self, url, param, sites, flag=0, fl=1):
        r = requests.get(url=url, headers=headers)
        soup = bs(r.text, 'lxml')
        if flag == 1:
            return soup
        block = soup.select(param)
        for item in block:
            if flag == 2:
                categ = soup.select('h2.search-results-cluster-subtitle.search-results-cluster-subtitle_step2')
                for cat in categ:
                    cat = re.sub('\d+', '', cat.text)
                    category.append(cat)
            next_block = self.get_url(item=item)
            if fl:
                sites.append(next_block)
        if flag == 2:
            try:
                page = soup.select_one('a.font-icon.icon-right-open.ico-pagination-next').get('href')
                # print(page)
                # return
                page = URL + page
                self.get_request(url=page, param=param, sites=sites_item, flag=2)
            except Exception:
                pass
        return

    def save_result(self):
        with open('results.csv', 'w') as fl:
            writer = csv.writer(fl, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)


if __name__ == '__main__':
    main()
