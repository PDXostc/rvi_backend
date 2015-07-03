# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JSONRSAKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_kty', models.CharField(default=b'rsa', verbose_name=b'Key Type', max_length=3, editable=False, choices=[(b'ec', b'Elliptic Curve'), (b'rsa', b'RSA'), (b'oct', b'Octet Sequence')])),
                ('key_use', models.CharField(default=b'sig', max_length=3, verbose_name=b'Public Key Use', choices=[(b'sig', b'Signature'), (b'enc', b'Encryption')])),
                ('key_created', models.DateTimeField(auto_now_add=True)),
                ('key_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
