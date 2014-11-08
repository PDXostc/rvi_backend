# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0005_auto_20141009_2207'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='retry',
            options={'verbose_name_plural': 'Retries'},
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_timeout',
            field=models.DateTimeField(verbose_name=b'Timeout'),
        ),
    ]
