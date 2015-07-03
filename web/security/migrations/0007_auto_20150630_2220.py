# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0006_jsonwebkey_key_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='jsonwebkey',
            name='key_valid_from',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 22, 20, 6, 259001), verbose_name=b'Valid From'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jsonwebkey',
            name='key_valid_to',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 30, 22, 20, 13, 874740), verbose_name=b'Valid To'),
            preserve_default=False,
        ),
    ]
