# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0010_auto_20141011_0250'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('level', models.CharField(max_length=10)),
                ('message', models.TextField()),
            ],
            options={
                'verbose_name': 'General Log',
                'verbose_name_plural': 'General Log',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SotaLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('level', models.CharField(max_length=10)),
                ('message', models.TextField()),
                ('retry', models.ForeignKey(verbose_name=b'Retry', to='sota.Retry')),
            ],
            options={
                'verbose_name': 'SOTA Log',
                'verbose_name_plural': 'SOTA Log',
            },
            bases=(models.Model,),
        ),
    ]
