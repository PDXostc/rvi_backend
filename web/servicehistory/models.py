import datetime, pytz, uuid, jwt
from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from common.models import Account
from vehicles.models import Vehicle
from security.models import JSONWebKey


class ServiceInvokedHistory(models.Model):
    """
    Data model for a mobile device which can be a smartphone,
    tablet, wearable, etc.
    """

    hist_user = models.ForeignKey(User, verbose_name='User')
    hist_service = models.CharField('Service Name', max_length=256)
    hist_latitude = models.FloatField('Latitude [deg]')
    hist_longitude = models.FloatField('Longitude [deg]')
    hist_address = models.CharField('Address', max_length=256, default='Not Available')
    hist_vehicle = models.ForeignKey(Vehicle, verbose_name='Vehicle')
    hist_timestamp = models.DateTimeField('Timestamp', max_length=100)

    def __unicode__(self):
        """
        Returns the Location string.
        """
        return unicode(self.to_string())

    def to_string(self):
        """
        Returns the Location string composed of
        <vehicle> on <time> at <longitude, latitude>.
        """
        return (unicode(self.hist_user.username) +
             " invoked " +
             unicode(self.hist_service) +
             " on " +
             unicode(self.hist_timestamp) +
             " at (" +
             str(self.hist_latitude) + ", " + str(self.hist_longitude) +
             ")"
            )