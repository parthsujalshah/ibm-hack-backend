# Generated by Django 3.0.7 on 2020-06-16 12:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0003_auto_20200616_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 16, 17, 37, 27, 100365)),
        ),
    ]
