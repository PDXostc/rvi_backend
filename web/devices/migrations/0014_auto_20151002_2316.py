# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0013_auto_20151001_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'6faa02f5-40d8-4527-8357-918f3bb10ee2', verbose_name=b'Remote UUID', unique=True, max_length=60, editable=False),
            preserve_default=True,
        ),
    ]
