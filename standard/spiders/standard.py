import os.path
import re
from abc import ABC, abstractmethod
from typing import Union

import scrapy
from scrapy.settings import BaseSettings


class StandardSpider(scrapy.Spider, ABC):

    @property
    @abstractmethod
    def duplicate_attr(self):
        """
        Atributo unico para filtrar duplicados
        """
        pass

    @duplicate_attr.setter
    @abstractmethod
    def duplicate_attr(self, value):
        pass

    @property
    @abstractmethod
    def images_attrs(self):
        """
        Atributo que contiene 1|+ urls de imagenes a descargar.
        """
        pass

    @images_attrs.setter
    @abstractmethod
    def images_attrs(self, value):
        pass

    @property
    @abstractmethod
    def attrs(self):
        """
        Atributos de interes del objeto a extraer
        """
        pass

    @attrs.setter
    @abstractmethod
    def attrs(self, value):
        pass

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def update_settings(cls, settings: BaseSettings) -> None:
        super().update_settings(settings)
        settings.set('FEEDS', {
            os.path.join('.jsons', cls.name, 'items.json'): {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'indent': 4,
                'overwrite': True
            }
        }, priority="spider")

    def get_item(self, attrs: list, data: Union[dict, list]):
        if isinstance(data, list):
            values = (next(self.get_item(attrs, item))[1] for item in data)
            yield attrs[0], ','.join(map(str, values))
        else:
            for k in attrs:
                if '.' not in k:
                    v = data[k]
                    if isinstance(v, str):
                        v = re.sub(r'\s+', ' ', v.strip())
                    yield k, v or None
                else:
                    new_attrs = k.split('.')
                    try:
                        new_data = data[new_attrs[0]]
                    except TypeError:
                        return
                    if new_data:
                        yield from self.get_item(new_attrs[1:], data[new_attrs[0]])
