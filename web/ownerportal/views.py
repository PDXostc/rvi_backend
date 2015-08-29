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

    device = Device.objects.filter()
    now = datetime.datetime.now()
    active_certificates = Remote.objects.filter(Q(rem_validto__gte=now)|Q(rem_validto=None)).order_by('-rem_validto')
#   active_certificates.filter(~Q(rem_device=rem_vehicle.list_account()))
#   .filter(~Q(rem_device.dev_owner = rem_vehicle))
    expired_certificates = Remote.objects.filter(Q(rem_validto__lt=now))

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
    })

    return HttpResponse(template.render(context))