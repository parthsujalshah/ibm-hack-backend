# Generated by Django 3.0.8 on 2020-07-09 10:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0051_auto_20200709_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 9, 16, 23, 5, 262267)),
        ),
    ]