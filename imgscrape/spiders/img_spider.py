import scrapy
import validators

from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.spiders import CrawlSpider, Rule
# from scrapy.selector import Selector
from imgscrape.items import ImgscrapeItem


class ImgSpider(CrawlSpider):

    name = 'img'
    # allowed_domains = ['http://www.huffingtonpost.com']
    start_urls = ['http://www.huffingtonpost.com']

    rules = (Rule(LinkExtractor(allow=()), callback='link_callback'),)

    def link_callback(self, response): 
        item = ImgscrapeItem()
        urls = response.css('img').xpath('@src').extract()
        item['image_urls'] = [url for url in urls if validators.url(url)]
        return item