# Generated by Django 4.1.1 on 2022-10-26 02:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_user_basic_info_password'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='search_history',
            new_name='SearchHistory',
        ),
        migrations.RenameModel(
            old_name='user_basic_info',
            new_name='UserBasicInfo',
        ),
        migrations.RenameModel(
            old_name='user_preference',
            new_name='UserPreference',
        ),
        migrations.RemoveField(
            model_name='news',
            name='key_words',
        ),
        migrations.AlterField(
            model_name='news',
            name='category',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=5),
        ),
        migrations.AlterField(
            model_name='news',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=8),
        ),
        migrations.AlterField(
            model_name='news',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
