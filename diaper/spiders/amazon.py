import datetime
import scrapy
import pandas as pd
from scrapy_selenium import SeleniumRequest

from diaper.items import DiaperItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def start_requests(self):
        urls = pd.read_csv('amazon_urls.csv').url.to_list()
        for url in urls:
            # Use headless chrome because crawling from AWS was blocked
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
            )

    def parse(self, response):
        next_links = response.xpath('//a[text()="Next"]/@href').getall()
        for next_link in next_links:
            yield SeleniumRequest(
                url=response.urljoin(next_link),
                callback=self.parse,
            )

        cell_xpath = '//span[@cel_widget_id="MAIN-SEARCH_RESULTS"]'
        url_xpath = f'{cell_xpath}/div/div/div[2]/h2/a/@href'
        url_list = response.xpath(url_xpath).getall()
        name_xpath = f'{cell_xpath}/div/div/div[2]/h2/a/span/text()'
        name_list = response.xpath(name_xpath).getall()
        price_xpath = '//span[@class="a-price"]/span[1]/text()'
        price_list = response.xpath(price_xpath).getall()
        cell_inner_html_list = response.xpath(cell_xpath).getall()

        NO_STOCK = 'Temporarily out of stock'
        df = pd.DataFrame(
            name_list,
            columns=['name']
        ).assign(
            url=[response.urljoin(x) for x in url_list],
            price=[x.strip('S$') for x in price_list],
            availability=[(NO_STOCK if NO_STOCK in x else 'OK') for x in cell_inner_html_list],
        )
        for r in df.itertuples():
            yield DiaperItem(
                name=r.name,
                units=None,
                price=r.price,
                availability=r.availability,
                url=r.url,
                date_crawled=datetime.datetime.today(),
            )
