"""
    apps.py in django frame work
"""
# import json
from django.apps import AppConfig

# from . import tools


class MainConfig(AppConfig):
    """
        MainConfig of Django App
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    # def ready(self):
    #     """
    #         init
    #     """
    #     with open("config/config.json","r",encoding="utf-8") as config_file:
    #         config = json.load(config_file)
    #     tools.CRAWLER_DB_CONNECTION = tools.connect_to_db(config["crawler-db"])

    #     tools.NEWS_CACHE = tools.NewsCache(tools.CRAWLER_DB_CONNECTION)

    #     tools.DB_SCANNER = tools.DBScanner(
    #         tools.CRAWLER_DB_CONNECTION,
    #         tools.THREAD_LOCK, tools.NEWS_CACHE
    #     )
    #     tools.DB_SCANNER.start()
    #     return super().ready()
