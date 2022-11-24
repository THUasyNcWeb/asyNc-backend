"""
    configures
"""

TESTING_MODE = False

EXPIRE_TIME = 7 * 86400  # 30s for testing. 7 days for deploy.
SECRET_KEY = "A good coder is all you need."

TOKEN_WHITE_LIST = {}  # storage alive token for each user

CATEGORY_LIST = [
    "",
    "ent",
    "sports",
    "mil",
    "politics",
    "tech",
    "social",
    "finance",
    "auto",
    "game",
    "women",
    "health",
    "history",
    "edu"
]

CATEGORY_FRONT_TO_BACKEND = {
    "": "",
    "home": "",
    "sport": "sports",
    "fashion": "women",
    "ent": "ent",
    "sports": "sports",
    "mil": "mil",
    "politics": "politics",
    "tech": "tech",
    "social": "social",
    "finance": "finance",
    "auto": "auto",
    "game": "game",
    "women": "women",
    "health": "health",
    "history": "history",
    "edu": "edu",
}

FRONT_PAGE_NEWS_NUM = 200

FAVORITES_PRE_PAGE = 10

DB_CHECK_INTERVAL = 1

DB_UPDATE_MINIMUM_INTERVAL = 300

MAX_RETURN_USER_TAG = 128

MAX_USER_SEARCH_HISTORY = 256

CACHE_NEWSPOOL_MAX = len(CATEGORY_LIST) * FRONT_PAGE_NEWS_NUM * 16

DB_NEWS_LOOK_BACK = 65536

MAX_LOCAL_NEWS_LIST_CACHE = 65536
