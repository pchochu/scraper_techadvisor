# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class TechadvisorItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    url_web = scrapy.Field()
    dimensions = scrapy.Field()
    weight = scrapy.Field()
    battery_capacity = scrapy.Field()
    screen_size = scrapy.Field()
    screen_resolution = scrapy.Field()
    contents = scrapy.Field()
    introduced = scrapy.Field()
