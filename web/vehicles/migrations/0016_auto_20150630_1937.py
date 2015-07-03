# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0015_auto_20150630_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehicle',
            name='veh_key',
            field=models.OneToOneField(null=True, verbose_name=b'Key', to='security.JSONWebKey'),
            preserve_default=True,
        ),
    ]
