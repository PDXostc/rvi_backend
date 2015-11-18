# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vehicles', '0017_auto_20150701_1937'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceInvokedHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hist_service', models.CharField(max_length=256, verbose_name=b'Service Name')),
                ('hist_latitude', models.FloatField(verbose_name=b'Latitude [deg]')),
                ('hist_longitude', models.FloatField(verbose_name=b'Longitude [deg]')),
                ('hist_timestamp', models.DateTimeField(max_length=100, verbose_name=b'Valid From')),
                ('hist_user', models.ForeignKey(verbose_name=b'User', to=settings.AUTH_USER_MODEL)),
                ('hist_vehicle', models.ForeignKey(verbose_name=b'Vehicle', to='vehicles.Vehicle')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
