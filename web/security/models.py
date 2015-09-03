"""
Copyright (C) 2014, Jaguar Land Rover

This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/

Rudolf Streif (rstreif@jaguarlandrover.com) 
"""

import string
import hashlib
import jwt
import random
from django.utils.functional import lazy
from django.db import models
from django.utils import timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from base64 import urlsafe_b64encode

N = 40
string_param = string.ascii_letters + string.digits + string.punctuation

def key_gen(size=N, chars=string_param):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))

class JSONWebKey(models.Model):
    """
    Class for JSON web key (JWK). The class stores a public and/or private key
    in PEM (Privacy Enhancement for Internet Electronic Mail) format.
    The public key is used for encryption and signature verification while the
    private key is used for decryption and signing.
    JSON is created dynamically from the key data.
    """
    TAG_PKCS1_PRIVATE_BEGIN  = '-----BEGIN RSA PRIVATE KEY-----'
    TAG_PKCS1_PRIVATE_END    = '-----END RSA PRIVATE KEY-----'
    TAG_PKCS1_PUBLIC_BEGIN   = '-----BEGIN RSA PUBLIC KEY-----'
    TAG_PKCS1_PUBLIC_END     = '-----END RSA PUBLIC KEY-----'
    TAG_PKCS8_PRIVATE_BEGIN  = '-----BEGIN PRIVATE KEY-----'
    TAG_PKCS8_PRIVATE_END    = '-----END PRIVATE KEY-----'
    TAG_PKCS8_PUBLIC_BEGIN   = '-----BEGIN PUBLIC KEY-----'
    TAG_PKCS8_PUBLIC_END     = '-----END PUBLIC KEY-----'
    
    
    KEY_TYPE_EC  = 'ec'
    KEY_TYPE_RSA = 'rsa'
    KEY_TYPE_OCT = 'oct'
    KEY_TYPE = (
        #(KEY_TYPE_EC,  'Elliptic Curve'),
        (KEY_TYPE_RSA, 'RSA'),
        #(KEY_TYPE_OCT, 'Octet Sequence'),
    )
    
    USE_TYPE_SIG = 'sig'
    USE_TYPE_ENC = 'enc'
    USE_TYPE = (
        (USE_TYPE_SIG, 'Signature'),
        (USE_TYPE_ENC, 'Encryption'),
    )
    
    ALG_SIG_DEFAULT = 'RS256'
    ALG_SIG = [
        #('Name', 'Description')
        ('HS256', 'HMAC using SHA-256'),
        ('HS384', 'HMAC using SHA-384'),
        ('HS512', 'HMAC using SHA-512'),
        ('RS256', 'RSASSA-PKCS1-v1_5 using SHA-256'),
        ('RS384', 'RSASSA-PKCS1-v1_5 using SHA-384'),
        ('RS512', 'RSASSA-PKCS1-v1_5 using SHA-512'),
        ('ES256', 'ECDSA using P-256 and SHA-256'),
        ('ES384', 'ECDSA using P-384 and SHA-384'),
        ('ES512', 'ECDSA using P-512 and SHA-512'),
        ('PS256', 'RSASSA-PSS using SHA-256 and MGF1 with SHA-256'),
        ('PS384', 'RSASSA-PSS using SHA-384 and MGF1 with SHA-384'),
        ('PS512', 'RSASSA-PSS using SHA-512 and MGF1 with SHA-512'),
        #('NONE',  'No digital signature or MAC performed', None),
    ]
    
    ALG_ENC_DEFAULT = 'A128CBC-HS256'
    ALG_ENC = [
        #('Name', 'Description')
        ('A128CBC-HS256', 'AES CBC using 128-bit key and HMAC with SHA-256'),
        ('A192CBC-HS384', 'AES CBC using 192-bit key and HMAC with SHA-384'),
        ('A256CBC-HS512', 'AES CBC using 256-bit key and HMAC with SHA-512'),
        #('A128GCM', 'AES GCM using 128-bit key'),
        #('A192GCM', 'AES GCM using 192-bit key'),
        #('A256GCM', 'AES GCM using 256-bit key'),
        #('NONE', 'No encryption performed'),
    ]
    
    key_name = models.CharField('Key Name', max_length=256, null=True, blank=True)
    key_kty = models.CharField('Key Type',
                                  max_length=3,
                                  choices=KEY_TYPE,
                                  default=KEY_TYPE_RSA,
                                  editable=True)
    key_alg_sig = models.CharField('Signature Algorithm',
                                  max_length=20,
                                  choices=ALG_SIG,
                                  default=ALG_SIG_DEFAULT)
    key_alg_enc = models.CharField('Encryption Algorithm',
                                  max_length=20,
                                  choices=ALG_ENC,
                                  default=ALG_ENC_DEFAULT)
    key_created = models.DateTimeField(auto_now_add=True, editable=False)
    key_updated = models.DateTimeField(auto_now=True, editable=False)
    key_valid_from = models.DateTimeField('Valid From')
    key_valid_to = models.DateTimeField('Valid To')
    key_pem = models.TextField('Key PEM')
    _key_instance = None
    
    def __init__(self, *args, **kwargs):
        super(JSONWebKey, self).__init__(*args, **kwargs)
    
    @property
    def key_kid(self):
        return hashlib.sha256(str(self.id)).hexdigest()

    def get_name(self):
        if self.key_name:
           return self.key_name
        else:
           return self.key_kid
		
    def __unicode__(self):
		return 	self.get_name()
        
    def not_valid_before(self):
        return (timezone.now() < self.key_valid_from)
        
    def not_valid_after(self):
        return (timezone.now() > self.key_valid_to)        
		
    def not_expired(self):
        return not self.not_valid_before() and not self.not_valid_after()
    not_expired.short_description = 'Key Valid'
    not_expired.admin_order_field = 'key_expired'
    not_expired.boolean = True
    
    def is_public_key(self):
        pkcs1 = self.TAG_PKCS1_PUBLIC_BEGIN in self.key_pem.encode('utf-8')
        pkcs8 = self.TAG_PKCS8_PUBLIC_BEGIN in self.key_pem.encode('utf-8')
        return pkcs1 or pkcs8

    def is_private_key(self):
        pkcs1 = self.TAG_PKCS1_PRIVATE_BEGIN in self.key_pem.encode('utf-8')
        pkcs8 = self.TAG_PKCS8_PRIVATE_BEGIN in self.key_pem.encode('utf-8')
        return pkcs1 or pkcs8

    def format_json_public_key(self, use = USE_TYPE_ENC):
        key = self._deserialize_key()
        if isinstance(key, rsa.RSAPrivateKey):
            key = key.public_key()
        kj = {}
        kj[u'kty'] = self.key_kty
        kj[u'use'] = use
        if use == self.USE_TYPE_SIG:
            kj[u'alg'] = self.key_alg_sig
        else:
            kj[u'alg'] = self.key_alg_enc
        kj[u'kid'] = self.key_kid
        kj[u'e'] = self._encode_number(key.public_numbers().e)
        kj[u'n'] = self._encode_number(key.public_numbers().n)
        return kj
        
    def format_json_private_key(self, use = USE_TYPE_SIG):
        key = self._deserialize_key()
        if not isinstance(key, rsa.RSAPrivateKey):
            raise KeyTypeException('Not a private key')
        private_numbers = key.private_numbers()
        public_numbers = private_numbers.public_numbers
        kj = {}
        kj[u'kty'] = self.key_kty
        kj[u'use'] = use
        if use == self.USE_TYPE_SIG:
            kj[u'alg'] = self.key_alg_sig
        else:
            kj[u'alg'] = self.key_alg_enc
        kj[u'kid'] = self.key_kid
        kj[u'e'] = self._encode_number(public_numbers.e)
        kj[u'n'] = self._encode_number(public_numbers.n)
        kj[u'd'] = self._encode_number(private_numbers.d)
        kj[u'p'] = self._encode_number(private_numbers.p)
        kj[u'q'] = self._encode_number(private_numbers.q)
        kj[u'dp'] = self._encode_number(private_numbers.dmp1)
        kj[u'dq'] = self._encode_number(private_numbers.dmq1)
        kj[u'i'] = self._encode_number(private_numbers.iqmp)
        return kj
        
    def sign_jwt(self, data):
        key = self._deserialize_key()
        if isinstance(key, rsa.RSAPrivateKey):
            return jwt.encode(data, self.key_pem, algorithm = self.key_alg_sig)            
        else:
            raise KeyTypeException('Cannot sign with public key')
            
    def validate_jwt(self, data):
        key = self._deserialize_key()
        if isinstance(key, rsa.RSAPublicKey):
            pem = self.key_pem
        elif isinstance(key, rsa.RSAPrivateKey):
            key = key.public_key()
            pem = key.public_bytes(
                encoding = Encoding.PEM,
                format = PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise KeyTypeException('Unsupported Kdy Type')
        return jwt.decode(data, pem)
        
    def _deserialize_key(self):
        if not self._key_instance:
            if self.is_public_key():
                self._key_instance = load_pem_public_key(self.key_pem.encode('utf-8'), default_backend())
            elif self.is_private_key():
                self._key_instance = load_pem_private_key(self.key_pem.encode('utf-8'), None, default_backend())
            else:
                raise KeyTypeException('Unsupported Key Type')
        return self._key_instance
            
    def _encode_number(self, number):
        s = '%x' % number
        if (len(s) & 1):
            s = '0' + s
        return urlsafe_b64encode(s.decode('hex'))
        
    class Meta:
        verbose_name = 'RVI Key'
        verbose_name_plural = 'RVI Keys'


class CANFWKey(models.Model):
    """
    CAN Firewall Key will automatically generate a random symetrical 40 character string that will be used with sha256
    and HMAC to sign our messages. 
    """
    
    def __init__(self, *args, **kwargs):
        super(CANFWKey, self).__init__(*args, **kwargs)


    def get_name(self):
        if self.key_name:
           return self.key_name
        else:
           return self.key_gen
        
    def __unicode__(self):
        return  self.get_name()

    class Meta:
        verbose_name = 'CAN FW Key'
        verbose_name_plural = 'CAN FW Keys'

    key_name = models.CharField('Key Name', max_length=256, null=True, blank=True)
    key_created = models.DateTimeField(auto_now_add=True, editable=False)
    key_updated = models.DateTimeField(auto_now=True, editable=False)
    symm_key = models.TextField('Random Key String', null=True, default=key_gen)
        
class KeyTypeException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
