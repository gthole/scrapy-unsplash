import os
from twisted.internet import reactor
from scrapy import Item, Field, Request, Selector, Spider, log, signals
from scrapy.crawler import Crawler
from scrapy.contrib.pipeline.images import ImagesPipeline
from scrapy.utils.project import get_project_settings
from PIL import Image
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

BASE_WIDTH = 1280


class UnsplashItem(Item):
    images = Field()
    image_urls = Field()


class UnsplashSpider(Spider):
    name = "unsplash"
    allowed_domains = ["unsplash.com"]
    base = "https://unsplash.com"
    start_urls = ["%s/" % base]

    def parse(self, response):
        hxs = Selector(response)

        # Gather up all image urls
        item = UnsplashItem(
            image_urls=[
                "%s%s" % (self.base, ref) for ref in
                hxs.xpath('//div[@class="photo"]/a/@href').extract()
            ]
        )
        yield item

        # Generate requests for additional pages, let framework track duping
        for ref in hxs.xpath('//div[@class="pagination"]/a/@href').extract():
            yield Request("%s%s" % (self.base, ref), callback=self.parse)


class UnsplashPipeline(ImagesPipeline):
    def get_images(self, response, request, info):
        path = self.file_path(request)

        # Resize the image to the desired width
        orig_image = Image.open(BytesIO(response.body))
        w, h = orig_image.size
        ratio = BASE_WIDTH / float(w)
        image, buf = self.convert_image(
            orig_image,
            (BASE_WIDTH, int(h * ratio))
        )

        # Return just this image
        yield path, image, buf

    def file_path(self, request, response=None, info=None):
        # Store by the unsplash image PID from the download URL
        return "%s.jpg" % request.url.split("/")[4]

if __name__ == "__main__":
    # http://doc.scrapy.org/en/latest/topics/
    #   practices.html#run-scrapy-from-a-script
    spider = UnsplashSpider()
    settings = get_project_settings()
    # TODO: Better overrideable settings
    settings.setdict({
        "DOWNLOADER_DELAY": 1,
        "ITEM_PIPELINES": {"unsplash.UnsplashPipeline": 1},
        "AWS_ACCESS_KEY_ID": os.environ.get("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        "IMAGES_STORE": os.environ.get("IMAGES_STORE", "images"),
    })
    crawler = Crawler(settings)
    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)
    crawler.start()
    log.start(loglevel=os.environ.get("LOGLEVEL", "INFO"))
    reactor.run()
