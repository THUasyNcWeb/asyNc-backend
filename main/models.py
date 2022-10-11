from django.db import models
from django.db.models import AutoField, CharField, URLField, DateTimeField, TextField, ForeignKey, IntegerField
from django.contrib.postgres.fields import JSONField, ArrayField

# Create your models here.

class news(models.Model):
    id = AutoField(primary_key=True, db_index=True)
    news_url = URLField(max_length = 200)
    media = CharField(max_length = 20)
    category = CharField(models.CharField(max_length = 10), max_length = 5)
    key_words = ArrayField(models.CharField(max_length = 10), size = 8)
    tags = ArrayField(models.CharField(max_length = 10), size = 8)
    title = CharField(max_length = 50)
    description = TextField()
    content = TextField()
    first_img_url = URLField(max_length = 200)
    pub_time = DateTimeField()

class user_basic_info(models.Model):
    id = AutoField(primary_key = True)
    user_name = CharField(max_length = 12, unique=True)
    password = CharField(max_length = 18)
    # register_date = DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class search_history(models.Model):
    id = AutoField(primary_key = True)
    user = ForeignKey(user_basic_info, on_delete = models.CASCADE)
    content = CharField(max_length = 38)

class user_preference(models.Model):
    id = AutoField(primary_key = True)
    user = ForeignKey(user_basic_info, on_delete = models.CASCADE)
    word = CharField(max_length = 10)
    num = IntegerField(default = 0)