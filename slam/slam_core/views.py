from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@login_required
def index(request):
    return render(request, 'core/index.html', dict())


def login(request):
    redirect_page = request.GET.get('next')
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST.get('username'),
                                 password=request.POST.get('password'))
        if user is not None:
            auth.login(request, user)
            return JsonResponse({'next': redirect_page})
    return render(request, "core/login.html", dict())


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({})


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
