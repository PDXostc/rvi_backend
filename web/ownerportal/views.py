from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required


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

    context = RequestContext(request, {
        'title': 'History',
        'user': request.user,
    })

    return HttpResponse(template.render(context))