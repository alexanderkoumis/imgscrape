# DistributedCV - Image Scraper

An example [Scrapy](http://scrapy.org/) [ImagePipeline](http://doc.scrapy.org/en/latest/topics/media-pipeline.html#using-the-images-pipeline) implementation. Recursively visits all valid links on a page, downloading all images to `imgscrape/output`.

## Install dependencies
```bash
pip install scrapy validators
```

## Usage
```
cd scraper
scrapy crawl img
```
