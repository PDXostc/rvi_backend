# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0010_auto_20150703_0021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remote',
            name='rem_uuid',
            field=models.CharField(default=b'8b0183e4-e259-4184-8a46-e178c39b6e4d', verbose_name=b'Remote UUID', max_length=256, editable=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remote',
            name='rem_validfrom',
            field=models.DateTimeField(max_length=100, verbose_name=b'Valid From'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remote',
            name='rem_validto',
            field=models.DateTimeField(max_length=100, verbose_name=b'Valid To'),
            preserve_default=True,
        ),
    ]
