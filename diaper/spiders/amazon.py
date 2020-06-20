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
        product_links = response.xpath('//span[@cel_widget_id="MAIN-SEARCH_RESULTS"]').css('a.a-link-normal::attr(href)').getall()
        for product_link in product_links:
            yield SeleniumRequest(
                url=response.urljoin(product_link),
                callback=self.parse_product,
            )

        next_links = response.xpath('//a[text()="Next"]/@href').getall()
        for next_link in next_links:
            yield SeleniumRequest(
                url=response.urljoin(next_link),
                callback=self.parse,
            )

    def parse_product(self, response):
        name = response.css('span#productTitle::text').get()
        if name:
            name = name.strip()
        else:
            return

        yield DiaperItem(
            name=name,
            brand=response.css('a#bylineInfo::text').get(),
            units=response.xpath('//td[text()="Units"]/following-sibling::td/text()').get(),
            price=response.css('span#price_inside_buybox::text').get().strip().split('$')[1],
            country=None,
            availability=response.css('div#availability span::text').get().strip(),
            url=response.request.url,
            date_crawled=datetime.datetime.today(),
        )
