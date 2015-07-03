# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vehicles', '0014_auto_20150620_0011'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dev_name', models.CharField(max_length=256, verbose_name=b'Device Name')),
                ('dev_owner', models.CharField(max_length=256, verbose_name=b'Owner')),
                ('dev_mdn', models.CharField(max_length=256, verbose_name=b'Phone Number')),
                ('dev_min', models.CharField(max_length=256, verbose_name=b'Mobile Identification Number')),
                ('dev_imei', models.CharField(max_length=256, verbose_name=b'Mobile Equipment Identifier')),
                ('dev_wifimac', models.CharField(max_length=256, verbose_name=b'WiFi MAC')),
                ('dev_btmac', models.CharField(max_length=256, verbose_name=b'Bluetooth MAC')),
                ('dev_uuid', models.CharField(max_length=256, verbose_name=b'UUID')),
                ('dev_pubkey', models.TextField(max_length=2048, null=True, verbose_name=b'Public Key', blank=True)),
                ('account', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Devices',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Remote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rem_name', models.CharField(max_length=256, verbose_name=b'Remote Name')),
                ('rem_validfrom', models.DateTimeField(verbose_name=b'Valid From')),
                ('rem_validto', models.DateTimeField(verbose_name=b'Valid To')),
                ('rem_engine', models.BooleanField(default=False, verbose_name=b'Start/Stop Engine')),
                ('rem_doors', models.BooleanField(default=False, verbose_name=b'Unlock/Lock Doors')),
                ('rem_trunk', models.BooleanField(default=False, verbose_name=b'Open Trunk')),
                ('rem_windows', models.BooleanField(default=False, verbose_name=b'Open/Close Windows')),
                ('rem_lights', models.BooleanField(default=False, verbose_name=b'Turn on/off Lights')),
                ('rem_hazard', models.BooleanField(default=False, verbose_name=b'Flash Hazard Lights')),
                ('rem_horn', models.BooleanField(default=False, verbose_name=b'Honk Horn')),
                ('rem_device', models.ForeignKey(verbose_name=b'Device', to='devices.Device')),
                ('rem_vehicle', models.ForeignKey(verbose_name=b'Vehicle', to='vehicles.Vehicle')),
            ],
            options={
                'verbose_name_plural': 'Remotes',
            },
            bases=(models.Model,),
        ),
    ]
