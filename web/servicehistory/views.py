from django.http import HttpResponse
from django.template import RequestContext, loader
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from servicehistory.models import ServiceInvokedHistory
from vehicles.models import Vehicle

# Globals
retrieval_amount = 12

@login_required
def history(request):

    last_invoked_dict = []
    owner = request.user
    owner_vehicles = Vehicle.objects.filter(account=owner)

    last_invoked = ServiceInvokedHistory.objects.filter(hist_vehicle=owner_vehicles)
    last_invoked = last_invoked.order_by('-hist_timestamp')[:retrieval_amount]

    for record in last_invoked:
        formatted_address = str(record.hist_address).split(', ')
        del formatted_address[-1]
        del formatted_address[-3]
        formatted_address.insert(-3, 'linebreakplaceholder')
        formatted_address = str(formatted_address).strip('[]').replace('\'','').replace('California','CA')
        formatted_address = formatted_address.replace(' linebreakplaceholder,', '\n')
        record.hist_address = unicode(formatted_address)
        last_invoked_dict.append({
            u'hist_id': record.id,
            u'hist_user': record.hist_user.username,
            u'hist_service' : record.hist_service,
            u'hist_timestamp' : unicode(record.hist_timestamp.strftime("%m/%d/%Y %I:%M %p")),
            u'hist_address' : record.hist_address,
            u'hist_latitude' : record.hist_latitude,
            u'hist_longitude' : record.hist_longitude
        })

    '''
    template = loader.get_template('rvi/history.html')
    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
        'last_invoked': last_invoked_dict,
    })
    '''
    return render_to_response('rvi/history.html', {
        'title': 'History',
        'user': request.user,
        'last_invoked': last_invoked_dict
    })
    #return HttpResponse(template.render(context))
