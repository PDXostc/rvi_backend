# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0011_auto_20150901_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'<function uuid4 at 0x1688a70>', verbose_name=b'Remote UUID', unique=True, max_length=60, editable=False),
            preserve_default=True,
        ),
    ]
