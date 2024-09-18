# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.exceptions import DropItem

from standard.spiders.standard import StandardSpider


class DuplicatesPipeline:
    duplicates = set()

    def process_item(self, item, spider: StandardSpider):
        _id = item[spider.duplicate_attr]
        if _id in self.duplicates:
            raise DropItem("Duplicate")
        self.duplicates.add(_id)

# class CustomImagePipeline(ImagesPipeline):
#
#
#     def open_spider(self, spider: StandardSpider):
#         super().open_spider(spider)
#
#     def get_media_requests(self, item: dict, info):
#         image_url = item.get('logo_url') or item.get('photo_url')
#         if image_url:
#             return [Request(url=image_url, meta={'item': item})]
#
#     def file_path(self, request, response=None, info=None, *, item=None):
#         # No guardar la imagen en el sistema de archivos
#         return None
#
#     def media_downloaded(self, response, request, info, *, item=None):
#         try:
#             return super().media_downloaded(response, request, info, item=item)
#         except FileException:
#             return {'url': request.url, 'path': None, 'checksum': None, 'status': None}
#
#     def image_downloaded(self, response, request, info, *, item=None):
#         checksum = None
#         try:
#             for _, _, buf in self.get_images(response, request, info, item=item):
#                 if checksum is None:
#                     buf.seek(0)
#                     checksum = md5sum(buf)
#                 item['image'] = base64.b64encode(buf.getvalue()).decode('utf-8')
#         except Exception:
#             checksum = None
#         return checksum
#
#     def item_completed(self, results, item, info):
#         # Se elimina la foto del item
#         image_url = item.pop('logo_url', None) or item.pop('photo_url', None)
#
#         if not results:
#             self.ignores.add(image_url)
#         else:
#             for ok, x in results:
#                 if not ok:
#                     continue
#                 # Si no ok es xq era un txt o no lo pudo convertir a imagen
#                 self.ignores.add(image_url)
#         return item
