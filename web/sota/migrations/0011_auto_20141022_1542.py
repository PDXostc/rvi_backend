# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0010_auto_20141011_0250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='log_retry',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
