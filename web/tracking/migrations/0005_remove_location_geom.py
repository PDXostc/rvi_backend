# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0004_auto_20141121_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='geom',
        ),
    ]
