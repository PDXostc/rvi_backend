# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sota.models


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0007_auto_20141009_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='update',
            name='upd_current',
            field=models.IntegerField(default=b'3', verbose_name=b'Current Retries', validators=[sota.models.validate_upd_retries]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_retries',
            field=models.IntegerField(default=b'3', verbose_name=b'Maximum Retries', validators=[sota.models.validate_upd_retries]),
        ),
    ]
