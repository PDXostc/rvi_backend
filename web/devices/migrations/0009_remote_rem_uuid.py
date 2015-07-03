# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0008_auto_20150701_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'5587b871-76f7-4106-b30b-013ebc9b6efb', verbose_name=b'Remote UUID', max_length=256, editable=False),
            preserve_default=True,
        ),
    ]
