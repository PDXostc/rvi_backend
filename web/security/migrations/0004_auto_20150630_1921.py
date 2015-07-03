# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0003_auto_20150630_1756'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jsonwebkey',
            options={'verbose_name': 'Key', 'verbose_name_plural': 'Keys'},
        ),
        migrations.AddField(
            model_name='jsonwebkey',
            name='key_active',
            field=models.BooleanField(default=True, verbose_name=b'Active'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jsonwebkey',
            name='key_kty',
            field=models.CharField(default=b'rsa', max_length=3, verbose_name=b'Key Type', choices=[(b'rsa', b'RSA')]),
            preserve_default=True,
        ),
    ]
