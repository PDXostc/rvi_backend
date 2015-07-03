# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vehicles', '0011_vehicle_veh_rvistatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='user',
            field=models.ForeignKey(default=1, editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
