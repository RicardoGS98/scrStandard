# debug.py

import sys

from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.project import get_project_settings

if len(sys.argv) < 2:
    print("Uso: python debug.py [nombre_de_spider]")
    sys.exit(1)

spider_name = sys.argv[1]

# Obtener las configuraciones del proyecto
settings = get_project_settings()

# Crear un proceso de crawler con esas configuraciones
process = CrawlerProcess(settings)

# Cargar la lista de spiders disponibles
spider_loader = SpiderLoader.from_settings(settings)
if spider_name not in spider_loader.list():
    print(f"Error: '{spider_name}' no es un nombre de spider válido.")
    print("Spiders disponibles:", ", ".join(spider_loader.list()))
    sys.exit(1)

# Añadir la spider al proceso
process.crawl(spider_name)

# Iniciar el proceso de crawling
process.start()
