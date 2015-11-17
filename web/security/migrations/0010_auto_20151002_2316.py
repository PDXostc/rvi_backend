# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import security.models


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0009_auto_20150701_1937'),
    ]

    operations = [
        migrations.CreateModel(
            name='CANFWKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_name', models.CharField(max_length=256, null=True, verbose_name=b'Key Name', blank=True)),
                ('key_created', models.DateTimeField(auto_now_add=True)),
                ('key_updated', models.DateTimeField(auto_now=True)),
                ('symm_key', models.TextField(default=security.models.key_gen, null=True, verbose_name=b'Random Key String')),
            ],
            options={
                'verbose_name': 'CAN FW Key',
                'verbose_name_plural': 'CAN FW Keys',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='jsonwebkey',
            options={'verbose_name': 'RVI Key', 'verbose_name_plural': 'RVI Keys'},
        ),
    ]
