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
    start_urls = [
        'http://www.cnn.com',
        'http://www.huffingtonpost.com',
        'http://www.msnbc.com',
        'http://www.foxnews.com'
    ]

    deny = [
        'facebook',
        'audible',
        'legal'
    ]

    rules = (Rule(LinkExtractor(allow=(), deny=deny), callback='item_callback', process_links='link_callback', follow=True),)

    def link_callback(self, links):
    	return links

    def item_callback(self, response):
        item = ImgscrapeItem()
        urls = response.css('img').xpath('@src').extract()
        item['image_urls'] = [url for url in urls if validators.url(url)]
        return item
