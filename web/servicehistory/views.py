from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import datetime
import urllib
from bs4 import BeautifulSoup
'''
1
>>> sock = urllib.urlopen("http://diveintopython.org/") 2
>>> htmlSource = sock.read()                            3
>>> sock.close()                                        4
>>> print htmlSource
'''
from servicehistory.models import ServiceInvokedHistory


@login_required
def history(request):
    template = loader.get_template('rvi/history.html')

    retrieval_amount = 10
    last_invoked = ServiceInvokedHistory.objects.all()[:retrieval_amount]
    # .order_by('-hist_timestamp')

    for service in last_invoked:
        sock = urllib.urlopen('http://nominatim.openstreetmap.org/search.php?q='+
                              str(service.hist_latitude)+'%2C+'+
                              str(service.hist_longitude))
        html_source = sock.read()
        sock.close()
        soup = BeautifulSoup(html_source, 'html.parser')
        address = soup.find_all("span", class_="name")
        service.hist_latitude = address

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
        'last_invoked': last_invoked,
    })

    return HttpResponse(template.render(context))