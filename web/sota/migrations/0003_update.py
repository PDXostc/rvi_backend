# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sota.models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicles', '0003_auto_20141009_2054'),
        ('sota', '0002_package_pac_arch'),
    ]

    operations = [
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upd_status', models.CharField(default=b'PE', max_length=2, verbose_name=b'Update Status', choices=[(b'PE', b'Pending'), (b'SC', b'Scheduled'), (b'AB', b'Aborted'), (b'SU', b'Success'), (b'FA', b'Failed')])),
                ('upd_timeout', models.IntegerField(verbose_name=b'Timeout', validators=[sota.models.validate_upd_timeout])),
                ('upd_package', models.ForeignKey(to='sota.Package')),
                ('upd_vehicle', models.ForeignKey(to='vehicles.Vehicle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
