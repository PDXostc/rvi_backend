# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0004_auto_20150630_1921'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jsonwebkey',
            name='key_active',
        ),
    ]
