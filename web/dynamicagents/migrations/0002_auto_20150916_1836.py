# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dynamicagents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RetryDA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ret_start_da', models.DateTimeField(verbose_name=b'Retry Started')),
                ('ret_timeout_da', models.DateTimeField(null=True, verbose_name=b'Retry Valid', blank=True)),
                ('ret_finish_da', models.DateTimeField(null=True, verbose_name=b'Retry Finished', blank=True)),
                ('ret_status_da', models.CharField(default=b'PE', max_length=2, verbose_name=b'Retry Status', choices=[(b'PE', b'Pending'), (b'ST', b'Started'), (b'RU', b'Running'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed'), (b'WA', b'Waiting'), (b'RE', b'Rejected')])),
                ('ret_update_da', models.ForeignKey(verbose_name=b'Update', to='dynamicagents.UpdateDA')),
            ],
            options={
                'verbose_name_plural': 'Retries',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='retry',
            name='ret_update_da',
        ),
        migrations.DeleteModel(
            name='Retry',
        ),
    ]
