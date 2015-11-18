# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicehistory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceinvokedhistory',
            name='hist_timestamp',
            field=models.DateTimeField(max_length=100, verbose_name=b'Timestamp'),
            preserve_default=True,
        ),
    ]
