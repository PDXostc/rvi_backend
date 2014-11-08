# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0015_auto_20141105_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='retry',
            name='ret_timeout',
            field=models.DateField(null=True, verbose_name=b'Retry Valid', blank=True),
            preserve_default=True,
        ),
    ]
