# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0012_auto_20151001_2206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'440e61e1-5f62-4d0e-a57b-c527c28963c8', verbose_name=b'Remote UUID', unique=True, max_length=60, editable=False),
            preserve_default=True,
        ),
    ]
