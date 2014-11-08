# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0017_auto_20141106_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='update',
            name='upd_timeout',
            field=models.DateTimeField(verbose_name=b'Valid Until'),
        ),
    ]
