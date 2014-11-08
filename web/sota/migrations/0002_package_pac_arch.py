# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='pac_arch',
            field=models.CharField(default='i686', max_length=256, verbose_name=b'Package Architecture'),
            preserve_default=False,
        ),
    ]
