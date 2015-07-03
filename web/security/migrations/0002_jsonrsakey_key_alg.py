# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jsonrsakey',
            name='key_alg',
            field=models.CharField(default='NONE', max_length=20, verbose_name=b'Algorithm'),
            preserve_default=False,
        ),
    ]
