# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0005_device_dev_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='dev_key',
            field=models.OneToOneField(null=True, verbose_name=b'Key', to='security.JSONWebKey'),
            preserve_default=True,
        ),
    ]
