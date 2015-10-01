# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext


def login_user(request):
    state = ""
    username = password = ''

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active or request.user.is_authenticated():
                login(request, user)
                return redirect('owner_history')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render_to_response('rvi/login.html', {
        'state': state,
        'username': username,
        'user': request.user}, context_instance=RequestContext(request))

def logout_user(request):
    state = "Successfully logged out!"
    username = password = ''

    logout(request)

    return render_to_response('rvi/login.html', {
        'state': state,
        'username': username,
        'user': request.user}, context_instance=RequestContext(request))