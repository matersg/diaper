import datetime
from bs4 import BeautifulSoup
import scrapy
import pandas as pd

from diaper.items import DiaperItem

class FairpriceSpider(scrapy.Spider):
    name = 'fairprice'
    start_urls = pd.read_csv('fairprice_urls.csv').url.to_list()

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for c in soup.find_all('div', {'class': 'product-container'}):
            price = c.select_one('span span').get_text()
            name = c.find('span', {'weight': 'normal'}).get_text()
            units = c.select_one('span:contains("per pack")').get_text()
            url = c.find('a').get('href')
            yield DiaperItem(
                name=name,
                brand=None,
                units=units,
                price=price.strip('$'),
                country=None,
                availability=None, #FIXME!
                url=response.urljoin(url),
                date_crawled=datetime.datetime.today(),
            )
