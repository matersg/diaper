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
        names = response.xpath(
            '//span[@cel_widget_id="MAIN-SEARCH_RESULTS"]//h2//span/text()').getall()
        prices_whole = response.xpath(
            '//span[@cel_widget_id="MAIN-SEARCH_RESULTS"]').css("span.a-price-whole::text").getall()
        prices_fraction = response.xpath(
            '//span[@cel_widget_id="MAIN-SEARCH_RESULTS"]').css("span.a-price-fraction::text").getall()
        urls = [response.urljoin(x) for x in response.xpath('//span[@cel_widget_id="MAIN-SEARCH_RESULTS"]//h2/a/@href').getall()]
        date_crawled = datetime.datetime.today()
        for name, price_whole, price_fraction, url in zip(names, prices_whole, prices_fraction, urls):
            yield DiaperItem(
                name=name,
                brand=None,
                units=None,
                price=f'{price_whole}.{price_fraction}',
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
