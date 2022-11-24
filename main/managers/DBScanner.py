"""
    scan crawler db
"""
import time
import pickle

from .NewsCache import NewsCache


class DBScanner():
    """
        news db scanner
    """
    def __init__(
        self, db_connection, news_cache: NewsCache, category_list: list, get_data_from_db,
        testing_mode=False, front_page_news_num=10, db_check_interval=8,
        db_news_look_back=65536, db_update_minimum_interval=8
    ) -> None:
        """
            init
        """
        self.db_connection = db_connection
        self.news_cache = news_cache
        self.news_num = 0
        self.category_list = category_list
        self.testing_mode = testing_mode
        self.front_page_news_num = front_page_news_num
        self.db_check_interval = db_check_interval
        self.db_news_look_back = db_news_look_back
        self.db_update_minimum_interval = db_update_minimum_interval
        self.get_data_from_db = get_data_from_db

    def get_db_news_num(self) -> int:
        """
            get db news num
        """
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("select count(*) from news")
            row = cursor.fetchone()
        except Exception as error:
            print("[error]", error)
        return row[0]

    def check_db_update(self) -> bool:
        """
            check if db updated
        """
        if self.testing_mode:
            return False
        db_news_num = self.get_db_news_num()
        self.news_cache.last_check_time = time.time()
        if not self.news_num == db_news_num:
            self.news_num = db_news_num
            print("db_news_num:", self.news_num, time.time())
            self.news_cache.last_change_time = time.time()
            return True
        return False

    def update_cache(self) -> None:
        """
            update all news cache
        """
        print("Updating cache", time.time())
        if self.testing_mode:
            with open("data/news_cache.pkl", "rb") as file:
                self.news_cache.cache = pickle.load(file)
            self.news_cache.last_update_time = time.time()
            return
        db_news_list = self.get_data_from_db(
            connection=self.db_connection,
            filter_command="id > {id}".format(id=self.news_cache.max_news_id),
            select=[
                "title","news_url","first_img_url","media",
                "pub_time","id","category","content","tags"
            ],
            order_command="ORDER BY pub_time DESC",
            limit=65536  # protection
        )
        self.news_cache.update_cache(db_news_list=db_news_list)
        print("cache shape:", [len(x) for x in self.news_cache.cache.values()])
        self.news_cache.save_local_cache()

    def run(self, _=None) -> None:
        """
            run timer
        """
        try:
            print("Starting runner")
            print("self.db_check_interval =", self.db_check_interval)
            self.news_cache.load_local_cache()
            print("cache shape", [len(x) for x in self.news_cache.cache.values()])

            print("Cache initialization:")

            if not self.testing_mode:
                self.check_db_update()

                db_news_list = []
                for category in self.category_list:
                    print("init category", category, "from db...")
                    db_news_list += self.get_data_from_db(
                        connection=self.db_connection,
                        filter_command="id > {id} AND category='{category}'".format(
                            id=max(self.news_cache.max_news_id, self.news_num - self.db_news_look_back),
                            category=category
                        ),
                        select=[
                            "title","news_url","first_img_url","media",
                            "pub_time","id","category","content","tags"
                        ],
                        order_command="ORDER BY pub_time DESC",
                        limit=self.front_page_news_num
                    )
                self.news_cache.update_cache(db_news_list)
                print("cache shape:", [len(x) for x in self.news_cache.cache.values()])

            print("Cache initialization completed.")

            self.news_cache.save_local_cache()

            print("cache checker loop begin")

            while True:
                try:
                    if self.check_db_update():
                        self.update_cache()
                    if time.time() - self.news_cache.last_update_time > self.db_update_minimum_interval:
                        self.update_cache()
                except Exception as error:
                    print("[error]", error)
                time.sleep(self.db_check_interval)

        except Exception as error:
            print("[error]", error)
        time.sleep(self.db_check_interval)
