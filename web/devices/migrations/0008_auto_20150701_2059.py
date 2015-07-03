# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0007_auto_20150701_1937'),
    ]

    operations = [
        migrations.AddField(
            model_name='remote',
            name='rem_created',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 1, 20, 59, 35, 27362, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='remote',
            name='rem_updated',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 1, 20, 59, 46, 379322, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
