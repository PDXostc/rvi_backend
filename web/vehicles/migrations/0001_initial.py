# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('veh_name', models.CharField(max_length=256)),
                ('veh_make', models.CharField(max_length=256)),
                ('veh_model', models.CharField(max_length=256)),
                ('veh_vin', models.CharField(max_length=256)),
                ('veh_year', models.CharField(max_length=4)),
                ('veh_rvibasename', models.CharField(max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
