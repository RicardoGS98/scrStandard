import json
import os

import scrapy
from scrapy.http import HtmlResponse
from scrapy.settings import BaseSettings

from standard.spiders.standard import StandardSpider

BASE_URL = 'https://apps.feriavalencia.com/api/'


class FeriaValenciaSpider(StandardSpider):
    name = "feria-valencia"
    allowed_domains = ["apps.feriavalencia.com"]
    duplicate_attr = "exhibitor"
    images_attrs = ['logourl']
    attrs = [
        'exhibitor', 'name', 'province.prtrname', 'country.cotrname', 'stand', 'pavilion',
        'sectors.setrname', 'activities.actrname', 'users.usr', 'exhicp', 'exhiphone1', 'exhiphone2',
        'logourl', 'exhicontactperson', 'exhiemail', 'exhiweb'
    ]

    @classmethod
    def update_settings(cls, settings: BaseSettings):
        super().update_settings(settings)
        settings.set("HTTPCACHE_ENABLED", True, priority="spider")
        settings.set("HTTPCACHE_IGNORE_HTTP_CODES", [500], priority="spider")
        settings.set('DEFAULT_REQUEST_HEADERS', {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.environ["FERIA_VALENCIA_TOKEN"]}'
        }, priority="spider")

    def start_requests(self):
        yield scrapy.Request(
            method='POST',
            url=BASE_URL + 'puisearch',
            body=json.dumps({
                "filter": {
                    "groupOp": "and",
                    # Data [id] es el evento que se va a llevar a cabo y del cual se quiere extraer la info
                    "rules": [{"data": 138, "field": "event", "op": "eq"}]
                },
                "model": "catalogexhibitor",
                "rows": None
            }),
            callback=self.parse
        )

    def parse(self, response: HtmlResponse, **kwargs):
        for exhibitor in response.json()['data']:
            yield scrapy.Request(
                method='GET',
                url=BASE_URL + f'exhibitor/get?exhiid={exhibitor["exhibitor"]}',
                callback=self.parse_item,
                cb_kwargs={'data': exhibitor}
            )

    def parse_item(self, response: HtmlResponse, data: dict):
        yield dict(self.get_item(self.attrs, data | response.json()))
