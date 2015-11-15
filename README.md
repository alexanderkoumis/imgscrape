# imgscrape

An example [Scrapy](http://scrapy.org/) [ImagePipeline](http://doc.scrapy.org/en/latest/topics/media-pipeline.html#using-the-images-pipeline) implementation. Recursively visits all valid links on a page, downloading all images to `imgscrape/output`.

Depends on [validators](https://github.com/kvesteri/validators) (`pip install validators`). Run with `scrapy crawl img`.
