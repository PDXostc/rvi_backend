# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dblog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='generallog',
            name='level',
            field=models.CharField(max_length=10, verbose_name=b'Level'),
        ),
        migrations.AlterField(
            model_name='generallog',
            name='message',
            field=models.TextField(verbose_name=b'Message'),
        ),
        migrations.AlterField(
            model_name='generallog',
            name='time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Timestamp'),
        ),
        migrations.AlterField(
            model_name='sotalog',
            name='level',
            field=models.CharField(max_length=10, verbose_name=b'Level'),
        ),
        migrations.AlterField(
            model_name='sotalog',
            name='message',
            field=models.TextField(verbose_name=b'Message'),
        ),
        migrations.AlterField(
            model_name='sotalog',
            name='time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Timestamp'),
        ),
    ]
