# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0009_remote_rem_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'9722ab6c-3206-423c-914e-d46c326a47b4', verbose_name=b'Remote UUID', max_length=256, editable=False),
            preserve_default=True,
        ),
    ]
