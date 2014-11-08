# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0014_auto_20141105_1829'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='retry',
            name='ret_deadline',
        ),
        migrations.AddField(
            model_name='retry',
            name='ret_finish',
            field=models.DateTimeField(null=True, verbose_name=b'Retry Finished', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='retry',
            name='ret_start',
            field=models.DateTimeField(verbose_name=b'Retry Started'),
        ),
    ]
