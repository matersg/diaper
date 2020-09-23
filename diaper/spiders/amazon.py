import datetime
import re
import scrapy
from scrapy_selenium import SeleniumRequest

from diaper.items import DiaperItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def start_requests(self):
        urls = [
            'https://www.amazon.sg/s?k=diapers&rh=p_6%3AACT6OAM3OSC9S%2Cp_89%3APampers&dc&qid=1592445069&rnid=6966029051&ref=sr_nr_p_76_1',
            'https://www.amazon.sg/s?k=diapers&rh=p_6%3AACT6OAM3OSC9S%2Cp_89%3AMerries&dc&qid=1592445347&rnid=6733559051&ref=sr_nr_p_89_3',
            'https://www.amazon.sg/s?k=diapers&rh=p_6%3AACT6OAM3OSC9S%2Cp_89%3AMamyPoko&dc&qid=1592445367&rnid=6733559051&ref=sr_nr_p_89_4',
            'https://www.amazon.sg/s?k=moony&i=hpc&rh=p_6%3AACT6OAM3OSC9S&dc&qid=1592447693&rnid=6469115051&ref=sr_nr_p_6_1',
        ]
        for url in urls:
            # Use headless chrome because crawling from AWS was blocked
            yield SeleniumRequest(
                url=url,
                callback=self.parse,
            )

    def parse(self, response):
        url_xpath   = '//span[@data-component-type="s-product-image"]/following-sibling::div[1]//a/@href'
        name_xpath  = '//span[@data-component-type="s-product-image"]/following-sibling::div[1]//span/text()'
        price_xpath = '//span[@data-component-type="s-product-image"]/following-sibling::div[2]/div/div/a/span/span[@class="a-offscreen"]/text()'

        urls = [response.urljoin(x) for x in response.xpath(url_xpath).getall()]
        names = response.xpath(name_xpath).getall()
        prices = response.xpath(price_xpath).getall()

        date_crawled = datetime.datetime.today()
        for name, price, url in zip(names, prices, urls):
            yield DiaperItem(
                name=name,
                brand=None,
                units=None,
                price=price.lstrip('S$'),
                country=None,
                availability=None, #FIXME!
                url=url,
                date_crawled=date_crawled,
            )

        next_links = response.xpath('//a[text()="Next"]/@href').getall()
        for next_link in next_links:
            yield SeleniumRequest(
                url=response.urljoin(next_link),
                callback=self.parse,
            )
