from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required

from servicehistory.models import ServiceInvokedHistory
from vehicles.models import Vehicle


@login_required
def history(request):
    template = loader.get_template('rvi/history.html')

    retrieval_amount = 12
    owner = request.user
    owner_vehicles = Vehicle.objects.filter(account=owner)
    last_invoked = ServiceInvokedHistory.objects.filter(hist_vehicle=owner_vehicles)
    last_invoked = last_invoked.order_by('-hist_timestamp')[:retrieval_amount]

    for record in last_invoked:
        formatted_address = str(record.hist_address).split(', ')
        del formatted_address[-1]
        del formatted_address[-3]
        formatted_address.insert(-3, 'newline')
        formatted_address = str(formatted_address).strip('[]').replace('\'','').replace('California','CA')
        formatted_address = formatted_address.replace(' newline,', '\n')
        # formatted_address = formatted_address.split(' newline,')
        record.hist_address = formatted_address

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
        'last_invoked': last_invoked,
    })

    return HttpResponse(template.render(context))
