# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0002_jsonrsakey_key_alg'),
    ]

    operations = [
        migrations.CreateModel(
            name='JSONWebKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key_kty', models.CharField(default=b'rsa', verbose_name=b'Key Type', max_length=3, editable=False, choices=[(b'rsa', b'RSA')])),
                ('key_alg_sig', models.CharField(default=b'RS256', max_length=20, verbose_name=b'Signature Algorithm', choices=[(b'HS256', b'HMAC using SHA-256'), (b'HS384', b'HMAC using SHA-384'), (b'HS512', b'HMAC using SHA-512'), (b'RS256', b'RSASSA-PKCS1-v1_5 using SHA-256'), (b'RS384', b'RSASSA-PKCS1-v1_5 using SHA-384'), (b'RS512', b'RSASSA-PKCS1-v1_5 using SHA-512'), (b'ES256', b'ECDSA using P-256 and SHA-256'), (b'ES384', b'ECDSA using P-384 and SHA-384'), (b'ES512', b'ECDSA using P-512 and SHA-512'), (b'PS256', b'RSASSA-PSS using SHA-256 and MGF1 with SHA-256'), (b'PS384', b'RSASSA-PSS using SHA-384 and MGF1 with SHA-384'), (b'PS512', b'RSASSA-PSS using SHA-512 and MGF1 with SHA-512'), (b'NONE', b'No digital signature or MAC performed')])),
                ('key_alg_enc', models.CharField(default=b'A128CBC-HS256', max_length=20, verbose_name=b'Encryption Algorithm', choices=[(b'A128CBC-HS256', b'AES CBC using 128-bit key and HMAC with SHA-256'), (b'A192CBC-HS384', b'AES CBC using 192-bit key and HMAC with SHA-384'), (b'A256CBC-HS512', b'AES CBC using 256-bit key and HMAC with SHA-512'), (b'A128GCM', b'AES GCM using 128-bit key'), (b'A192GCM', b'AES GCM using 192-bit key'), (b'A256GCM', b'AES GCM using 256-bit key')])),
                ('key_created', models.DateTimeField(auto_now_add=True)),
                ('key_updated', models.DateTimeField(auto_now=True)),
                ('key_pem_private', models.TextField(null=True, verbose_name=b'Private Key PEM', blank=True)),
                ('key_pem_public', models.TextField(null=True, verbose_name=b'Public Key PEM', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='JSONRSAKey',
        ),
    ]
