# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('security', '0008_auto_20150701_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jsonwebkey',
            name='key_alg_enc',
            field=models.CharField(default=b'A128CBC-HS256', max_length=20, verbose_name=b'Encryption Algorithm', choices=[(b'A128CBC-HS256', b'AES CBC using 128-bit key and HMAC with SHA-256'), (b'A192CBC-HS384', b'AES CBC using 192-bit key and HMAC with SHA-384'), (b'A256CBC-HS512', b'AES CBC using 256-bit key and HMAC with SHA-512')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jsonwebkey',
            name='key_alg_sig',
            field=models.CharField(default=b'RS256', max_length=20, verbose_name=b'Signature Algorithm', choices=[(b'HS256', b'HMAC using SHA-256'), (b'HS384', b'HMAC using SHA-384'), (b'HS512', b'HMAC using SHA-512'), (b'RS256', b'RSASSA-PKCS1-v1_5 using SHA-256'), (b'RS384', b'RSASSA-PKCS1-v1_5 using SHA-384'), (b'RS512', b'RSASSA-PKCS1-v1_5 using SHA-512'), (b'ES256', b'ECDSA using P-256 and SHA-256'), (b'ES384', b'ECDSA using P-384 and SHA-384'), (b'ES512', b'ECDSA using P-512 and SHA-512'), (b'PS256', b'RSASSA-PSS using SHA-256 and MGF1 with SHA-256'), (b'PS384', b'RSASSA-PSS using SHA-384 and MGF1 with SHA-384'), (b'PS512', b'RSASSA-PSS using SHA-512 and MGF1 with SHA-512')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jsonwebkey',
            name='key_pem',
            field=models.TextField(verbose_name=b'Key PEM'),
            preserve_default=True,
        ),
    ]
