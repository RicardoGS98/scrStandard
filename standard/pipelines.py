# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import base64

from scrapy import Request
# useful for handling different item types with a single interface
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FileException
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum

from standard.spiders.standard import StandardSpider


class DuplicatesPipeline:
    duplicates = set()

    def process_item(self, item, spider: StandardSpider):
        _id = item[spider.duplicate_attr]
        if _id in self.duplicates:
            raise DropItem("Duplicate")
        self.duplicates.add(_id)
        return item


class CustomImagePipeline(ImagesPipeline):

    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func, settings)
        self.images_attrs = None

    def open_spider(self, spider: StandardSpider):
        super().open_spider(spider)
        self.images_attrs = spider.images_attrs

    def get_media_requests(self, item: dict, info):
        _requests = []
        for attr in self.images_attrs:
            values = item.pop(attr, None)
            if not values:
                continue
            if isinstance(values, list):
                _requests.extend([Request(url=v, meta={'item': item}) for v in values])
            else:
                _requests.append(Request(url=values, meta={'item': item}))
        return _requests

    def file_path(self, request, response=None, info=None, *, item=None):
        # No guardar la imagen en el sistema de archivos
        return None

    def media_downloaded(self, response, request, info, *, item=None):
        try:
            return super().media_downloaded(response, request, info, item=item)
        except FileException:
            return {'url': request.url, 'path': None, 'checksum': None, 'status': None}

    def image_downloaded(self, response, request, info, *, item: dict = None):
        checksum = None
        try:
            for _, _, buf in self.get_images(response, request, info, item=item):
                if checksum is None:
                    buf.seek(0)
                    checksum = md5sum(buf)
                item.setdefault('images', []).append(base64.b64encode(buf.getvalue()).decode('utf-8'))
        except Exception:
            checksum = None
        return checksum

    def item_completed(self, results, item, info):
        return item
