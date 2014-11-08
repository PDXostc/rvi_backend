# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pac_name', models.CharField(max_length=256, verbose_name=b'Package Name')),
                ('pac_version', models.CharField(max_length=256, verbose_name=b'Package Version')),
                ('pac_file', models.FileField(upload_to=b'', verbose_name=b'Package File')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
