from django.shortcuts import render_to_response
from django.template import RequestContext

def owner_history(request):
    return render_to_response('rvi/history.html')