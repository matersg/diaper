import datetime
import scrapy
import pandas as pd

from diaper.items import DiaperItem

class FairpriceSpider(scrapy.Spider):
    name = 'fairprice'
    start_urls = pd.read_csv('fairprice_urls.csv').url.to_list()

    def parse(self, response):
        container_link_xpath = '//div[contains(@class, "product-container")]/a'
        url_list   = response.xpath(f'{container_link_xpath}/@href').getall()
        price_list = response.xpath(f'{container_link_xpath}/div/div[3]/div/div/span/span/text()').getall()
        name_list  = response.xpath(f'{container_link_xpath}/div/div[3]/div[2]/span/text()').getall()
        units = response.xpath(f'{container_link_xpath}/div/div[3]/div[2]/div/div/span/text()').get()

        df = pd.DataFrame(
            name_list,
            columns=['name']
        ).assign(
            url=[response.urljoin(x) for x in url_list],
            price=[x.strip('$') for x in price_list],
            units=units,
        )
        for r in df.itertuples():
            yield DiaperItem(
                name=r.name,
                brand=None,
                units=r.units,
                price=r.price,
                country=None,
                availability=None, #FIXME!
                url=r.url,
                date_crawled=datetime.datetime.today(),
            )
