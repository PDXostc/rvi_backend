# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0004_auto_20141009_2152'),
    ]

    operations = [
        migrations.CreateModel(
            name='Retry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ret_start', models.DateTimeField(verbose_name=b'Update Started')),
                ('ret_deadline', models.DateTimeField(verbose_name=b'Update Deadline')),
                ('ret_status', models.CharField(default=b'AC', max_length=2, verbose_name=b'Retry Status', choices=[(b'AC', b'Active'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed')])),
                ('ret_update', models.ForeignKey(verbose_name=b'Update', to='sota.Update')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_status',
            field=models.CharField(default=b'PE', max_length=2, verbose_name=b'Update Status', choices=[(b'PE', b'Pending'), (b'SC', b'Scheduled'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed'), (b'EX', b'Expired')]),
        ),
    ]
