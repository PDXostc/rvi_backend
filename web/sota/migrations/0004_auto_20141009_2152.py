# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sota.models


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0003_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='update',
            name='upd_retries',
            field=models.IntegerField(default=b'3', verbose_name=b'Retries', validators=[sota.models.validate_upd_retries]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_package',
            field=models.ForeignKey(verbose_name=b'Package', to='sota.Package'),
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_vehicle',
            field=models.ForeignKey(verbose_name=b'Vehicle', to='vehicles.Vehicle'),
        ),
    ]
