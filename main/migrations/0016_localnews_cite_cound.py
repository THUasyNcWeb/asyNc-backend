# Generated by Django 4.1.1 on 2022-11-19 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_localnews_ai_processed_localnews_news_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='localnews',
            name='cite_cound',
            field=models.IntegerField(default=0),
        ),
    ]
