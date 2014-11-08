# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0016_retry_ret_timeout'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retry',
            name='ret_timeout',
            field=models.DateTimeField(null=True, verbose_name=b'Retry Valid', blank=True),
        ),
    ]
