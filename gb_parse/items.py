# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class HHItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    url_company = scrapy.Field()
    name = scrapy.Field()
    url_site = scrapy.Field()
    activity = scrapy.Field()
    description_company = scrapy.Field()
    vacancies_company = scrapy.Field()
