import scrapy

class DiaperItem(scrapy.Item):
    name = scrapy.Field()
    units = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    url = scrapy.Field()
    date_crawled = scrapy.Field()
