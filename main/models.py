"""
Models for db.
"""
from django.db import models
from django.db.models import AutoField, CharField, URLField, DateTimeField
from django.db.models import TextField, ForeignKey, IntegerField, JSONField
from django.db.models import BooleanField
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class News(models.Model):
    """
        model for news
    """
    id = AutoField(primary_key=True, db_index=True)
    news_url = URLField(max_length=200)
    media = CharField(max_length=20)
    category = CharField(max_length=20)
    tags = ArrayField(models.CharField(max_length=30))
    title = CharField(max_length=200)
    description = TextField()
    content = TextField()
    first_img_url = TextField(blank=True)
    pub_time = DateTimeField()

    class Meta:
        """
            set table name in db
        """
        db_table = "news"


class LocalNews(models.Model):
    """
        model for news
    """
    id = AutoField(primary_key=True, db_index=True)
    news_id = IntegerField(default=0)
    cite_count = IntegerField(default=0)
    ai_processed = BooleanField(default=False)
    data = JSONField(null=True, blank=True, default=dict)

    class Meta:
        """
            set table name in db
        """
        db_table = "local_news"


class UserBasicInfo(models.Model):
    """
        model for user
    """
    id = AutoField(primary_key=True)
    tags = JSONField(null=True, blank=True, default=dict)
    user_name = CharField(max_length=12, unique=True)
    password = CharField(max_length=40)
    signature = CharField(max_length=200, blank=True)
    mail = CharField(max_length=100, blank=True)
    avatar = TextField(blank=True)
    register_date = DateTimeField(auto_now_add=True)

    # favorites
    favorites = JSONField(null=True, blank=True, default=dict)
    # readlater
    readlist = JSONField(null=True, blank=True, default=dict)
    # read history
    read_history = JSONField(null=True, blank=True, default=dict)
    # search history
    search_history = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return str(self.user_name)

    class Meta:
        """
            set table name in db
        """
        db_table = "user_basic_info"


class SearchHistory(models.Model):
    """
        model for search history
    """
    id = AutoField(primary_key=True)
    user = ForeignKey(UserBasicInfo, on_delete=models.CASCADE)
    content = CharField(max_length=38)

    class Meta:
        """
            set table name in db
        """
        db_table = "search_history"


class UserPreference(models.Model):
    """
        model for user preference
    """
    id = AutoField(primary_key=True)
    user = ForeignKey(UserBasicInfo, on_delete=models.CASCADE)
    word = CharField(max_length=10)
    num = IntegerField(default=0)

    class Meta:
        """
            set table name in db
        """
        db_table = "user_preference"
