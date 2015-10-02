from django.shortcuts import render_to_response, render
from django.utils.timezone import localtime
from pytz import timezone
from django.contrib.auth.decorators import login_required

from servicehistory.models import ServiceInvokedHistory
from vehicles.models import Vehicle

# Globals
retrieval_amount = 12

@login_required
def history(request):
    owner = request.user
    owner_vehicles = Vehicle.objects.filter(account=owner)

    last_invoked = ServiceInvokedHistory.objects.filter(hist_vehicle=owner_vehicles)
    last_invoked = last_invoked.order_by('-hist_timestamp')[:retrieval_amount]

    last_invoked_dict = []
    for record in last_invoked:
        formatted_address = str(record.hist_address).split(', ')
        # remove country
        del formatted_address[-1]
        formatted_address.insert(-2, '\n')
        formatted_address = str(formatted_address).strip('[]').replace('\'', '')
        formatted_address = formatted_address.replace(', \\n, ', '\n')

        record.hist_address = unicode(formatted_address)

        time = localtime(record.hist_timestamp, timezone('US/Pacific'))

        last_invoked_dict.append({
            u'hist_id': record.id,
            u'hist_user': record.hist_user.username,
            u'hist_service' : record.hist_service,
            u'hist_timestamp' : unicode(time.strftime("%m/%d/%Y\n%-I:%M %p %Z")),
            u'hist_address' : record.hist_address,
            u'hist_latitude' : record.hist_latitude,
            u'hist_longitude' : record.hist_longitude
        })

    return render(request, 'rvi/history.html', {
        'title': 'History',
        'user': request.user,
        'last_invoked': last_invoked_dict
    })