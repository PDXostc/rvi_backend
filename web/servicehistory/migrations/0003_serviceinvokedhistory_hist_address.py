# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicehistory', '0002_auto_20150828_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceinvokedhistory',
            name='hist_address',
            field=models.CharField(default=b'Not Available', max_length=256, verbose_name=b'Address'),
            preserve_default=True,
        ),
    ]
