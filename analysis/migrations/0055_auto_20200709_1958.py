# Generated by Django 3.0.8 on 2020-07-09 14:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0054_auto_20200709_1948'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 9, 19, 58, 58, 286923)),
        ),
    ]
