"""
    crawler news cache
    cache presented news
"""
import os
import time
import math
import pickle
import copy
import datetime

from ..config import MAX_NEWS_CACHE, CATEGORY_LIST
from ..config import CATEGORY_FRONT_TO_BACKEND, CATEGORY_LIST


class NewsCache():
    """
        News Cache
    """
    def __init__(self, db_connection) -> None:
        """
            init
        """
        self.db_connection = db_connection
        self.cache = {}  # cache for news home page only
        self.newspool = {}  # pool of cached ori format news, for all news
        self.last_update_time = 0
        self.last_check_time = 0
        self.last_change_time = time.time()
        self.category_last_update_time = {}
        self.max_news_id = 0
        for category in CATEGORY_LIST:
            self.cache[category] = []
            self.category_last_update_time[category] = 0

        self.ori_news_format = {
            "title": str,
            "news_url": str,
            "first_img_url": str,
            "media": str,
            "pub_time": datetime.datetime,
            "id": int,
            "category": str,
            "content": str,
            "tags": list
        }

    def check_ori_news_format(self, news: dict) -> bool:
        """
            check_ori_news_format
        """
        if news:
            for (key, instance) in self.ori_news_format.items():
                if key not in news:
                    return False
                if not isinstance(news[key], instance):
                    return False
            return True
        return False

    def add_to_news_cache_pool(self, news_list: list) -> bool:
        """
            add to news cache pool
        """
        news_list = copy.deepcopy(news_list)
        for news in news_list:
            if self.check_ori_news_format(news):
                if int(news["id"]) in self.newspool:
                    if news["tags"]:
                        self.newspool[int(news["id"])] = news
                else:
                    self.newspool[int(news["id"])] = news
            else:
                print("news format error")
                return False
        try:
            if len(self.newspool) > MAX_NEWS_CACHE:  # del outdate news
                for key in list(self.newspool.keys())[: MAX_NEWS_CACHE // 2]:
                    self.newspool.pop(key)
        except Exception as error:
            print("[Error when cleaning self.newspool]")
            print(error)
            return False

        return True

    def save_local_cache(self):
        """
            save cache from file
        """
        try:
            print("Saving cache to dict", time.time())
            with open("data/news_cache.pkl", "wb") as file:
                pickle.dump(self.cache, file)
            print("Saved", time.time())
        except Exception as error:
            print("[error in save local cache] :", error)

    def load_local_cache(self):
        """
            load cache from file
        """
        print("loading local cache file")
        if os.path.exists("data/news_cache.pkl"):
            with open("data/news_cache.pkl", "rb") as file:
                self.cache = pickle.load(file)
            self.sort_cache_ascend()
            self.update_max_news_id()
            for category in CATEGORY_LIST:
                self.add_to_news_cache_pool(self.cache[category])
            print("local cache loaded")
        else:
            print("load cache not found")

    def sort_cache_ascend(self):
        """
            sort cache in ascend order
        """
        for category in CATEGORY_LIST:
            self.cache[category].sort(key=lambda x:x["id"])

    def sort_cache_descend(self):
        """
            sort cache in descend order
        """
        for category in CATEGORY_LIST:
            self.cache[category].sort(key=lambda x:x["id"], reverse=True)

    def update_max_news_id(self) -> None:
        """
            update max news id in cache
        """
        for category in CATEGORY_LIST:
            try:
                news = self.cache[category][-1]
                if self.max_news_id < news["id"]:
                    self.max_news_id = news["id"]
            except Exception as error:
                print("[error]", error)

    def update_cache(self, db_news_list) -> None:
        """
            update news cache of one specific category
        """
        db_news_list = copy.deepcopy(db_news_list)
        self.last_update_time = time.time()
        db_news_list.sort(key=lambda x:x["id"])

        self.add_to_news_cache_pool(db_news_list)

        for news in db_news_list:
            if news["category"] in CATEGORY_LIST:
                self.cache[news["category"]].append(news)
                self.category_last_update_time[news["category"]] = time.time()
        for category in CATEGORY_LIST:
            self.cache[category] = self.cache[category][-200:]

        self.update_max_news_id()

    def get_cache(self, category):
        """
            get news cache of one specific category
        """
        if category == CATEGORY_FRONT_TO_BACKEND[""]:
            news_list = []
            n_category = len(CATEGORY_LIST)
            n_per_category = math.ceil(200 / n_category)
            for key in CATEGORY_LIST:
                news_list += copy.deepcopy(self.cache[key][-n_per_category:])
        else:
            news_list = copy.deepcopy(self.cache[category])
        news_list.sort(key=lambda x:x["pub_time"], reverse=True)
        return news_list[:200]
