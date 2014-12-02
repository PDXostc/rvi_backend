# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0008_auto_20141125_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='veh_picture',
            field=models.ImageField(upload_to=b'', null=True, verbose_name=b'Vehicle Picture', blank=True),
            preserve_default=True,
        ),
    ]
