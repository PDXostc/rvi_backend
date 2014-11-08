# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sota', '0006_auto_20141009_2227'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_timestamp', models.DateTimeField(verbose_name=b'Timestamp')),
                ('log_message', models.TextField(verbose_name=b'Message')),
                ('log_retry', models.ForeignKey(verbose_name=b'Retry', to='sota.Retry')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='update',
            name='upd_timeout',
            field=models.DateField(verbose_name=b'Valid Until'),
        ),
    ]
