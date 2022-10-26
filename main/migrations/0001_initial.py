# Generated by Django 4.1.1 on 2022-10-26 09:23

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(db_index=True, primary_key=True, serialize=False)),
                ('news_url', models.URLField()),
                ('media', models.CharField(max_length=20)),
                ('category', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=5)),
                ('tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=8)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('content', models.TextField()),
                ('first_img_url', models.URLField()),
                ('pub_time', models.DateTimeField()),
            ],
            options={
                'db_table': 'news',
            },
        ),
        migrations.CreateModel(
            name='UserBasicInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=12, unique=True)),
                ('password', models.CharField(max_length=40)),
                ('signature', models.CharField(blank=True, max_length=200)),
                ('tags', models.JSONField(null=True)),
            ],
            options={
                'db_table': 'user_basic_info',
            },
        ),
        migrations.CreateModel(
            name='UserPreference',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('word', models.CharField(max_length=10)),
                ('num', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userbasicinfo')),
            ],
            options={
                'db_table': 'user_preference',
            },
        ),
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.CharField(max_length=38)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.userbasicinfo')),
            ],
            options={
                'db_table': 'search_history',
            },
        ),
    ]
