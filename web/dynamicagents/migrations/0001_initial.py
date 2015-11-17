# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dynamicagents.models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0019_vehicle_seq_counter'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pac_name_da', models.CharField(max_length=256, verbose_name=b'Agent Name')),
                ('pac_description_da', models.TextField(null=True, verbose_name=b'Agent Description', blank=True)),
                ('pac_version_da', models.CharField(max_length=256, verbose_name=b'Agent Version')),
                ('pac_file_da', models.FileField(upload_to=b'', verbose_name=b'Agent File')),
                ('pac_start_cmd', models.TextField(verbose_name=b'Agent Launch Command')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Retry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ret_start_da', models.DateTimeField(verbose_name=b'Retry Started')),
                ('ret_timeout_da', models.DateTimeField(null=True, verbose_name=b'Retry Valid', blank=True)),
                ('ret_finish_da', models.DateTimeField(null=True, verbose_name=b'Retry Finished', blank=True)),
                ('ret_status_da', models.CharField(default=b'PE', max_length=2, verbose_name=b'Retry Status', choices=[(b'PE', b'Pending'), (b'ST', b'Started'), (b'RU', b'Running'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed'), (b'WA', b'Waiting'), (b'RE', b'Rejected')])),
            ],
            options={
                'verbose_name_plural': 'Retries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UpdateDA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upd_status_da', models.CharField(default=b'PE', max_length=2, verbose_name=b'Update Status', choices=[(b'PE', b'Pending'), (b'ST', b'Started'), (b'RU', b'Running'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed'), (b'WA', b'Waiting'), (b'RE', b'Rejected')])),
                ('upd_timeout_da', models.DateTimeField(verbose_name=b'Valid Until')),
                ('upd_retries_da', models.IntegerField(default=b'0', verbose_name=b'Maximum Retries', validators=[dynamicagents.models.validate_upd_retries_da])),
                ('upd_package_da', models.ForeignKey(verbose_name=b'Agent', to='dynamicagents.Agent')),
                ('upd_vehicle_da', models.ForeignKey(verbose_name=b'Vehicle', to='vehicles.Vehicle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='retry',
            name='ret_update_da',
            field=models.ForeignKey(verbose_name=b'Update', to='dynamicagents.UpdateDA'),
            preserve_default=True,
        ),
    ]
