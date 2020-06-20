import datetime
import re
import scrapy
from scrapy_selenium import SeleniumRequest

from diaper.items import DiaperItem

class FairpriceSpider(scrapy.Spider):
    name = 'fairprice'
    start_urls = [
        'https://www.fairprice.com.sg/search?query=diapers&filter=brand%3Amamypoko%26Country%20Of%20Origin%3AJapan',
        'https://www.fairprice.com.sg/search?query=diapers&filter=brand%3Amamypoko%26Country%20Of%20Origin%3AIndonesia',
        'https://www.fairprice.com.sg/search?query=diapers&filter=brand%3Amamypoko%26Country%20Of%20Origin%3AThailand',
        'https://www.fairprice.com.sg/search?query=diapers&filter=brand%3Amerries',
        'https://www.fairprice.com.sg/search?query=diapers&filter=brand%3Apampers',
    ]

    def parse(self, response):
        product_links = response.css('div.product-container a::attr(href)').getall()
        for url in product_links:
            full_url = response.urljoin(url)
            # Use headless chrome to get 'Out of stock' info
            yield SeleniumRequest(
                url=full_url,
                callback=self.parse_product,
            )

    def parse_product(self, response):
        name = response.xpath('//span[@weight="regular"]/text()').get()
        if name:
            name = name.strip()
        else:
            return

        if response.xpath('//span[text()="Out of stock"]').get():
            availability = 'Out of stock'
        else:
            availability = 'In stock'

        yield DiaperItem(
            name=name,
            brand=response.xpath('//span[@data-testid="brandDetails"]/a/text()').get(),
            units=response.xpath('//span[@data-testid="brandDetails"]/parent::div/span/span/text()').get(),
            price=response.xpath('//span[@weight="black"]/text()').get().split('$')[1],
            country=response.xpath('//h2[@title="Country of Origin"]/parent::div/div/span/text()').get(),
            availability=availability,
            url=response.request.url,
            date_crawled=datetime.datetime.today(),
        )
