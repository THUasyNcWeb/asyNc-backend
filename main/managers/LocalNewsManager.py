"""
    crawler news cache
    cache user touched news
"""

import random
from ..models import LocalNews


def news_formator(news) -> dict:
    """
        transform crawler format to frontend format
    """
    format_news = {}
    if "id" in news:
        format_news["id"] = news["id"]
    if "title" in news:
        format_news["title"] = news["title"]
    if "media" in news:
        format_news["media"] = news["media"]
    if "url" in news:
        format_news["url"] = news["url"]
    elif "news_url" in news:
        format_news["url"] = news["news_url"]
    if "pub_time" in news:
        format_news["pub_time"] = str(news["pub_time"])
    if "picture_url" in news:
        format_news["picture_url"] = news["picture_url"]
    elif "first_img_url" in news:
        format_news["picture_url"] = news["first_img_url"]
    if "full_content" in news:
        format_news["full_content"] = news["full_content"]
    elif "content" in news:
        format_news["full_content"] = news["content"]
    if "summary" in news:
        format_news["summary"] = news["summary"]
    if "tags" in news:
        format_news["tags"] = news["tags"]
    return format_news


class LocalNewsManager():
    """
        Favorited or in reading list news will be storaged to local.
        This class manages local news.
    """
    def __init__(self, max_cache=65536) -> None:
        """
            init
        """
        self.local_news_list_cache = {}  # cache summarized news
        self.none_ai_processed_news_dict = {}
        self.min_batch = 256
        self.max_cache = max_cache

    def get_one_ai_news(self, news_id: int, news=None) -> dict:
        """
            get one news with summary
        """
        if news_id in self.local_news_list_cache:
            if "summary" in self.local_news_list_cache[news_id]:
                return self.local_news_list_cache[news_id]
        ai_news = {}
        local_news = LocalNews.objects.filter(news_id=news_id).first()
        if local_news:
            if local_news.ai_processed:
                self.add_to_cache(local_news.data)
            ai_news = {
                "id": int(local_news.data["id"]),
                "title": local_news.data["title"],
                "media": local_news.data["media"],
                "url": local_news.data["url"],
                "pub_time": str(local_news.data["pub_time"]),
                "picture_url": local_news.data["picture_url"],
                "full_content": local_news.data["full_content"],
            }
            if "summary" in local_news.data:
                ai_news["summary"] = local_news.data["summary"]
        elif news:  # add news local_news
            self.save_one_local_news(news)
        return ai_news

    def get_ai_news(self, news_id_list) -> dict:
        """
            get news with summary
        """
        news_dict = {}
        for news_id in news_id_list:
            ai_news = self.get_one_ai_news(news_id)
            if ai_news:
                news_dict[news_id] = ai_news
        return news_dict

    def get_none_ai_processed_news(self, num=1) -> list:
        """
            get none ai processed news
        """
        news_list = []
        if len(self.none_ai_processed_news_dict) < num:
            batch_size = max(num, self.min_batch)
            news_object_list = LocalNews.objects.filter(ai_processed=False)
            news_object_list = list(news_object_list)
            random.shuffle(news_object_list)
            news_object_list = news_object_list[:batch_size]
            if news_object_list:
                for news_object in news_object_list:
                    news = news_object.data
                    news["id"] = int(news["id"])
                    if ("full_content" in news) and news["full_content"]:
                        if news["id"] not in self.none_ai_processed_news_dict:
                            self.none_ai_processed_news_dict[news["id"]] = news
                    else:
                        print(dict(news_object.data).keys())
                        print(news_object.ai_processed)
                        news_object.ai_processed = True
                        news_object.full_clean()
                        news_object.save()

        news_list = list(self.none_ai_processed_news_dict.values())[:num]
        for news in news_list:
            self.none_ai_processed_news_dict.pop(news["id"])
        return news_list

    def update_ai_processed_news(self, news_list) -> bool:
        """
            update ai processed news
        """
        try:
            for news in news_list:
                if "summary" in news and news["summary"]:
                    if news["id"] in self.none_ai_processed_news_dict:
                        self.none_ai_processed_news_dict.pop(news["id"])
                    self.add_to_cache(news)
                    local_news = LocalNews.objects.filter(news_id=int(news["id"])).first()
                    if local_news:
                        local_news.ai_processed = True
                        local_news.data["summary"] = news["summary"]
                        local_news.full_clean()
                        local_news.save()
                    else:
                        local_news = LocalNews(
                            data=news_formator(news),
                            news_id=int(news["id"]),
                            ai_processed=True, cite_count=1
                        )
                        local_news.full_clean()
                        local_news.save()
        except Exception as error:
            print(error)
            return False
        return True

    def add_to_cache(self, news: dict):
        """
            add a news to cache
        """
        if news["id"] in self.local_news_list_cache:
            if "summary" in news and news["summary"]:
                self.local_news_list_cache[news["id"]] = news
        else:
            self.local_news_list_cache[news["id"]] = news

        if len(self.local_news_list_cache) > self.max_cache:
            news_id = list(self.local_news_list_cache.keys())[0]
            self.local_news_list_cache.pop(news_id)

    def del_from_cache(self, news_id: int):
        """
            del a news from cache
        """
        if news_id in self.local_news_list_cache:
            self.local_news_list_cache.pop(news_id)

    def del_one_local_news(self, news_id: int) -> bool:
        """
            del one local news
        """
        if isinstance(news_id, int):
            try:
                self.del_from_cache(news_id)
                local_news = LocalNews.objects.filter(news_id=news_id).first()
                if local_news:
                    local_news.cite_count -= 1
                    if local_news.cite_count <= 0:
                        LocalNews.objects.filter(news_id=news_id).delete()
                        return True
                    local_news.full_clean()
                    local_news.save()
            except Exception as error:
                print(error)
                return False
            return True
        return False

    def del_local_news(self, news) -> bool:
        """
            del local news
        """
        if isinstance(news, dict):
            return self.del_one_local_news(news["id"])
        if isinstance(news, list):
            news_list = news
            for _news in news_list:
                if isinstance(_news, dict):
                    if not self.del_one_local_news(_news["id"]):
                        return False
                elif isinstance(_news, int):
                    if not self.del_one_local_news(_news):
                        return False
            return True
        if isinstance(news, int):
            return self.del_one_local_news(news)
        return False

    def save_one_local_news(self, news: dict) -> bool:
        """
            save one local news
        """
        if isinstance(news, dict):
            try:
                self.add_to_cache(news)
                local_news = LocalNews.objects.filter(news_id=int(news["id"])).first()
                if local_news:
                    local_news.cite_count += 1
                    local_news.full_clean()
                    local_news.save()
                    return True
                local_news = LocalNews(
                    data=news_formator(news),
                    news_id=int(news["id"]),
                    ai_processed=False, cite_count=1
                )
                local_news_dict = news_formator(news)
                if not ("full_content" in local_news_dict and local_news_dict["full_content"]):
                    print(dict(local_news_dict).keys())
                    print(local_news.ai_processed)
                    local_news.ai_processed = True
                local_news.full_clean()
                local_news.save()
            except Exception as error:
                print(error)
                return False
            return True
        return False

    def save_local_news(self, news) -> bool:
        """
            save local news
        """
        if isinstance(news, dict):
            return self.save_one_local_news(news)
        if isinstance(news, list):
            news_list = news
            for _news in news_list:
                if not self.save_one_local_news(_news):
                    return False
            return True
        return False
