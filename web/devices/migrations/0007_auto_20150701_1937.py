# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_auto_20150630_2203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='remote',
            name='rem_doors',
        ),
        migrations.AddField(
            model_name='device',
            name='dev_rvibasename',
            field=models.CharField(default='jlr.com', max_length=256, verbose_name=b'RVI Domain'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='remote',
            name='rem_lock',
            field=models.BooleanField(default=False, verbose_name=b'Lock/Unlock'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remote',
            name='rem_lights',
            field=models.BooleanField(default=False, verbose_name=b'Turn On/Off Lights'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='remote',
            name='rem_trunk',
            field=models.BooleanField(default=False, verbose_name=b'Open/Close Trunk'),
            preserve_default=True,
        ),
    ]
