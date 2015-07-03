# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0007_auto_20150630_2220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jsonwebkey',
            name='key_pem_private',
        ),
        migrations.RemoveField(
            model_name='jsonwebkey',
            name='key_pem_public',
        ),
        migrations.AddField(
            model_name='jsonwebkey',
            name='key_pem',
            field=models.TextField(null=True, verbose_name=b'Key PEM', blank=True),
            preserve_default=True,
        ),
    ]
