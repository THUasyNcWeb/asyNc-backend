# Generated by Django 4.1.1 on 2022-10-26 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_userbasicinfo_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbasicinfo',
            name='signature',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
