# Generated by Django 3.0.7 on 2020-06-17 14:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0011_auto_20200617_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 17, 20, 8, 21, 775358)),
        ),
    ]