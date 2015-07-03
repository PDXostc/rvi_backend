# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20150622_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='device',
            name='dev_pubkey',
        ),
    ]
