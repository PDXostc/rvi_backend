from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

@login_required
def owner_history(request):
    return render_to_response('rvi/history.html', {
        'user': request.user}, context_instance=RequestContext(request))