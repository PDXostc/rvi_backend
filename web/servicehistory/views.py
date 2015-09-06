from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime
import urllib
from bs4 import BeautifulSoup

from servicehistory.models import ServiceInvokedHistory


@login_required
def history(request):
    template = loader.get_template('rvi/history.html')

    # TODO retrieve history based on vehicle tied to owner
    # Presently returning all history
    retrieval_amount = 8
    last_invoked = ServiceInvokedHistory.objects.all().order_by('-hist_timestamp')[:retrieval_amount]

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
        'last_invoked': last_invoked,
    })

    return HttpResponse(template.render(context))