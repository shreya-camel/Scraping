import scrapy

class HtmlItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()

class QAItem(scrapy.Item):
    url = scrapy.Field()
    question = scrapy.Field()
    answer = scrapy.Field() 