from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime

from devices.models import Device, Remote
from vehicles.models import Vehicle


@login_required
def history(request):
    template = loader.get_template('rvi/history.html')

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
    })

    return HttpResponse(template.render(context))


@login_required
def keys(request):
    template = loader.get_template('rvi/keys.html')

    owner = request.user
    owner_devices = Device.objects.get(dev_owner=owner.username)

    now = datetime.datetime.now()
    non_owner_certificates = Remote.objects.filter(~Q(rem_device=owner_devices))
    active_certificates = non_owner_certificates.filter(
        Q(rem_validto__gte=now)|
        Q(rem_validto=None)
    ).order_by('-rem_validto')

# TODO filter keys tied to the selected vehicle and only show "friend" accounts of the owner
# Presently, showing all keys
#   active_certificates.filter(~Q(rem_device=rem_vehicle.list_account()))
#   .filter(~Q(rem_device.dev_owner = rem_vehicle))
    expired_certificates = non_owner_certificates.filter(
        Q(rem_validto__lt=now)
    ).order_by('-rem_validto')

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
    })

    return HttpResponse(template.render(context))