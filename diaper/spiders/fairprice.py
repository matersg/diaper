import datetime
import scrapy
import pandas as pd

from diaper.items import DiaperItem

class FairpriceSpider(scrapy.Spider):
    name = 'fairprice'
    start_urls = pd.read_csv('fairprice_urls.csv').url.to_list()

    def parse(self, response):
        container_link_xpath = '//div[contains(@class, "product-container")]/a'
        url_list = response.xpath(f'{container_link_xpath}/@href').getall()

        description_xpath = f'{container_link_xpath}/div/div[2]'
        price_list = response.xpath(f'{description_xpath}/div[1]/div/span[1]/span/text()').getall()
        name_list  = response.xpath(f'{description_xpath}/div[2]/span/text()').getall()
        units_list = response.xpath(f'{description_xpath}/div[2]/div/div/span[1]/text()').getall()

        df = pd.DataFrame(
            name_list,
            columns=['name']
        ).assign(
            url=[response.urljoin(x) for x in url_list],
            price=[x.strip('$') for x in price_list],
            units=units_list,
        )
        for r in df.itertuples():
            yield DiaperItem(
                name=r.name,
                units=r.units,
                price=r.price,
                availability=None, #FIXME!
                url=r.url,
                date_crawled=datetime.datetime.today(),
            )
