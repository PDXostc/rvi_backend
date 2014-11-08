# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sota.models


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0008_auto_20141010_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='update',
            name='upd_current',
        ),
        migrations.AlterField(
            model_name='retry',
            name='ret_deadline',
            field=models.DateField(verbose_name=b'Update Deadline'),
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_retries',
            field=models.IntegerField(default=b'0', verbose_name=b'Maximum Retries', validators=[sota.models.validate_upd_retries]),
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_status',
            field=models.CharField(default=b'PE', max_length=2, verbose_name=b'Update Status', choices=[(b'PE', b'Pending'), (b'ST', b'Started'), (b'RU', b'Running'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed')]),
        ),
    ]
