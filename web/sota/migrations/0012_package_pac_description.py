# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0011_auto_20141022_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='pac_description',
            field=models.TextField(null=True, verbose_name=b'Package Description', blank=True),
            preserve_default=True,
        ),
    ]
