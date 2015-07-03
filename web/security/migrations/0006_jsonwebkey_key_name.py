# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0005_remove_jsonwebkey_key_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='jsonwebkey',
            name='key_name',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Key Name', blank=True),
            preserve_default=True,
        ),
    ]
