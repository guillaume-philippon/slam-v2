"""
This module provide HTTP view for SLAM. slam_core just provide basic view like home, login, logout.
each django's App (slam_*) provide it's own view
"""
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie


@login_required
def index(request):
    """
    This is the home page of SLAM.
    """
    return render(request, 'core/index.html', dict())


def login(request):
    """
    This is the sign in form
    """
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
    """
    This page is only a empty page to force CSRF token to be send to browser. In case of REST API,
    CSRF can be painful to retrieve as it is not sent on every pages. This page force Django to
    resend a new CSRF Token.

    As django view are generic function with "request" as parameter and we don't use it, we must
    tell to pylint to *not* check W0613 (unused-argument) from this function.

    :param request: full HTTP request from user
    """
    # pylint: disable=W0613
    return JsonResponse({})


@login_required
def logout(request):
    """
    This is the logout page.
    """
    auth.logout(request)
    return HttpResponseRedirect('/')
